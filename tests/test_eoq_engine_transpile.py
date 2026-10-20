import random

import pytest
from qiskit import QuantumCircuit

from eoqrid import (
    DotArchitecture,
    EoqEngine,
    ExchangeInteraction,
    Measurement,
    PhysicalQuantumCircuit,
)
from eoqrid.util import random_arch, random_quantum_circuit

# functions

def is_valid(arch: DotArchitecture, qc_in: QuantumCircuit, qc_out: PhysicalQuantumCircuit) -> bool:

    for name in qc_out.count_ops():
        if name not in ('ex', 'm', 'sin', 'up'):
            raise ValueError("qc_in is invalid.")

    if arch.topology is None:
        return True

    for i, inst in enumerate(qc_out.to_qiskit()):
        name = inst.operation.name
        qid = [q._index for q in inst.qubits]
        if name in ('up', 'sin'):
            continue
        elif name == 'm':
            if qid in arch.readout_pairs:
                return False
        elif not arch.topology.has_edge(qid[0], qid[1]):
            return False

    return True

# tests

@pytest.mark.parametrize("num_dots, num_qubits, num_measurements, num_readout_pairs", [
    (3, 1, 0, 0),
    (3, 1, 1, 1),
    (3, 1, 2, 2),
    (3, 1, 3, 3),
    (6, 2, 0, 0),
    (6, 2, 1, 1),
    (6, 2, 2, 2),
    (6, 2, 3, 3),
    (9, 3, 0, 0),
    (9, 3, 1, 1),
    (9, 3, 2, 2),
    (9, 3, 3, 3),
    (12, 4, 0, 0),
    (12, 4, 1, 1),
    (12, 4, 2, 2),
    (12, 4, 3, 3),
])
def test_random_qc(num_dots, num_qubits, num_measurements, num_readout_pairs):

    random.seed(123)
    depth = 10
    trial = 3

    for _ in range(trial):
        arch = random_arch(num_dots, num_dots, num_readout_pairs=num_readout_pairs)
        qc_in = random_quantum_circuit(num_qubits, depth, num_measurements=num_measurements)
        eoq = EoqEngine(arch)
        for optimization_level in (0, 1, 2, 3):
            qc_out = eoq.transpile(qc_in, optimization_level=optimization_level)
            assert is_valid(arch, qc_in, qc_out)

def test_exception_qc_is_for_native_device():

    qc_in = QuantumCircuit(3, 1)
    qc_in.h(0)
    qc_in.append(ExchangeInteraction(1.0), [0, 1])
    qc_in.append(ExchangeInteraction(2.0), [0, 2])
    qc_in.append(Measurement(), [0, 1], [0])
    eoq = EoqEngine(DotArchitecture(9))

    with pytest.raises(ValueError):
        eoq.transpile(qc_in)

def test_exception_optimization_level_is_invalid():

    qc_in = QuantumCircuit(2)
    qc_in.h(0)
    qc_in.cx(0, 1)
    eoq = EoqEngine(DotArchitecture(9))

    with pytest.raises(ValueError):
        eoq.transpile(qc_in, optimization_level=4)

def test_exception_topology_size_is_not_match_num_dots():

    qc_in = QuantumCircuit(2)
    qc_in.h(0)
    qc_in.cx(0, 1)
    eoq = EoqEngine(DotArchitecture(5))

    with pytest.raises(ValueError):
        eoq.transpile(qc_in, optimization_level=3)
