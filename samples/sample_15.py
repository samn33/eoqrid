import numpy as np
from qiskit import QuantumCircuit

from eoqrid import EoqEngine

num_qubits = 3
num_dots = num_qubits * 3
eoq = EoqEngine(num_dots)
qc = QuantumCircuit(num_qubits)
qc.h(0)
qc.cx(0, 1)
qc.h(2)
qc.rz(np.pi / 3, 2)
print(qc)
qc_phys = eoq.transpile(qc)

print("=== whole quantum state ===")
qs = eoq.execute(qc_phys).qstate
qs.draw()

print("=== trace out ===")
qs_part = qs.partial_trace([6, 7, 8])
print(f"purity = {qs_part.purity()}")
print(f"pure?: {qs_part.is_pure()}")
qs_part.draw()
