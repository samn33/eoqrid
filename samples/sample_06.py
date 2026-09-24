from qiskit import QuantumCircuit

from eoqrid import DotArchitecture, EoqEngine


def main():

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(1, 4)
    arch.add_edge(3, 4)
    arch.add_edge(4, 5)

    eoq = EoqEngine(arch)
    qc_phys = eoq.transpile(qc)
    res = eoq.execute(qc_phys)

    print("== quantum state (logical) ==")
    res.qstate.draw()

    print("== quantum state (physical) ==")
    res.qstate.draw(mode='physical', ignore_zeros=True)

    print("== fidelity ==")
    fid = eoq.fidelity(qc, qc_phys)
    print(f"fidelity = {fid:.6f}")
    
if __name__ == "__main__":
    main()
