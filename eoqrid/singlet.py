from __future__ import annotations

from qiskit.circuit import Instruction, QuantumCircuit


class Singlet(Instruction):
    """
    Singlet state preparation.

    """
    def __init__(self):
        super().__init__(name="sin", num_qubits=2, num_clbits=0, params=[])

    def _define(self):
        qc = QuantumCircuit(self.num_qubits)
        qc.reset(0)
        qc.reset(1)
        qc.x(0)
        qc.x(1)
        qc.h(0)
        qc.cx(0, 1)
        self.definition = qc
