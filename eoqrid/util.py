import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit


def plot_graph(G: nx.Graph) -> None:
    """
    plot the graph.

    Parameters
    ----------
    G : nx.Graph
        graph

    Returns
    -------
    None

    """
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=500,
        font_size=12,
        font_weight="bold",
    )

    raw_labels = nx.get_edge_attributes(G, 'weight')
    edge_labels = {k: f"{v:.2f}" for k, v in raw_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.show()


def random_connected_graph(n: int, m:int, seed: int | None = None) -> nx.Graph:
    """
    get a random connected graph.
    
    Parameters
    ----------
    n : int
        number of nodes.
    m : int
        number of edges (m >= n-1).
    seed : int | None, default None
        seed of random generation.

    Returns
    -------
    G : nx.Graph
        random connected graph.
    
    """
    if seed is not None:
        random.seed(seed)

    G = nx.random_labeled_tree(n)

    while G.number_of_edges() < m:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v)

    return G


def random_quantum_circuit(num_qubits: int, depth: int, seed: int | None = None) -> QuantumCircuit:
    """
    get a random quantum circuit.

    Parameters
    ----------
    num_qubits : int
        number of quantum bits.
    depth : int
        depth of quantum circuit.
    seed : int | None, default None
        seed of random generation.

    Returns
    -------
    qc : QuantumCircuit
        random quantum circuit.

    """
    if seed is not None:
        random.seed(seed)

    qc = QuantumCircuit(num_qubits)
    gates = ['h','x','z','rz','cx','swap']

    for _ in range(depth):
        gate = random.choice(gates)

        if gate == 'cx':
            ops = random.sample(range(num_qubits), 2)
            qc.cx(ops[0], ops[1])
        elif gate == 'swap':
            ops = random.sample(range(num_qubits), 2)
            qc.swap(ops[0], ops[1])
        elif gate == 'rz':
            q = random.randint(0, num_qubits - 1)
            phase = np.pi * random.uniform(-2.0, 2.0)
            qc.rz(phase, q)
        else:
            q = random.randint(0, num_qubits - 1)
            getattr(qc, gate)(q)

    return qc
