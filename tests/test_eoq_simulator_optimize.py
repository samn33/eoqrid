import pytest
import math
import networkx as nx
import numpy as np
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator, ExchangeInteraction, Measurement

# functions

def equal_state_vector(a, b):
    return math.isclose(abs(np.vdot(a, b)), 1.0, abs_tol=1e-8)

def is_valid(eoq: EoqSimulator, qc_in: QuantumCircuit, qc_out: QuantumCircuit) -> bool:

    for name in qc_in.count_ops():
        if name not in ('ex', 'm'):
            raise ValueError("qc_in is invalid.")
    for name in qc_out.count_ops():
        if name not in ('ex', 'm'):
            raise ValueError("qc_in is invalid.")

    topology = eoq.topology
    if topology is None:
        return qc_in == qc_out

    for i, inst in enumerate(qc_out):
        name = inst.operation.name
        #params = inst.params
        qid = [q._index for q in inst.qubits]

        if not topology.has_edge(qid[0], qid[1]):
            return False

    res_in = eoq.execute(qc_in)
    res_out = eoq.execute(qc_out)

    if 'm' not in qc_in.count_ops():
        return equal_state_vector(res_in.qstate.physical_qstate, res_out.qstate.physical_qstate)

    return True

# tests

def test_3dots_without_measurements_all_to_all():

    eoq = EoqSimulator()
    qc_in = QuantumCircuit(3)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)
    
def test_3dots_with_measurements_all_to_all():

    eoq = EoqSimulator()
    qc_in = QuantumCircuit(3, 1)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(Measurement(), [0, 1], [0])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)
    
def test_3dots_without_measurements_linear():

    # linear
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)

    eoq = EoqSimulator(topo)
    qc_in = QuantumCircuit(3)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)
    
def test_3dots_with_measurements_linear():

    # linear
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)

    eoq = EoqSimulator(topo)
    qc_in = QuantumCircuit(3, 1)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(Measurement(), [0, 1], [0])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_6dots_without_measurements_all_to_all():

    eoq = EoqSimulator()
    qc_in = QuantumCircuit(6)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(ExchangeInteraction(3.0), [0, 3])
    qc_in.append(ExchangeInteraction(4.0), [0, 4])
    qc_in.append(ExchangeInteraction(5.0), [0, 5])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_6dots_with_measurements_all_to_all():

    eoq = EoqSimulator()
    qc_in = QuantumCircuit(6, 2)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(ExchangeInteraction(3.0), [0, 3])
    qc_in.append(ExchangeInteraction(4.0), [0, 4])
    qc_in.append(ExchangeInteraction(5.0), [0, 5])
    qc_in.append(Measurement(), [0, 1], [0])
    qc_in.append(Measurement(), [3, 4], [1])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_6dots_without_measurements_linear():

    # linear
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(2, 3)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)

    eoq = EoqSimulator(topo)
    qc_in = QuantumCircuit(6)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(ExchangeInteraction(3.0), [0, 3])
    qc_in.append(ExchangeInteraction(4.0), [0, 4])
    qc_in.append(ExchangeInteraction(5.0), [0, 5])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_6dots_with_measurements_linear():

    # linear
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(2, 3)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)

    eoq = EoqSimulator(topo)
    qc_in = QuantumCircuit(6, 2)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(ExchangeInteraction(3.0), [0, 3])
    qc_in.append(ExchangeInteraction(4.0), [0, 4])
    qc_in.append(ExchangeInteraction(5.0), [0, 5])
    qc_in.append(Measurement(), [0, 1], [0])
    qc_in.append(Measurement(), [3, 4], [1])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_6dots_without_measurements_butterfly():

    # butterfly
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(1, 4)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)

    eoq = EoqSimulator(topo)
    qc_in = QuantumCircuit(6)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(ExchangeInteraction(3.0), [0, 3])
    qc_in.append(ExchangeInteraction(4.0), [0, 4])
    qc_in.append(ExchangeInteraction(5.0), [0, 5])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_6dots_with_measurements_butterfly():

    # butterfly
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(1, 4)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)

    eoq = EoqSimulator(topo)
    qc_in = QuantumCircuit(6, 2)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(ExchangeInteraction(3.0), [0, 3])
    qc_in.append(ExchangeInteraction(4.0), [0, 4])
    qc_in.append(ExchangeInteraction(5.0), [0, 5])
    qc_in.append(Measurement(), [0, 1], [0])
    qc_in.append(Measurement(), [3, 4], [1])

    for optimization_level in (0, 1, 2, 3):
        qc_out = eoq.optimize(qc_in, optimization_level=optimization_level, seed=123)
        assert is_valid(eoq, qc_in, qc_out)

def test_exception_qc_is_not_quantum_circuit():

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)

    eoq = EoqSimulator()
    with pytest.raises(TypeError):
        eoq.optimize(qc_native="qc_native")
        
    eoq = EoqSimulator(topo)
    with pytest.raises(TypeError):
        eoq.optimize(qc_native="qc_native")
        
def test_exception_gate_is_not_supported():

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)

    qc_native = QuantumCircuit(3, 1)
    qc_native.append(ExchangeInteraction(1.0), [0, 1])
    qc_native.append(ExchangeInteraction(2.0), [0, 2])
    qc_native.h(0)
    qc_native.append(Measurement(), [0, 1], [0])

    eoq = EoqSimulator()
    with pytest.raises(ValueError):
        eoq.optimize(qc_native=qc_native)
        
    eoq = EoqSimulator(topo)
    with pytest.raises(ValueError):
        eoq.optimize(qc_native=qc_native)
        
def test_exception_optimization_level_is_not_supported():

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)

    qc_native = QuantumCircuit(3, 1)
    qc_native.append(ExchangeInteraction(1.0), [0, 1])
    qc_native.append(ExchangeInteraction(2.0), [0, 2])
    qc_native.append(Measurement(), [0, 1], [0])

    eoq = EoqSimulator()
    with pytest.raises(ValueError):
        eoq.optimize(qc_native=qc_native, optimization_level=4)
        
    eoq = EoqSimulator(topo)
    with pytest.raises(ValueError):
        eoq.optimize(qc_native=qc_native, optimization_level=4)

def test_exception_num_qubits_is_too_large():

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)

    qc_native = QuantumCircuit(4, 1)
    qc_native.append(ExchangeInteraction(1.0), [0, 1])
    qc_native.append(ExchangeInteraction(2.0), [0, 2])
    qc_native.append(Measurement(), [0, 1], [0])

    eoq = EoqSimulator(topo)
    with pytest.raises(ValueError):
        eoq.optimize(qc_native=qc_native)
