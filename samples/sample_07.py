import numpy as np
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator, ExchangeInteraction

def main():

    sim = EoqSimulator()

    theta = np.arccos(1.0 / 3.0)
    qc_native = QuantumCircuit(3)

    print("== initial state ==")
    sim.execute(qc_native).qstate.draw()

    print("== native quantum circuit for Pauli-X ==")
    qc_native.append(ExchangeInteraction(theta - np.pi), [1, 2])
    qc_native.append(ExchangeInteraction(-theta), [0, 1])
    qc_native.append(ExchangeInteraction(theta - np.pi), [1, 2])
    print(qc_native)

    print("== final state ==")
    sim.execute(qc_native).qstate.draw()

    qc = QuantumCircuit(1)
    qc.x(0)

    print("== fidelity ==")
    fid = sim.fidelity(qc, qc_native)
    print(f"fidelity = {fid:.3f}")
    
if __name__ == "__main__":
    main()
