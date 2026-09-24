from qiskit import QuantumCircuit

from eoqrid import EoqEngine
from eoqrid.util import plot_qc


def main():

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)

    print("== quantum circuit ==")
    print(qc)
    
    eoq = EoqEngine(3)
    qc_phys = eoq.transpile(qc)

    print("== transpiled quantum circuit ==")
    print(qc_phys)
    plot_qc(qc_phys)

if __name__ == "__main__":
    main()
