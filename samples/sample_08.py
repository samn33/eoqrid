import matplotlib.pyplot as plt
import networkx as nx
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator
from eoqrid.util import plot_graph

def main():

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0,1], [0,1])

    print("== quantum circuit ==")
    print(qc)

    topo = nx.Graph()
    topo.add_edge(0, 2)
    topo.add_edge(1, 2)
    topo.add_edge(2, 3)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)
    plot_graph(topo)
    
    sim = EoqSimulator(topo)
    qc_native = sim.transpile(qc, optimization_level=0)
    qc_native.draw('mpl')
    plt.show()

    print("== transpiled quantum circuit ==")
    print(qc_native)
    print(f"depth = {qc_native.depth()}")

    res = sim.execute(qc_native, shots=10)
    print(res)
    
if __name__ == "__main__":
    main()
