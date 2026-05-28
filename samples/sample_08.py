from qiskit import QuantumCircuit

from eoqrid import EoqSimulator
from eoqrid.util import plot_qc

def main():

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)

    print("== quantum circuit ==")
    print(qc)
    
    eoq = EoqSimulator()
    qc_native = eoq.transpile(qc)

    print("== transpiled quantum circuit ==")
    print(qc_native)
    plot_qc(qc_native)

if __name__ == "__main__":
    main()
