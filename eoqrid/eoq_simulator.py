from __future__ import annotations
import itertools
from collections import defaultdict
import numpy as np
import networkx as nx
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from eoqrid.quantum_state import QuantumState
from eoqrid.transpiler import Transpiler
from eoqrid.result import Result

DEF_EXCHANGE_INTEGRAL = 1.0

class EoqSimulator:
    """
    Exchange-Only Quantum Computing Simulator
    
    Attributes
    ----------
    topology : nx.Graph
        quantum chip topology

    """
    def __init__(self, topology: nx.Graph = None) -> None:
        """
        Parameters
        ----------
        topology : nx.Graph
            quantum chip topology

        Returns
        -------
        None
        
        """
        self._topology = topology

    @property
    def topology(self) -> nx.Graph:
        return self._topology

    @topology.setter
    def topology(self, value) -> None:
        self._topology = value

    def _qc_is_noops(self, qc: QuantumCircuit) -> bool:
        """
        quantum circuit contains no gates operation or not.

        Parameters
        ----------
        qc : QuantumCircuit
            quantum circuit
        
        Returns
        -------
        bool
            true if quantum circuit contains no gates operation, false otherwise

        """
        return qc.count_ops() == {}
        
    def _qc_is_transpiled(self, qc: QuantumCircuit) -> bool:
        """
        quantum circuit is already transpiled or not.

        Parameters
        ----------
        qc : QuantumCircuit
            quantum circuit
        
        Returns
        -------
        bool
            true if quantum circuit is transpiled, false otherwise

        """
        if qc.num_qubits % 3 != 0:
            return False
        for k,v in qc.count_ops().items():
            if k != 'ex' and k != 'm':
                return False
        return True
        
    def optimize(self, qc_native: QuantumCircuit, optimization_level: int = 0, seed: int | None = None) -> QuantumCircuit:
        """
        optimize the native quantum circuit.
        
        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        optimization_level : int
            optimization level.
        seed : int | None, default None
            seed of random generation.
        
        Returns
        -------
        QuantumCircuit
            optimized quantum circuit.

        """
        if not isinstance(qc_native, QuantumCircuit):
            raise TypeError("the qc must be a QuantumCircuit object.")
        for name in qc_native.count_ops():
            if name != 'ex':
                raise ValueError("the qc_native contains gates other than exchange interaction.")

        num_dots = qc_native.num_qubits
        topology = nx.Graph()
        if self._topology is None:
            for pair in itertools.combinations(range(num_dots), 2):
                topology.add_edge(pair[0], pair[1], weight=DEF_EXCHANGE_INTEGRAL)
        else:
            topology = self._topology
        trans = Transpiler(topology)
        return trans.optimize(qc_native, optimization_level, seed)

    def transpile(self, qc: QuantumCircuit, optimization_level: int = 0, seed: int | None = None) -> QuantumCircuit:
        """
        transpile the quantum circuit.
        
        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        optimization_level : int, default 1
            optimization level.
        seed : int | None, default None
            seed of random generation.
        
        Returns
        -------
        qc_t : QuantumCircuit
            transpiled quantum circuit.

        """
        if not isinstance(qc, QuantumCircuit):
            raise TypeError("the qc must be a QuantumCircuit object.")
        if not self._qc_is_noops(qc) and self._qc_is_transpiled(qc):
            raise ValueError("the qc is already transpiled.")

        num_dots = qc.num_qubits * 3
        topology = nx.Graph()
        if self._topology is None:
            for pair in itertools.combinations(range(num_dots), 2):
                topology.add_edge(pair[0], pair[1], weight=DEF_EXCHANGE_INTEGRAL)
        else:
            topology = self._topology
        trans = Transpiler(topology)
        qc_t = trans.run(qc, optimization_level, seed)

        return qc_t

    def _execute_measurement(self, qc_native: QuantumCircuit, shots: int = 1) -> Result:
        """
        execute the native quantum circuit with measurements.
        
        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        shots : int, default 1
            shots of execute the quantumcircuit.
        
        Returns
        -------
        res : Result
            result of execution.

        """
        if not isinstance(qc_native, QuantumCircuit):
            raise TypeError("the qc_native must be a QuantumCircuit object.")
        if not self._qc_is_noops(qc_native) and not self._qc_is_transpiled(qc_native):
            raise ValueError("the qc_native must be transpiled.")
        
        num_dots = qc_native.num_qubits
        num_qubits = num_dots // 3
        num_clbits = qc_native.num_clbits
        
        qstate = QuantumState(num_qubits)
        backend = AerSimulator(method='statevector')
        qc_t = QuantumCircuit(num_dots, num_clbits)
        qc_t.set_statevector(qstate.statevector)
        qc_t = qc_t.compose(
            transpile(qc_native, backend=backend, optimization_level=0)
        )
        qc_t.save_statevector()
        
        freq_qiskit = defaultdict(int)
        if shots > 1:
            result = backend.run(qc_t, shots=shots-1).result()
            freq_qiskit |= result.get_counts()
        
        result = backend.run(qc_t, shots=1).result()
        qstate.statevector = result.get_statevector()
        for k,v in result.get_counts().items():
            m_last = k[::-1]
            freq_qiskit[k] += v

        freq = {k[::-1]:v for k,v in freq_qiskit.items()}

        res = Result(
            num_qubits = num_qubits,
            num_clbits = num_clbits,
            num_dots = num_dots,
            qstate = qstate,
            m_last = m_last,
            freq = freq,
        )
        return res

    def _execute_no_measurement(self, qc_native: QuantumCircuit, shots: int = 1) -> Result:
        """
        execute the native quantum circuit without measurements.
        
        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        shots : int, default 1
            shots of execute the quantumcircuit.
        
        Returns
        -------
        res : Result
            result of execution.

        """
        if not isinstance(qc_native, QuantumCircuit):
            raise TypeError("the qc_native must be a QuantumCircuit object.")
        
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

    def execute(self, qc_native: QuantumCircuit, shots: int = 1) -> Result:
        """
        execute the native quantum circuit.
        
        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        shots : int, default 1
            shots of execute the quantumcircuit.
        
        Returns
        -------
        res : Result
            result of execution.

        """
        if self._qc_is_transpiled(qc_native) is False:
            raise ValueError("qc_native must be a transpiled native quantum circuit.")
        
        if 'm' in qc_native.count_ops():
            res = self._execute_measurement(qc_native, shots)
        else:
            res = self._execute_no_measurement(qc_native, shots)
        return res
        
    def run(self, qc: QuantumCircuit, optimization_level: int = 0, shots: int = 1, seed: int | None = None) -> Result:
        """
        run the quantum circuit (transpile and execute).
        
        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        optimization_level : int, default 1
            optimization level.
        shots : int, default 1
            shots of execute the quantumcircuit.
        seed : int | None, default None
            seed of random generation.
        
        Returns
        -------
        res : Result
            result of execution.

        """
        qc_native = self.transpile(qc, optimization_level = optimization_level, seed = seed)
        res = self.execute(qc_native, shots)
        return res
        
    def fidelity(self, qc: QuantumCircuit, qc_native: QuantumCircuit) -> float:
        """
        fidelity of the quantum circuit execution.
        
        Parameters
        ----------
        qc : QuantumCircuit
            quantum circuits.
        qc_native : QuantumCircuit
            quantum circuits for native device.
        
        Returns
        -------
        fidelity : float
            fidelity

        """
        if 'measure' in qc.count_ops():
            raise ValueError("can't calculate fidelity in quantum circuits that include measurements.")
        
        sv_qiskit = Statevector.from_int(0, 2 ** qc.num_qubits).evolve(qc)
        state_expect = sv_qiskit.reverse_qargs().data
        
        res = self.execute(qc_native)
        
        fidelity = np.abs(np.vdot(state_expect, res.qstate.logical_qstate)) ** 2
        return fidelity
