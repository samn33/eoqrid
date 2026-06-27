import random
import numpy as np
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator, ExchangeInteraction

# 2-qubit circuit
qc_native = QuantumCircuit(6)

# 3 random exchange interactions for qubit #0
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3), 2))

# 3 random exchange interactions for qubit #1
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3, 6), 2))
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3, 6), 2))
qc_native.append(ExchangeInteraction(random.uniform(0.0, 2.0 * np.pi), 1.0), random.sample(range(3, 6), 2))

# exchange interaction for qubit #0 and #1 -> leakage
qc_native.append(ExchangeInteraction(np.pi / 4.0), [2, 3])

# draw circuit
print(qc_native)

# evaluate leakage
eoq = EoqSimulator()
leak = eoq.execute(qc_native).qstate.leakage()
print(f"leakage = {leak:.6f}")
