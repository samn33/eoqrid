from eoqrid import EoqEngine
from eoqrid.util import plot_arch, plot_qc, random_arch, random_quantum_circuit


def main():

    num_qubits = 3
    num_dots = num_qubits * 3
    depth = 100
    seed = 12345
    
    qc = random_quantum_circuit(num_qubits, depth, num_measurements=0, seed=seed)
    plot_qc(qc)

    arch = random_arch(num_dots, num_dots, num_readout_pairs=0, seed=seed)
    plot_arch(arch)

    print("== optimization_level, depth ==")
    eoq = EoqEngine(arch)
    for optimization_level in (0, 1, 2, 3):
        qc_phys = eoq.transpile(qc, optimization_level=optimization_level, seed=seed)
        print(f"optimization_level = {optimization_level}, depth = {qc_phys.depth()}")

if __name__ == "__main__":
    main()
