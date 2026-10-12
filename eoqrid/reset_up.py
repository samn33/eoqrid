from __future__ import annotations

from qiskit.circuit import Instruction, QuantumCircuit


class ResetUp(Instruction):
    """
    Singlet state preparation.

    """
    def __init__(self):
        super().__init__(name="up", num_qubits=1, num_clbits=0, params=[])
        #self.duration = np.pi
        #self.unit = "ns"

    def _define(self):
        qc = QuantumCircuit(self.num_qubits)
        qc.reset(0)
        self.definition = qc
