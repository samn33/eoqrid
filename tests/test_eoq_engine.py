import random

import networkx as nx
import pytest

from eoqrid import DotArchitecture, EoqEngine
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
        arch = random_arch(num_dots, num_dots) # number of nodes and edges
        eoq = EoqEngine(arch)
        assert eoq.num_dots == num_dots
        assert eoq.num_dots == len(eoq.arch.topology)
        assert len(eoq.arch.topology.edges()) == num_dots

    for _ in range(trial):
        arch = DotArchitecture(num_dots)
        eoq = EoqEngine(arch)
        assert eoq.num_dots == num_dots
        assert eoq.num_dots == len(eoq.arch.topology)
        assert len(eoq.arch.topology.edges()) == (num_dots - 1) * num_dots / 2

def test_construct_by_num_dots():

    num_dots = 6
    eoq = EoqEngine(num_dots)

    assert eoq.num_dots == num_dots
    assert eoq.num_dots == len(eoq.arch.topology)
    assert len(eoq.arch.topology.edges()) == (num_dots - 1) * num_dots / 2
    
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
    eoq = EoqEngine(arch)

    assert eoq.num_dots == num_dots
    assert eoq.num_dots == len(eoq.arch.topology)
    assert len(eoq.arch.topology.edges()) == num_edges

def test_exception_num_dots_is_not_multiple_of_3():

    with pytest.raises(ValueError):
        EoqEngine(4)

    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(2, 3)
    arch.add_edge(3, 4)

    with pytest.raises(ValueError):
        EoqEngine(arch)

def test_exception_arhi_not_connected():

    arch = DotArchitecture()
    arch.add_edge(0, 1)
    arch.add_edge(1, 2)
    arch.add_edge(3, 4)
    arch.add_edge(4, 5)

    with pytest.raises(ValueError):
        EoqEngine(arch)

def test_exception_num_dots_is_negative():

    with pytest.raises(ValueError):
        EoqEngine(-1)

def test_exception_num_dots_is_str():

    with pytest.raises(TypeError):
        EoqEngine("3")
