import matplotlib.pyplot as plt

from eoqrid import EoqSimulator
from eoqrid.util import plot_graph, random_quantum_circuit, random_connected_graph

def main():

    num_qubits = 3
    num_dots = num_qubits * 3
    depth = 100
    seed = 1234
    
    qc = random_quantum_circuit(num_qubits, depth, seed)
    qc.draw('mpl')
    plt.show()

    topo = random_connected_graph(num_dots, num_dots, seed)
    plot_graph(topo)

    print("== optimization_level, depth ==")
    sim = EoqSimulator(topo)
    for optimization_level in (0, 1, 2, 3):
        qc_native = sim.transpile(qc, optimization_level=optimization_level, seed=seed)
        print(f"optimization_level = {optimization_level}, depth = {qc_native.depth()}")

if __name__ == "__main__":
    main()
