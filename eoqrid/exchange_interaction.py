from __future__ import annotations
from qiskit.circuit import Gate, QuantumCircuit

class ExchangeInteraction(Gate):
    """
    Exchange Interaction

    """
    def __init__(self, t: float, J: float = 1.0, label: str = None):
        super().__init__(name="ex", num_qubits=2, params=[t, J], label=label)

    def _define(self):
        duration = self.params[0]
        exchange_integral = self.params[1]
        qc = QuantumCircuit(2, name=self.name)
        phase = 0.5 * exchange_integral * duration
        qc.rxx(phase, 0, 1)
        qc.ryy(phase, 0, 1)
        qc.rzz(phase, 0, 1)
        self.definition = qc
