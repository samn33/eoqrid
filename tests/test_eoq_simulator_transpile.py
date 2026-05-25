import pytest
import random
from qiskit import QuantumCircuit

from eoqrid import EoqSimulator, ExchangeInteraction, Measurement
from eoqrid.util import random_quantum_circuit, random_connected_graph

# functions

def is_valid(eoq: EoqSimulator, qc_in: QuantumCircuit, qc_out: QuantumCircuit) -> bool:

    for name in qc_out.count_ops():
        if name not in ('ex', 'm'):
            raise ValueError("qc_in is invalid.")

    topology = eoq.topology
    if topology is None:
        return True

    for i, inst in enumerate(qc_out):
        name = inst.operation.name
        qid = [q._index for q in inst.qubits]

        if not topology.has_edge(qid[0], qid[1]):
            return False

    return True

# tests

@pytest.mark.parametrize("num_qubits, with_measurements", [
    (1, False),
    (1, True),
    (2, False),
    (2, True),
    (3, False),
    (3, True),
    (4, False),
    (4, True),
])
def test_random_qc(num_qubits, with_measurements):

    random.seed(123)
    num_dots = num_qubits * 3
    depth = 10
    trial = 3

    for _ in range(trial):
        topo = random_connected_graph(num_dots, num_dots)
        qc_in = random_quantum_circuit(num_qubits, depth, with_measurements)
        eoq = EoqSimulator(topo)
        for optimization_level in (0, 1, 2, 3):
            qc_out = eoq.transpile(qc_in, optimization_level=optimization_level)
            assert is_valid(eoq, qc_in, qc_out)

def test_exception_qc_is_for_native_device():

    qc_in = QuantumCircuit(3, 1)
    qc_in.h(0)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(Measurement(), [0, 1], [0])
    eoq = EoqSimulator()

    with pytest.raises(ValueError):
        eoq.transpile(qc_in)

def test_exception_optimization_level_is_invalid():

    qc_in = QuantumCircuit(2)
    qc_in.h(0)
    qc_in.cx(0, 1)
    eoq = EoqSimulator()

    with pytest.raises(ValueError):
        eoq.transpile(qc_in, optimization_level=4)
