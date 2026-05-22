from qiskit import QuantumCircuit

from eoqrid import EoqSimulator

def main():

    qc = QuantumCircuit(1)
    qc.h(0)

    print("== quantum circuit ==")
    print(qc)

    sim = EoqSimulator()
    qc_native = sim.transpile(qc)

    print("== transpiled quantum circuit ==")
    print(qc_native)
    print(f"depth = {qc_native.depth()}")

    res = sim.execute(qc_native)

    print("== quantum state (logical) ==")
    res.qstate.draw()

    print("== quantum state (physical) ==")
    res.qstate.draw(mode='physical')
    
if __name__ == "__main__":
    main()
