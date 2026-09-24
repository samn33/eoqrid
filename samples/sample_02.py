from qiskit import QuantumCircuit

from eoqrid import EoqEngine
from eoqrid.util import plot_arch, plot_qc


def main():

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    print("== quantum circuit ==")
    print(qc)

    eoq = EoqEngine(6)
    plot_arch(eoq.arch)
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
