import math
import random

import numpy as np
import pytest
from qiskit import QuantumCircuit

from eoqrid import EoqEngine, ExchangeInteraction, PhysicalQuantumCircuit
from eoqrid.util import random_arch, random_quantum_circuit


@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 2, 100, 3, 12),
    (3, 3, 100, 3, 12),
])
def test_random_logical_fid1(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        qc = random_quantum_circuit(num_qubits, depth)
        eoq = EoqEngine(arch)
        qc_phys = eoq.transpile(qc, optimization_level=optimization_level)
        qs_phys_A = eoq.execute(qc_phys).qstate

        q = random.randint(0, num_qubits - 1)
        a, b = random.sample(range(num_qubits), 2)
        phase = random.uniform(0.0, 2.0 * np.pi)

        # Identity operation
        qc.cx(a, b)
        qc.rx(phase, q)
        qc.rx(-phase, q)
        qc.cx(a, b)
        qc_phys = eoq.transpile(qc, optimization_level=optimization_level)
        qs_phys_B = eoq.execute(qc_phys).qstate

        fid = qs_phys_A.fidelity(qs_phys_B, mode="logical")
        assert math.isclose(fid, 1.0, abs_tol=1e-8)
        
        fid = qs_phys_A.fidelity(qs_phys_B, mode="physical")
        assert math.isclose(fid, 1.0, abs_tol=1e-8)

@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 2, 100, 3, 123),
    (3, 3, 100, 3, 123),
])
def test_random_logical_fid0(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3

    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        eoq = EoqEngine(arch)

        qc_x = QuantumCircuit(num_qubits)
        qc_x.x(qc_x.qubits)
        qc_random = random_quantum_circuit(num_qubits, depth)

        qc_phys_A = eoq.transpile(qc_random, optimization_level=optimization_level)
        qc_phys_B = eoq.transpile(qc_x.compose(qc_random), optimization_level=optimization_level)

        qs_phys_A = eoq.execute(qc_phys_A).qstate
        qs_phys_B = eoq.execute(qc_phys_B).qstate

        fid = qs_phys_A.fidelity(qs_phys_B, mode="logical")
        assert math.isclose(fid, 0.0, abs_tol=1e-8)
        
        fid = qs_phys_A.fidelity(qs_phys_B, mode="physical")
        assert math.isclose(fid, 0.0, abs_tol=1e-8)

@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 1, 100, 3, 1234),
    (3, 2, 100, 3, 1234),
    (3, 3, 100, 3, 1234),
])
def test_random_partial_mixed_fid1(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        indices = list(range(num_dots))
        random.shuffle(indices)
        k = random.randint(1, num_dots - 2)
        indices_B = indices[k:]
        
        qc = random_quantum_circuit(num_qubits, depth)
        eoq = EoqEngine(num_dots)
        qc_phys = eoq.transpile(qc, optimization_level=optimization_level)
        qs_phys_former = eoq.execute(qc_phys).qstate.partial_trace(indices_B)

        for _ in range(5):
            a, b = random.sample(indices_B, 2)
            phase = random.uniform(0.0, 2.0 * np.pi)
            qc_phys.append(ExchangeInteraction(phase), [a, b])
            
        qs_phys_latter = eoq.execute(qc_phys).qstate.partial_trace(indices_B)

        fid = qs_phys_former.fidelity(qs_phys_latter, mode="physical")
        assert math.isclose(fid, 1.0, abs_tol=1e-6)

@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 2, 100, 3, 1234),
    (3, 3, 100, 3, 1234),
    (3, 4, 100, 3, 1234),
])
def test_random_partial_pure_fid1(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        indices = list(range(num_dots))
        random.shuffle(indices)
        i = random.randint(1, num_qubits - 1)
        indices_A = indices[:i*3]
        indices_B = indices[i*3:]
        
        eoq = EoqEngine(num_dots)
        qc_phys = PhysicalQuantumCircuit(num_dots, index_layout=indices)
        qc_phys.initialize()
        for _ in range(5):
            a, b = random.sample(indices_A, 2)
            phase = random.uniform(0.0, 2.0 * np.pi)
            qc_phys.append(ExchangeInteraction(phase), [a, b])

        qs_phys_former = eoq.execute(qc_phys).qstate.partial_trace(indices_B)

        for _ in range(5):
            a, b = random.sample(indices_B, 2)
            phase = random.uniform(0.0, 2.0 * np.pi)
            qc_phys.append(ExchangeInteraction(phase), [a, b])

        qs_phys_latter = eoq.execute(qc_phys).qstate.partial_trace(indices_B)

        fid = qs_phys_former.fidelity(qs_phys_latter, mode="physical")
        assert qs_phys_former.is_pure()
        assert qs_phys_latter.is_pure()
        assert math.isclose(fid, 1.0, abs_tol=1e-6)
