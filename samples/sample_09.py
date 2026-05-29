import networkx as nx
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator

def main():

    topo = nx.Graph()
    topo.add_edge(0, 2)
    topo.add_edge(1, 2)
    topo.add_edge(1, 4)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0,1], [0,1])

    print("== quantum circuit ==")
    print(qc)

    eoq = EoqSimulator(topo)

    print("== frequency ==")
    res = eoq.run(qc, shots=10)
    print(res)
    
if __name__ == "__main__":
    main()
