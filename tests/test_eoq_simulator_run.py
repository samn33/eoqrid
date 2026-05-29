import pytest
import math
import numpy as np
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator

def equal_array(a, b):
    return all([math.isclose(abs(aa-bb), 0, abs_tol=1e-8) for aa, bb in zip(a, b)])

def equal_state_vector(a, b):
    return math.isclose(abs(np.vdot(a, b)), 1.0, abs_tol=1e-8)
    
def test_initial_logical_qstate():

    sim = EoqSimulator()

    qc = QuantumCircuit(1)
    res = sim.run(qc)
    expect = np.array([1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    res = sim.run(qc)
    expect = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_initial_physical_qstate():

    sim = EoqSimulator()

    qc = QuantumCircuit(1)
    res = sim.run(qc)
    expect = np.array([0.0, 0.0, 0.70710678, 0.0, -0.70710678, 0.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.physical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    res = sim.run(qc)
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

    sim = EoqSimulator()

    qc = QuantumCircuit(1)
    qc.x(0)
    res = sim.run(qc)
    expect = np.array([0.0, 1.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(1)
    res = sim.run(qc)
    expect = np.array([0.0, 1.0, 0.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(0)
    qc.x(1)
    res = sim.run(qc)
    expect = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_h_gate():

    sim = EoqSimulator()

    qc = QuantumCircuit(1)
    qc.h(0)
    res = sim.run(qc)
    expect = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(1)
    qc.x(0)
    qc.h(0)
    res = sim.run(qc)
    expect = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    res = sim.run(qc)
    expect = np.array([1.0, 0.0, 1.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(1)
    res = sim.run(qc)
    expect = np.array([1.0, 1.0, 0.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(1)
    res = sim.run(qc)
    expect = np.array([1.0, 1.0, 1.0, 1.0], dtype=complex) / 2.0
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_z_gate():

    sim = EoqSimulator()

    qc = QuantumCircuit(1)
    qc.z(0)
    res = sim.run(qc)
    expect = np.array([1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.z(0)
    res = sim.run(qc)
    expect = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.z(0) 
    res = sim.run(qc)
    expect = np.array([1.0, 0.0, -1.0, 0.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(1)
    qc.z(1) 
    res = sim.run(qc)
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
    res = sim.run(qc)
    expect = np.array([1.0, 1.0, -1.0, -1.0], dtype=complex) / 2.0
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
def test_rz_gate():

    sim = EoqSimulator()

    qc = QuantumCircuit(1)
    qc.rz(np.pi/4.0, 0)
    res = sim.run(qc)
    expect = np.array([1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.rz(np.pi/4.0, 0)
    res = sim.run(qc)
    actual = res.qstate.logical_qstate
    expect = np.array([1.0/np.sqrt(2.0), 0.5+0.5j], dtype=complex)
    assert res.num_qubits == 1
    assert res.num_clbits == 0
    assert res.num_dots == 3
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.rz(np.pi/4.0, 0)
    res = sim.run(qc)
    expect = np.array([1.0/np.sqrt(2.0), 0.0, 0.5+0.5j, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(1)
    qc.rz(np.pi/4.0, 1)
    res = sim.run(qc)
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
    res = sim.run(qc)
    expect = np.array([0.5, 0.5, 1.0/np.sqrt(8.0)+1.0j/np.sqrt(8.0), 1.0/np.sqrt(8.0)+1.0j/np.sqrt(8.0)], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)
    
def test_cx_gate():

    sim = EoqSimulator()

    qc = QuantumCircuit(2)
    qc.x(0)
    qc.cx(0, 1)
    res = sim.run(qc)
    expect = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.x(1)
    qc.cx(0, 1)
    res = sim.run(qc)
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
    res = sim.run(qc)
    expect = np.array([0.0, 0.0, 1.0, 0.0], dtype=complex)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    res = sim.run(qc)
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
    res = sim.run(qc)
    expect = np.array([1.0, 0.0, 0.0, -1.0], dtype=complex) / np.sqrt(2.0)
    actual = res.qstate.logical_qstate
    assert res.num_qubits == 2
    assert res.num_clbits == 0
    assert res.num_dots == 6
    assert equal_state_vector(expect, actual)

def test_measure_1q():

    sim = EoqSimulator()

    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)
    res = sim.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 1
    assert res.num_dots == 3
    assert res.m_last == '0'
    assert res.freq == {'0': 1}

    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    res = sim.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 1
    assert res.num_dots == 3
    assert res.m_last == '1'
    assert res.freq == {'1': 1}
    
    qc = QuantumCircuit(1, 2)
    qc.x(0)
    qc.measure(0, 1)
    res = sim.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 2
    assert res.num_dots == 3
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(1, 3)
    qc.x(0)
    qc.measure(0, 1)
    res = sim.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 3
    assert res.num_dots == 3
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(1, 3)
    qc.x(0)
    qc.measure(0, 2)
    res = sim.run(qc)
    assert res.num_qubits == 1
    assert res.num_clbits == 3
    assert res.num_dots == 3
    assert res.m_last == '001'
    assert res.freq == {'001': 1}
    
def test_measure_2q():

    sim = EoqSimulator()

    # X(0): num_clbits=2
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '10'
    assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0, 1], [1, 0])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([1, 0], [0, 1])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([1, 0], [1, 0])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '10'
    assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure(0, 0)
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '10'
    assert res.freq == {'10': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0], [1])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '01'
    assert res.freq == {'01': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure(1, 0)
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '00'
    assert res.freq == {'00': 1}
    
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure(1, 1)
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 2
    assert res.num_dots == 6
    assert res.m_last == '00'
    assert res.freq == {'00': 1}
    
    # X(0): num_clbits=3
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '100'
    assert res.freq == {'100': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [1, 0])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [0, 1])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [1, 0])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '100'
    assert res.freq == {'100': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [1, 2])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '010'
    assert res.freq == {'010': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([0, 1], [2, 1])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '001'
    assert res.freq == {'001': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [1, 2])
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    assert res.m_last == '001'
    assert res.freq == {'001': 1}
    
    qc = QuantumCircuit(2, 3)
    qc.x(0)
    qc.measure([1, 0], [2, 1])
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.num_dots == 6
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '001':
        assert res.freq == {'001': 1} 
    
def test_measure_3q():

    sim = EoqSimulator()

    # X(0): num_clbits=3
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1, 2], [0, 1, 2])
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '100'

    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '100'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1], [1, 2])
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '010'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure([0, 1], [2, 0])
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '001'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure(0, 0)
    res = sim.run(qc)
    assert res.m_last == '100'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure(0, 1)
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '010'
    
    qc = QuantumCircuit(3, 3)
    qc.x(0)
    qc.measure(0, 2)
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    assert res.m_last == '001'
    
    # H(0)-CX(0,1): num_clbits=3
    
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1, 2], [0, 1, 2])
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
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
    res = sim.run(qc)
    assert res.num_qubits == 3
    assert res.num_clbits == 3
    assert res.num_dots == 9
    if res.m_last == '000':
        assert res.freq == {'000': 1} 
    elif res.m_last == '010':
        assert res.freq == {'010': 1} 

def test_run_exception():

    sim = EoqSimulator()
    with pytest.raises(TypeError):
        sim.run("foo")

    with pytest.raises(TypeError):
        sim.run(123)
