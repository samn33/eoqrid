import random
import numpy as np
import matplotlib.pyplot as plt

from eoqrid import (
    EoqEngine,
    ExchangeInteraction,
    PhysicalQuantumCircuit,
    ResetSinglet,
    ResetUp,
)


def main_old():

    #random.seed(1234)

    num_pairs_A = 2
    num_pairs_B = 1
    num_pairs = num_pairs_A + num_pairs_B
    num_dots_A = num_pairs_A * 2
    num_dots_B = num_pairs_B * 2
    num_dots = num_dots_A + num_dots_B
    num_gates = 3
    eoq = EoqEngine(num_dots)
    qc_phys = PhysicalQuantumCircuit(num_dots)

    for i in range(num_pairs_A):
        a, b = i * 2, i * 2 +1
        qc_phys.append(ResetSinglet(), [a, b])

    for i in range(num_pairs_A, num_pairs):
        a, b = i * 2, i * 2 +1
        qc_phys.append(ResetSinglet(), [a, b])

    for _ in range(num_gates):
        theta = random.uniform(0.0, 2.0 * np.pi)
        a, b = random.sample(list(range(num_dots_A)), 2)
        qc_phys.append(ExchangeInteraction(theta), [a, b])

    for _ in range(num_gates):
        theta = random.uniform(0.0, 2.0 * np.pi)
        a, b = random.sample(list(range(num_dots_A, num_dots)), 2)
        qc_phys.append(ExchangeInteraction(theta), [a, b])

    print(qc_phys)

    eoq = EoqEngine(num_dots)

    res = eoq.execute(qc_phys)
    qs = res.qstate
    trace_out = [0,1]
    qs_part = qs.partial_trace(trace_out)

    print(f"index_layout = {qs.index_layout}")
    print(f"trace_out = {trace_out}")
    print(f"num_dots = {qs_part.num_dots}")
    print(f"num_qubits = {qs_part.num_qubits}")
    print(f"index_layout = {qs_part.index_layout}")

    if qs_part.is_pure():
        print("== pure state ==")
    else:
        print("== mixed state ==")

    #print(qs_part.density_matrix)
    qs_part.draw(mode="physical")

    qs_part.density_matrix.draw("hinton")
    plt.show()

def main():

    num_dots = 3
    eoq = EoqEngine(num_dots)
    qc_phys = PhysicalQuantumCircuit(num_dots)
    qc_phys.append(ResetSinglet(), [0, 1])
    qc_phys.append(ResetUp(), [2])
    qc_phys.append(ExchangeInteraction(np.pi / 3), [0, 1])
    qc_phys.append(ExchangeInteraction(np.pi / 5), [1, 2])

    res = eoq.execute(qc_phys)
    qs = res.qstate
    qs.draw()
    qs.draw(mode="physical")

    qs_part = qs.partial_trace([2])

    qs_part.draw(ignore_zeros=True)

    
if __name__ == "__main__":
    main()
