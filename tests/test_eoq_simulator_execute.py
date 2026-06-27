import pytest
import math
import random
import numpy as np
from qiskit.quantum_info import Statevector

from eoqrid import EoqSimulator
from eoqrid.util import random_connected_graph, random_quantum_circuit

@pytest.mark.parametrize("trial, num_qubits, depth, seed", [
    (3, 2, 100, 123),
    (3, 3, 100, 123),
    (3, 4, 100, 123),
])
def test_random_qc(trial, num_qubits, depth, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        topo = random_connected_graph(num_dots, num_dots)
        qc = random_quantum_circuit(num_qubits, depth)
        eoq = EoqSimulator(topo)
        qc_t = eoq.transpile(qc)

        sv_qiskit = Statevector.from_int(0, 2 ** qc.num_qubits).evolve(qc)
        state_expect = sv_qiskit.reverse_qargs().data
        
        res = eoq.execute(qc_t)
        
        fid = np.abs(np.vdot(state_expect, res.qstate.logical_qstate)) ** 2
        assert math.isclose(fid, 1.0, abs_tol=1e-8)

        leak = res.qstate.leakage()
        assert math.isclose(leak, 0.0, abs_tol=1e-8)
