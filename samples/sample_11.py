import random

import numpy as np

from eoqrid import EoqEngine, ExchangeInteraction, PhysicalQuantumCircuit

# 2-qubit circuit
qc_phys = PhysicalQuantumCircuit(6)
qc_phys.initialize()

# 3 random exchange interactions for qubit #0
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))

# 3 random exchange interactions for qubit #1
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3, 6), 2))
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3, 6), 2))
qc_phys.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3, 6), 2))

# exchange interaction for qubit #0 and #1 -> leakage
qc_phys.append(ExchangeInteraction(np.pi / 4.0), [2, 3])

# draw circuit
print(qc_phys)

# evaluate leakage
eoq = EoqEngine(6)
leak = eoq.execute(qc_phys).qstate.leakage()
print(f"leakage = {leak:.6f}")
