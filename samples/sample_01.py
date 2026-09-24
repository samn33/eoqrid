from qiskit import QuantumCircuit

from eoqrid import EoqEngine


def main():

    qc = QuantumCircuit(1)
    qc.h(0)

    print("== quantum circuit ==")
    print(qc)

    eoq = EoqEngine(3)
    qc_phys = eoq.transpile(qc)

    print("== transpiled quantum circuit ==")
    print(qc_phys)
    print(f"depth = {qc_phys.depth()}")

    res = eoq.execute(qc_phys)

    print("== quantum state (logical) ==")
    res.qstate.draw()

    print("== quantum state (physical) ==")
    res.qstate.draw(mode='physical')
    
if __name__ == "__main__":
    main()
