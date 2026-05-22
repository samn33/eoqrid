import math
import random

from eoqrid import EoqSimulator
from eoqrid.util import random_connected_graph, random_quantum_circuit


def eval_fidelity(trial, num_qubits, depth, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        topo = random_connected_graph(num_dots, num_dots)
        qc = random_quantum_circuit(num_qubits, depth)
        sim = EoqSimulator(topo)
        qc_t = sim.transpile(qc)
        fid = sim.fidelity(qc, qc_t)

        assert math.isclose(fid, 1.0, abs_tol=1e-8)

def test_random_circuit():

    eval_fidelity(trial=3, num_qubits=2, depth=100, seed=1234)
    eval_fidelity(trial=3, num_qubits=3, depth=100, seed=1234)
    eval_fidelity(trial=3, num_qubits=4, depth=100, seed=1234)
