from qiskit import QuantumCircuit

from eoqrid import DotArchitecture, EoqEngine
from eoqrid.util import plot_arch, plot_qc


def main():

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    print("== quantum circuit ==")
    print(qc)

    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(2, 3)
    arch.add_edge(3, 4)
    arch.add_edge(4, 5)
    plot_arch(arch)
    eoq = EoqEngine(arch)
    qc_phys = eoq.transpile(qc)
    plot_qc(qc_phys)

    print("== transpiled quantum circuit ==")
    print(qc_phys)
    print(f"depth = {qc_phys.depth()}")

    res = eoq.execute(qc_phys)

    print("== quantum state (logical) ==")
    res.qstate.draw()

    print("== quantum state (physical) ==")
    res.qstate.draw(mode='physical', ignore_zeros=True)
    
if __name__ == "__main__":
    main()
