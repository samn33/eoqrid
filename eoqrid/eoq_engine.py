import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from eoqrid.dot_architecture import DotArchitecture
from eoqrid.eoq_simulator import EoqSimulator
from eoqrid.eoq_transpiler import EoqTranspiler
from eoqrid.physical_quantum_circuit import PhysicalQuantumCircuit
from eoqrid.result import Result


class EoqEngine:
    """
    Provide an execution engine for exchange-only quantum computing.

    Attributes
    ----------
    arch : DotArchitecture
        Quantum dot architecture layout.
    num_dots : int
        Number of quantum dots.
    transpiler : EoqTranspiler
        Logical-to-physical quantum circuit transpiler.
    simulator : EoqSimulator
        Quantum circuit simulator.
    """
    def __init__(self, arch: DotArchitecture | int) -> None:
        """
        Initialize the exchange-only quantum computing engine.

        Parameters
        ----------
        arch : DotArchitecture or int
            Quantum dot architecture, or number of dots for a fully connected layout.

        Notes
        -----
        If `arch` is an integer, a complete graph topology is generated with readout enabled on all dots.
        """
        if isinstance(arch, int):
            self._arch = DotArchitecture(arch)
        elif isinstance(arch, DotArchitecture):
            self._arch = arch
        else:
            raise TypeError("arch must be DotArchitecture or integer.")

        if not self._arch.is_valid():
            raise ValueError("arch is invalid.")

        self._transpiler = EoqTranspiler(self.arch)
        self._simulator = EoqSimulator(self.arch)

    @property
    def arch(self) -> DotArchitecture:
        return self._arch

    @property
    def num_dots(self) -> int:
        return self._arch.num_dots

    @arch.setter
    def arch(self, arch) -> None:
        self._arch = arch

    @property
    def transpiler(self):
        return self._transpiler

    @property
    def simulator(self):
        return self._simulator

    def transpile(
            self,
            qc: QuantumCircuit,
            optimization_level: int = 0,
            seed: int | None = None
    ) -> PhysicalQuantumCircuit:
        """
        Transpile a logical quantum circuit.

        Parameters
        ----------
        qc : QuantumCircuit
            Logical quantum circuit.
        optimization_level : int, default 0
            Optimization level (0, 1, 2, or 3).
        seed : int or None, default None
            Random seed for transpilation.

        Returns
        -------
        PhysicalQuantumCircuit
            Transpiled physical circuit.
        """
        return self.transpiler.transpile(qc, optimization_level, seed)

    def run(
            self,
            qc: QuantumCircuit,
            optimization_level: int = 0,
            shots: int = 1,
            seed: int | None = None
    ) -> Result:
        """
        Execute a logical quantum circuit.

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
        return self.simulator.run(qc, optimization_level, shots, seed)

    def execute(self, qc_phys: PhysicalQuantumCircuit, shots: int = 1) -> Result:
        """
        Execute a physical quantum circuit.
        
        Parameters
        ----------
        qc_phys : PhysicalQuantumCircuit
            Physical quantum circuit.
        shots : int
            Number of shots.
    
        Returns
        -------
        Result
            Execution result.
        
        """
        return self.simulator.execute(qc_phys, shots)

    def fidelity(self, qc: QuantumCircuit, qc_phys: PhysicalQuantumCircuit) -> float:
        """
        Calculate the fidelity of a physical quantum circuit execution.

        Parameters
        ----------
        qc : QuantumCircuit
            Logical quantum circuit.
        qc_phys : PhysicalQuantumCircuit
            Physical quantum circuit after transpilation.

        Returns
        -------
        float
            Estimated fidelity between the logical and physical circuits.
        """
        if 'measure' in qc.count_ops():
            raise ValueError("can't calculate fidelity in quantum circuits that include measurements.")
        
        sv_qiskit = Statevector.from_int(0, 2 ** qc.num_qubits).evolve(qc)
        state_expect = sv_qiskit.reverse_qargs().data
        
        res = self.execute(qc_phys)
        
        fidelity = np.abs(np.vdot(state_expect, res.qstate.logical_qstate)) ** 2
        return fidelity
