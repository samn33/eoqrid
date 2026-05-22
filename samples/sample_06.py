import networkx as nx
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator

def main():

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(1, 4)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)

    sim = EoqSimulator(topo)
    qc_native = sim.transpile(qc)
    res = sim.execute(qc_native)

    print("== quantum state (logical) ==")
    res.qstate.draw()

    print("== quantum state (physical) ==")
    res.qstate.draw(mode='physical', ignore_zeros=True)

    print("== fidelity ==")
    fid = sim.fidelity(qc, qc_native)
    print(f"fidelity = {fid:.6f}")
    
if __name__ == "__main__":
    main()
