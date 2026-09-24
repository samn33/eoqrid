import math
import random

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from eoqrid import DotArchitecture, EoqEngine
from eoqrid.util import random_arch, random_quantum_circuit


@pytest.mark.parametrize("trial, num_qubits, depth, optimization_level, seed", [
    (3, 1, 100, 3, 123),
    (3, 2, 100, 3, 123),
    (3, 3, 100, 3, 123),
    (3, 4, 100, 3, 123),
])
def test_random_qc_random_arch(trial, num_qubits, depth, optimization_level, seed):

    random.seed(seed)
    num_dots = num_qubits * 3
    
    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        qc = random_quantum_circuit(num_qubits, depth)
        eoq = EoqEngine(arch)

        sv_qiskit = Statevector.from_int(0, 2 ** qc.num_qubits).evolve(qc)
        state_expect = sv_qiskit.reverse_qargs().data
        
        res = eoq.run(qc)

        fid = np.abs(np.vdot(state_expect, res.qstate.logical_qstate)) ** 2
        assert math.isclose(fid, 1.0, abs_tol=1e-8)

        leak = res.qstate.leakage()
        assert math.isclose(leak, 0.0, abs_tol=1e-8)

@pytest.mark.parametrize("trial, num_readout_pairs, optimization_level, seed", [
    (3, 1, 0, 123),
    (3, 1, 1, 123),
    (3, 1, 2, 123),
    (3, 1, 3, 123),
    (3, 2, 0, 123),
    (3, 2, 1, 123),
    (3, 2, 2, 123),
    (3, 2, 3, 123),
    (3, 3, 0, 123),
    (3, 3, 1, 123),
    (3, 3, 2, 123),
    (3, 3, 3, 123),
])
def test_random_arch_with_measurement(trial, num_readout_pairs, optimization_level, seed):

    random.seed(seed)
    shots = 20

    num_qubits = 2
    num_clbits = num_qubits
    num_dots = num_qubits * 3
    for _ in range(trial):
        arch = random_arch(num_dots, num_dots, num_readout_pairs=num_readout_pairs)
        qc_in = QuantumCircuit(num_qubits, num_clbits)
        qc_in.h(0)
        qc_in.cx(0, 1)
        qc_in.measure(0, 0)
        qc_in.measure(1, 1)
        eoq = EoqEngine(arch)
        res = eoq.run(qc_in, shots=shots)

        assert "00" in res.freq
        assert "11" in res.freq
        assert "01" not in res.freq
        assert "10" not in res.freq

    num_qubits = 3
    num_clbits = num_qubits
    num_dots = num_qubits * 3
    for _ in range(trial):
        arch = random_arch(num_dots, num_dots, num_readout_pairs=num_readout_pairs)
        qc_in = QuantumCircuit(num_qubits, num_clbits)
        qc_in.h(0)
        qc_in.cx(0, 1)
        qc_in.cx(0, 2)
        qc_in.measure([0, 1, 2], [0, 1, 2])
        eoq = EoqEngine(arch)
        res = eoq.run(qc_in, shots=shots)

        assert "000" in res.freq
        assert "111" in res.freq
        assert "001" not in res.freq
        assert "010" not in res.freq
        assert "011" not in res.freq
        assert "100" not in res.freq
        assert "101" not in res.freq
        assert "110" not in res.freq

def equal_state_vector(a, b):
    return math.isclose(abs(np.vdot(a, b)), 1.0, abs_tol=1e-8)
    
def test_initial_logical_qstate():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_initial_physical_qstate():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1)
    res = eoq.run(qc)
    expect = np.array([0.0, 0.0, 0.70710678, 0.0, -0.70710678, 0.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.physical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    res = eoq.run(qc)
    expect = np.array([0.0, 0.0,  0. , 0.0,  0. , 0.0, 0.0, 0.0,
                       0.0, 0.0,  0. , 0.0,  0. , 0.0, 0.0, 0.0,
                       0.0, 0.0,  0.5, 0.0, -0.5, 0.0, 0.0, 0.0,
                       0.0, 0.0,  0. , 0.0,  0. , 0.0, 0.0, 0.0,
                       0.0, 0.0, -0.5, 0.0,  0.5, 0.0, 0.0, 0.0,
                       0.0, 0.0,  0. , 0.0,  0. , 0.0, 0.0, 0.0,
                       0.0, 0.0,  0. , 0.0,  0. , 0.0, 0.0, 0.0,
                       0.0, 0.0,  0. , 0.0,  0. , 0.0, 0.0, 0.0])
    actual = res.qstate.physical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_x_gate():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1)
    qc.x(0)
    res = eoq.run(qc)
    expect = np.array([0.0, 1.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    qc.x(1)
    res = eoq.run(qc)
    expect = np.array([0.0, 1.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(0)
    qc.x(1)
    res = eoq.run(qc)
    expect = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_h_gate():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1)
    qc.h(0)
    res = eoq.run(qc)
    expect = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(1)
    qc.x(0)
    qc.h(0)
    res = eoq.run(qc)
    expect = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)
    
    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    qc.h(0)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0, 1.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(1)
    res = eoq.run(qc)
    expect = np.array([1.0, 1.0, 0.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(1)
    res = eoq.run(qc)
    expect = np.array([1.0, 1.0, 1.0, 1.0], dtype=complex) / 2.0
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_z_gate():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1)
    qc.z(0)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.z(0)
    res = eoq.run(qc)
    expect = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.z(0) 
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0, -1.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(1)
    qc.z(1) 
    res = eoq.run(qc)
    expect = np.array([1.0, -1.0, 0.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(1)
    qc.z(0) 
    res = eoq.run(qc)
    expect = np.array([1.0, 1.0, -1.0, -1.0], dtype=complex) / 2.0
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
def test_rz_gate():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1)
    qc.rz(np.pi/4.0, 0)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.rz(np.pi/4.0, 0)
    res = eoq.run(qc)
    actual = res.qstate.logical_qstate
    expect = np.array([1.0/np.sqrt(2.0), 0.5+0.5j], dtype=complex)
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.rz(np.pi/4.0, 0)
    res = eoq.run(qc)
    expect = np.array([1.0/np.sqrt(2.0), 0.0, 0.5+0.5j, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(1)
    qc.rz(np.pi/4.0, 1)
    res = eoq.run(qc)
    expect = np.array([1.0/np.sqrt(2.0), 0.5+0.5j, 0.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(1)
    qc.rz(np.pi/4.0, 0)
    res = eoq.run(qc)
    expect = np.array([0.5, 0.5, 1.0/np.sqrt(8.0)+1.0j/np.sqrt(8.0), 1.0/np.sqrt(8.0)+1.0j/np.sqrt(8.0)], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
def test_cx_gate():

    eoq = EoqEngine(DotArchitecture(6))

    qc = QuantumCircuit(2)
    qc.x(0)
    qc.cx(0, 1)
    res = eoq.run(qc)
    expect = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(1)
    qc.cx(0, 1)
    res = eoq.run(qc)
    expect = np.array([0.0, 1.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(0)
    qc.x(1)
    qc.cx(0, 1)
    res = eoq.run(qc)
    expect = np.array([0.0, 0.0, 1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(0)
    qc.h(0)
    qc.cx(0, 1)
    res = eoq.run(qc)
    expect = np.array([1.0, 0.0, 0.0, -1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_measure_1q():

    eoq = EoqEngine(DotArchitecture(3))

    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 1
    assert res.num_dots == 3
    assert res.m_last == '0'
    assert res.freq == {'0': 1}

    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 1
    assert res.num_dots == 3
    assert res.m_last == '1'
    assert res.freq == {'1': 1}
    
    qc = QuantumCircuit(1, 2)
    qc.x(0)
    qc.measure(0, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 2
    assert res.num_dots == 3
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(1, 3)
    qc.x(0)
    qc.measure(0, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 3
    assert res.num_dots == 3
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(1, 3)
    qc.x(0)
    qc.measure(0, 2)
    res = eoq.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 3
    assert res.num_dots == 3
    assert res.m_last == '001'
    assert res.freq == {'001': 1}
    
def test_measure_2q():

    eoq = EoqEngine(DotArchitecture(6))

    # X(0): num_clbits=2
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '10'
    assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0, 1], [1, 0])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([1, 0], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([1, 0], [1, 0])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '10'
    assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure(0, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '10'
    assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0], [1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure(1, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '00'
    assert res.freq == {'00': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure(1, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '00'
    assert res.freq == {'00': 1}
    
    # X(0): num_clbits=3
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '100'
    assert res.freq == {'100': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [1, 0])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [1, 0])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '100'
    assert res.freq == {'100': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [1, 2])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [2, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '001'
    assert res.freq == {'001': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [1, 2])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '001'
    assert res.freq == {'001': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [2, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    # H(0)-CX(0,1): num_clbits=2
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    if res.m_last == '00':
        assert res.freq == {'00': 1}
    elif res.m_last == '11':
        assert res.freq == {'11': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    if res.m_last == '00':
        assert res.freq == {'00': 1}
    elif res.m_last == '10':
        assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    if res.m_last == '00':
        assert res.freq == {'00': 1} 
    elif res.m_last == '01':
        assert res.freq == {'01': 1} 
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(1, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    if res.m_last == '00':
        assert res.freq == {'00': 1} 
    elif res.m_last == '10':
        assert res.freq == {'10': 1} 
    
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(1, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    if res.m_last == '00':
        assert res.freq == {'00': 1} 
    elif res.m_last == '01':
        assert res.freq == {'01': 1} 
    
    # H(0)-CX(0,1): num_clbits=3
    
    qc = QuantumCircuit(2, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '110':
        assert res.freq == {'110': 1} 
    
    qc = QuantumCircuit(2, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [1, 2])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '011':
        assert res.freq == {'011': 1} 
    
    qc = QuantumCircuit(2, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [2, 0])
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '101':
        assert res.freq == {'101': 1} 
    
    qc = QuantumCircuit(2, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '100':
        assert res.freq == {'100': 1} 
    
    qc = QuantumCircuit(2, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '010':
        assert res.freq == {'010': 1} 
    
    qc = QuantumCircuit(2, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 2)
    res = eoq.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '001':
        assert res.freq == {'001': 1} 
    
def test_measure_3q():

    eoq = EoqEngine(DotArchitecture(9))

    # X(0): num_clbits=3
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1, 2], [0, 1, 2])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '100'

    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '100'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1], [1, 2])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '010'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1], [2, 0])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '001'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure(0, 0)
    res = eoq.run(qc)
    assert res.m_last == '100'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure(0, 1)
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '010'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure(0, 2)
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '001'
    
    # H(0)-CX(0,1): num_clbits=3
    
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1, 2], [0, 1, 2])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '110':
        assert res.freq == {'110': 1} 
    
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '110':
        assert res.freq == {'110': 1} 
    
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([1, 2], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '100':
        assert res.freq == {'100': 1} 
    
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([2, 0], [0, 1])
    res = eoq.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '010':
        assert res.freq == {'010': 1} 

def test_simulate_exception():

    eoq = EoqEngine(DotArchitecture(3))
    with pytest.raises(TypeError):
        eoq.run("foo")

    with pytest.raises(TypeError):
        eoq.run(123)
