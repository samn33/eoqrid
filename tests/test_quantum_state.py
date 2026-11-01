import math
import random

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from eoqrid import DotArchitecture, EoqEngine, QuantumState
from eoqrid.util import random_arch, random_quantum_circuit

@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 2, 100, 3, 12),
    (3, 3, 100, 3, 12),
])
def test_random_fidelity_one(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        qc = random_quantum_circuit(num_qubits, depth)
        eoq = EoqEngine(arch)
        qc_t = eoq.transpile(qc, optimization_level=optimization_level)
        qs_A = eoq.execute(qc_t).qstate

        q = random.randint(0, num_qubits - 1)
        a, b = random.sample(range(0, num_qubits), 2)
        phase = random.uniform(0.0, 2.0 * np.pi)

        # Identity operation
        qc.cx(a, b)
        qc.rx(phase, q)
        qc.rx(-phase, q)
        qc.cx(a, b)
        qc_t = eoq.transpile(qc, optimization_level=optimization_level)
        qs_B = eoq.execute(qc_t).qstate

        fid = qs_A.fidelity(qs_B, mode="logical")
        assert math.isclose(fid, 1.0, abs_tol=1e-8)
        
        fid = qs_A.fidelity(qs_B, mode="physical")
        assert math.isclose(fid, 1.0, abs_tol=1e-8)

@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 1, 100, 3, 123),
])
def test_random_fidelity_zero_1(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3

    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        eoq = EoqEngine(arch)

        qc = QuantumCircuit(num_qubits)
        qc.x(0)
        qc.h(0)
        qc_t = eoq.transpile(qc, optimization_level=optimization_level)
        qs_A = eoq.execute(qc_t).qstate

        qc = QuantumCircuit(num_qubits)
        qc.h(0)
        qc_t = eoq.transpile(qc, optimization_level=optimization_level)
        qs_B = eoq.execute(qc_t).qstate
        
        fid = qs_A.fidelity(qs_B, mode="logical")
        assert math.isclose(fid, 0.0, abs_tol=1e-8)
        
        fid = qs_A.fidelity(qs_B, mode="physical")
        assert math.isclose(fid, 0.0, abs_tol=1e-8)

@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 2, 100, 3, 1234),
])
def test_random_fidelity_zero_2(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3

    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        eoq = EoqEngine(arch)

        qc = QuantumCircuit(num_qubits)
        qc.x(0)
        qc.x(1)
        qc.h(0)
        qc.cx(0, 1)
        qc_t = eoq.transpile(qc, optimization_level=optimization_level)
        qs_A = eoq.execute(qc_t).qstate

        qc = QuantumCircuit(num_qubits)
        qc.h(0)
        qc.cx(0, 1)
        qc_t = eoq.transpile(qc, optimization_level=optimization_level)
        qs_B = eoq.execute(qc_t).qstate
        
        fid = qs_A.fidelity(qs_B, mode="logical")
        assert math.isclose(fid, 0.0, abs_tol=1e-8)
        
        fid = qs_A.fidelity(qs_B, mode="physical")
        assert math.isclose(fid, 0.0, abs_tol=1e-8)
