from __future__ import annotations
from qiskit.circuit import Instruction, QuantumCircuit

class Measurement(Instruction):
    """
    Measurement

    """
    def __init__(self):
        super().__init__(name="m", num_qubits=2, num_clbits=1, params=[])

    def _define(self):
        qc = QuantumCircuit(self.num_qubits, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.x(0)
        qc.x(1)
        qc.measure(0, 0)
        with qc.if_test((0, 0)):
            qc.measure(1, 0)

        self.definition = qc
