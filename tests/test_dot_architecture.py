import random

import networkx as nx
import pytest

from eoqrid import DotArchitecture
from eoqrid.util import random_arch


@pytest.mark.parametrize("trial, num_dots, seed", [
    (3, 3, 123),
    (3, 6, 123),
    (3, 9, 123),
    (3, 12, 123),
])
def test_random_topo(trial, num_dots, seed):

    random.seed(seed)

    for _ in range(trial):
        arch = random_arch(num_dots, num_dots)
        assert arch.num_dots == num_dots

    for _ in range(trial):
        arch = DotArchitecture(num_dots)
        assert arch.num_dots == num_dots

def test_construct_by_num_dots():

    num_dots = 6
    arch = DotArchitecture(num_dots)

    assert arch.num_dots == num_dots
    assert arch.num_dots == len(arch.topology)
    assert len(arch.topology.edges()) == (num_dots - 1) * num_dots / 2
    
def test_construct_by_topology():

    num_dots = 6
    num_edges = 5
    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(2, 3)
    topo.add_edge(3, 4)
    topo.add_edge(4, 5)
    arch = DotArchitecture(topo)

    assert arch.num_dots == num_dots
    assert arch.num_dots == len(arch.topology)
    assert len(arch.topology.edges()) == num_edges

def test_construct_and_add_edge():

    num_dots = 6
    num_edges = 5
    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(2, 3)
    arch.add_edge(3, 4)
    arch.add_edge(4, 5)

    assert arch.num_dots == num_dots
    assert arch.num_dots == len(arch.topology)
    assert len(arch.topology.edges()) == num_edges
    assert arch.is_valid()

    arch.add_edge(5, 6)
    assert not arch.is_valid()
    
def test_readout_pairs():

    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(2, 3)
    arch.add_edge(3, 4)
    arch.add_edge(4, 5)
    
    arch.add_readout_pair(0, 1)
    arch.add_readout_pair(1, 2)

    assert arch.is_readout_pair(0, 1)
    assert arch.is_readout_pair(1, 2)
    assert not arch.is_readout_pair(1, 0)
    assert not arch.is_readout_pair(0, 3)
    
def test_exception_num_dots_is_not_multiple_of_3():

    with pytest.raises(ValueError):
        DotArchitecture(4)

    topo = nx.Graph()
    topo.add_edge(0, 1)
    topo.add_edge(1, 2)
    topo.add_edge(2, 3)
    topo.add_edge(3, 4)

    with pytest.raises(ValueError):
        DotArchitecture(topo)

def test_exception_num_dots_is_negative():

    with pytest.raises(ValueError):
        DotArchitecture(-1)

def test_exception_num_dots_is_str():

    with pytest.raises(TypeError):
        DotArchitecture("3")
