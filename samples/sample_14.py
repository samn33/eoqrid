import numpy as np

from eoqrid import (
    EoqEngine,
    ExchangeInteraction,
    PhysicalQuantumCircuit,
    ResetSinglet,
    ResetUp,
)


def main():

    eoq = EoqEngine(4)

    theta = np.arccos(1.0 / 3.0)
    qc_phys = PhysicalQuantumCircuit(4)

    print("== native quantum circuit for Pauli-X ==")
    qc_phys.append(ResetSinglet(), [0, 1])
    qc_phys.append(ExchangeInteraction(theta), [0, 1])
    qc_phys.append(ExchangeInteraction(theta), [1, 2])
    qc_phys.append(ExchangeInteraction(theta), [2, 3])
    print(qc_phys)

    print("== final state ==")
    qs = eoq.execute(qc_phys).qstate
    qs.index_layout = [1, 0, 2, 3]
    qs.draw(mode = "physical")
    
if __name__ == "__main__":
    main()
