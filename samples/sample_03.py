import networkx as nx
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator
from eoqrid.util import plot_qc, plot_graph

def main():

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    print("== quantum circuit ==")
    print(qc)

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(2, 3)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)
    plot_graph(topo)
    
    eoq = EoqSimulator(topo)
    qc_native = eoq.transpile(qc)
    plot_qc(qc_native)

    print("== transpiled quantum circuit ==")
    print(qc_native)
    print(f"depth = {qc_native.depth()}")

    res = eoq.execute(qc_native)

    print("== quantum state (logical) ==")
    res.qstate.draw()

    print("== quantum state (physical) ==")
    res.qstate.draw(mode='physical', ignore_zeros=True)
    
if __name__ == "__main__":
    main()
