from __future__ import annotations

from collections import defaultdict

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from eoqrid.dot_architecture import DotArchitecture
from eoqrid.eoq_transpiler import EoqTranspiler
from eoqrid.physical_quantum_circuit import PhysicalQuantumCircuit
from eoqrid.quantum_state import QuantumState
from eoqrid.result import Result


class EoqSimulator:
    """
    Simulator for exchange-only quantum computing.
    
    Attributes
    ----------
    arch : DotArchitecture
        Quantum dot architecture layout.
    """
    def __init__(self, arch: DotArchitecture) -> None:
        """
        Initialize the exchange-only quantum computing simulator.

        Parameters
        ----------
        arch : DotArchitecture
            Quantum dot architecture layout.
        """
        self._arch = arch

    @property
    def arch(self) -> DotArchitecture:
        return self._arch

    @property
    def num_dots(self) -> int:
        return self._arch.num_dots

    @property
    def num_qubits(self) -> int:
        return self._arch.num_qubits
        
    def _execute_measurement(
            self,
            qc_phys: PhysicalQuantumCircuit,
            shots: int = 1,
    ) -> Result:
        """
        Execute a physical quantum circuit with measurements.

        Parameters
        ----------
        qc_phys : PhysicalQuantumCircuit
            Physical quantum circuit.
        shots : int, default 1
            Number of shots.

        Returns
        -------
        Result
            Execution result including measurement outcomes.
        """
        qc_native = qc_phys.to_qiskit()
        if qc_native.num_qubits != self.num_dots:
            raise ValueError("number of qubits of qc_native must be same as num_dots.")

        if len(self._arch.readout_pairs) == 0:
            raise ValueError("readout pair does not exist.")

        num_dots = qc_native.num_qubits
        num_qubits = num_dots // 3
        num_clbits = qc_native.num_clbits
        
        qstate = QuantumState(num_qubits)
        backend = AerSimulator(method='statevector')
        qc_t = QuantumCircuit(num_dots, num_clbits)
        qc_t.set_statevector(qstate.statevector)
        qc_t = qc_t.compose(
            transpile(qc_native.decompose(), backend=backend, optimization_level=0)
        )
        
        freq_qiskit = defaultdict(int)
        if shots > 1:
            result = backend.run(qc_t, shots=shots-1).result()
            freq_qiskit |= result.get_counts()
        
        result = backend.run(qc_t, shots=1).result()
        for k,v in result.get_counts().items():
            m_last = k[::-1]
            freq_qiskit[k] += v

        freq = {k[::-1]:v for k,v in freq_qiskit.items()}

        res = Result(
            num_qubits = num_qubits,
            num_clbits = num_clbits,
            num_dots = num_dots,
            qstate = None,
            m_last = m_last,
            freq = freq,
        )
        return res

    def _execute_no_measurement(
            self,
            qc_phys: PhysicalQuantumCircuit,
            shots: int = 1
    ) -> Result:
        """
        Execute a physical quantum circuit without measurements.
        
        Parameters
        ----------
        qc_phys : QuantumCircuit
            Physical uantum circuit.
        shots : int, default 1
            Number of shots.
        
        Returns
        -------
        Result
             Execution result.
        """
        qc_native = qc_phys.to_qiskit()
        
        num_dots = qc_native.num_qubits
        num_qubits = num_dots // 3
        num_clbits = qc_native.num_clbits

        qstate = QuantumState(num_qubits)

        qstate.statevector = qstate.statevector.evolve(qc_native)

        if qc_native.layout is None:
            logical_indices = list(range(num_dots))
        else:
            logical_indices = qc_native.layout.final_index_layout()

        data = np.zeros(2 ** num_dots, dtype=complex)
        for p_id in range(2 ** num_dots):
            b_str = f"{p_id:0{num_dots}b}"
            b_list = list(map(int, list(b_str)))[::-1]
            bb_list = [0] * num_dots
            l_id = 0
            for k in range(num_dots):
                bb_list[logical_indices[k]] = b_list[k]
                if b_list[k] == 1:
                    l_id += (1 << logical_indices[k])
            data[p_id] = qstate.statevector.data[l_id]
    
        qstate.statevector = Statevector(data)

        res = Result(
            num_qubits = num_qubits,
            num_clbits = num_clbits,
            num_dots = num_dots,
            qstate = qstate,
            m_last = None,
            freq = None,
        )
        return res

    def execute(self, qc_phys: PhysicalQuantumCircuit, shots: int = 1) -> Result:
        """
        Execute a physical quantum circuit.
        
        Parameters
        ----------
        qc_phys : PhysicalQuantumCircuit
            Physical quantum circuits.
        shots : int, default 1
            Number of shots.
        
        Returns
        -------
        Result
            Execution result.
        """
        if not isinstance(qc_phys, PhysicalQuantumCircuit):
            raise TypeError("qc_phys must be PhysicalQuantumCircuiit.")
        if not qc_phys.is_valid():
            raise ValueError("qc_native must be native.")

        qc_native = qc_phys.to_qiskit()
        
        # check the graph connectivity
        for i, inst in enumerate(qc_native):
            operation = inst.operation
            qubits = inst.qubits
            qid = [q._index for q in qubits]
            match operation.name:
                case 'ex' | 'm' | 'sin':
                    if not self._arch.topology.has_edge(qid[0], qid[1]):
                        raise ValueError("two quantum dot indices are specified that cannot be acted upon.")
                case 'reset':
                    pass
                case _:
                    raise ValueError(f"{operation.name} can't be executed because it operate to 2 dots not connected.")
        
        if 'm' in qc_native.count_ops():
            res = self._execute_measurement(qc_phys, shots)
        else:
            res = self._execute_no_measurement(qc_phys, shots)
        return res
        
    def run(
            self,
            qc: QuantumCircuit,
            optimization_level: int = 0,
            shots: int = 1,
            seed: int | None = None
    ) -> Result:
        """
        Transpile and execute a logical quantum circuit.

        Parameters
        ----------
        qc : QuantumCircuit
            Logical quantum circuit.
        optimization_level : int, default 0
            Optimization level (0, 1, 2, or 3).
        shots : int, default 1
            Number of shots.
        seed : int or None, default None
            Random seed.

        Returns
        -------
        Result
            Execution result.
        """
        trans = EoqTranspiler(self._arch)
        qc_native = trans.transpile(qc, optimization_level = optimization_level, seed = seed)
        res = self.execute(qc_native, shots)
        return res
