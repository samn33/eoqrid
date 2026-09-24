import random

import numpy as np

from eoqrid import (
    EoqEngine,
    ExchangeInteraction,
    PhysicalQuantumCircuit,
)

# single qubit circuit
qc_phys = PhysicalQuantumCircuit(3)

# 3 random exchange interactions
qc_phys.initialize()
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))

# draw circuit
print(qc_phys)

# evaluate leakage
eoq = EoqEngine(3)
leak = eoq.execute(qc_phys).qstate.leakage()
print(f"leakage = {leak:.6f}")
