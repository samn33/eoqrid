import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator, ExchangeInteraction

a , b = 0, 1
(a6, a5, a4) = (a * 3, a * 3 + 1, a * 3 + 2)
(a1, a2, a3) = (b * 3, b * 3 + 1, b * 3 + 2)
phase_1 = np.arccos(1.0 / np.sqrt(3.0))
phase_2 = np.arccos(2.0 * np.sqrt(2.0) / 3.0)
phase_3 = np.arccos(-2.0 * np.sqrt(2.0) / 3.0)
phase_4 = np.arccos(1.0 / np.sqrt(3.0))

# args of ExchangeInteraction for CNOT
args_list = []
args_list.append((ExchangeInteraction(2.0 * np.pi - phase_1, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a5, a4]))
args_list.append((ExchangeInteraction(phase_2, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a6, a5]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a4, a3]))
args_list.append((ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a4, a3]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a5, a4]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a4, a3]))
args_list.append((ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a5, a4]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a4, a3]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a5, a4]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(np.pi / 2.0, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a4, a3]))
args_list.append((ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a4, a3]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a2, a1]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a6, a5]))
args_list.append((ExchangeInteraction(phase_3, 1.0), [a3, a2]))
args_list.append((ExchangeInteraction(np.pi, 1.0), [a5, a4]))
args_list.append((ExchangeInteraction(phase_4, 1.0), [a2, a1]))

# get leakage sequence
eoq = EoqSimulator()
qc_native = QuantumCircuit(6)
y = []
for args in args_list:
    qc_native.append(*args)
    leakage = eoq.execute(qc_native).qstate.leakage()
    y.append(leakage)
x = list(range(len(y)))

# plot leakage sequence
plt.plot(x, y, marker='o', color='red')
plt.title("Leakage per Step")
plt.xlabel("Step")
plt.ylabel("Leakage")
plt.grid(True)
plt.show()
