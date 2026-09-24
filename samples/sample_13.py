from qiskit import QuantumCircuit

from eoqrid import DotArchitecture, EoqEngine
from eoqrid.util import plot_qc


def main():

    #arch = DotArchitecture(6)

    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(2, 3)
    arch.add_edge(3, 4)
    arch.add_edge(4, 5)
    arch.add_readout_pair(2, 3)
    arch.add_readout_pair(4, 5)

    #print(arch)
    #plot_arch(arch)

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)

    print("== quantum circuit ==")
    print(qc)

    eoq = EoqEngine(arch)
    qc_phys = eoq.transpile(qc)
    print(qc_phys)

    plot_qc(qc_phys)

    res = eoq.execute(qc_phys, shots=10)
    print(res)
    
if __name__ == "__main__":
    main()
