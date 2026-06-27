import random
import numpy as np
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator, ExchangeInteraction

# single qubit circuit
qc_native = QuantumCircuit(3)

# 3 random exchange interactions
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))

# draw circuit
print(qc_native)

# evaluate leakage
eoq = EoqSimulator()
leak = eoq.execute(qc_native).qstate.leakage()
print(f"leakage = {leak:.6f}")
