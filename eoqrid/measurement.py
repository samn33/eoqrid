from __future__ import annotations
from qiskit.circuit import Instruction, QuantumCircuit

class Measurement(Instruction):
    """
    Measurement (TEST)

    """
    def __init__(self):
        super().__init__(name="m", num_qubits=3, num_clbits=1, params=[])

    def _define(self):
        qc = QuantumCircuit(self.num_qubits, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.cx(0, 2)
        qc.x(0)
        qc.x(1)
        qc.ccx(0, 1, 2)
        qc.x(0)
        qc.x(1)
        qc.x(2)

        qc.measure(2, 0)

        qc.x(0)
        qc.x(1)
        qc.x(2)
        qc.ccx(0, 1, 2)
        qc.x(0)
        qc.x(1)
        qc.cx(0, 2)
        qc.h(0)
        qc.cx(0, 1)
        
        self.definition = qc
