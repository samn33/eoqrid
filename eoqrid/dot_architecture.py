from __future__ import annotations

import itertools

import networkx as nx


class DotArchitecture:
    """
    Quantum dot architecture description.

    Attributes
    ----------
    topology : nx.Graph
        Quantum chip connectivity graph.
    num_dots : int
        Number of quantum dots.
    readout_pairs : list[tuple[int, int]]
        Dot index pairs for readout.
    """
    def __init__(self, topology: nx.Graph | int = 0) -> None:
        """
        Initialize the quantum dot architecture.

        Parameters
        ----------
        topology : nx.Graph or int
            Quantum chip graph topology, or integer number of dots for a complete graph.

        Notes
        -----
        If an integer is passed, a fully connected graph of that size is created.
        """
        self._readout_pairs = []

        if isinstance(topology, int):
            num_dots = topology
            self._check_num_dots(num_dots)
            self._topology = nx.Graph()
            for a, b in itertools.combinations(range(topology), 2):
                self._readout_pairs.append((a, b))
                self._topology.add_edge(a, b)
                self._topology[a][b]["readout"] = True
                self._topology.nodes[a]["readout"] = [True, True]
                self._topology.nodes[b]["readout"] = [True, True]
        elif isinstance(topology, nx.Graph):
            self._topology = topology
            num_dots = len(self._topology)
            self._check_num_dots(num_dots)
            for a, b in self._topology.edges():
                self._topology[a][b]["readout"] = False
            for a in self._topology.nodes():
                self._topology.nodes[a]["readout"] = [False, False]
        else:
            raise TypeError("the constructor argument must be a positive integer or a nx.Graph.")

    def _check_num_dots(self, num_dots):
        if num_dots < 0 or (num_dots >= 0 and num_dots % 3 != 0):
            raise ValueError("number of quantum dots must be a positive and multiple of 3.")

    def __str__(self) -> str:
        s = f"- nodes: {self._topology.nodes(data='readout')}\n"
        s += f"- edges: {self._topology.edges(data='readout')}\n"
        s += f"- readout pairs: {self._readout_pairs}"
        return s
        
    @property
    def topology(self) -> nx.Graph:
        return self._topology

    @property
    def num_dots(self) -> int:
        return len(self.topology)

    @property
    def readout_pairs(self) -> list[tuple(int,int)]:
        return self._readout_pairs

    def is_valid(self) -> bool:
        """
        Check whether the object is in a valid state.

        Returns
        -------
        bool
            True if the object is valid, False otherwise.
        """
        if self.num_dots < 0 or (self.num_dots >= 0 and self.num_dots % 3 != 0) or not nx.is_connected(self._topology):
            return False
        for a, b in self._readout_pairs:
            if not self._topology.has_edge(a, b):
                return False
        return True
        
    def add_edge(self, a: int, b: int) -> None:
        """
        Add an undirected edge between two quantum dots.

        Parameters
        ----------
        a : int
            Index of the first quantum dot.
        b : int
            Index of the second quantum dot.
        """
        if self._topology.has_edge(a, b):
            return
        self._topology.add_node(a)
        self._topology.add_node(b)
        self._topology.add_edge(a, b)
        self._topology[a][b]["readout"] = False
        self._topology.nodes[a]["readout"] = [False, False]
        self._topology.nodes[b]["readout"] = [False, False]

    def add_readout_pair(self, a: int, b: int) -> None:
        """
        Add a readout pair for two connected quantum dots.

        Parameters
        ----------
        a : int
            Index of the first measurement dot.
        b : int
            Index of the second measurement dot.

        Raises
        ------
        ValueError
            If dots `a` and `b` do not exist or are not connected.
        """
        if not self._topology.has_edge(a, b):
            raise ValueError("can't add the readout pair, because two dots are not connected.")
        self._readout_pairs.append((a, b))
        self._topology[a][b]["readout"] = True
        self._topology.nodes[a]["readout"][0] = True
        self._topology.nodes[b]["readout"][1] = True

    def is_readout_pair(self, a: int, b: int) -> bool:
        """
        Check whether a and b form a readout pair.

        Parameters
        ----------
        a : int
            Index of the first measurement dot.
        b : int
            Index of the second measurement dot.

        Returns
        -------
        bool
            True if `a` and `b` form a readout pair, False otherwise.
        """
        return (a, b) in self._readout_pairs
