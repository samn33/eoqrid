import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit


def plot_qc(qc: QuantumCircuit) -> None:

    style = {
        "displaycolor": {
            "ex": 'darkred',
            "m": 'darkgreen',
        }
    }
    qc.draw('mpl', style=style)
    plt.show()


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


def random_quantum_circuit(num_qubits: int, depth: int, seed: int | None = None,
                           with_measurements: bool = False) -> QuantumCircuit:
    """
    get a random quantum circuit.

    Parameters
    ----------
    num_qubits : int
        number of quantum bits.
    depth : int
        depth of quantum circuit.
    with_measurement : bool
        make quantum circuit with measurements.
    seed : int | None, default None
        seed of random generation.

    Returns
    -------
    qc : QuantumCircuit
        random quantum circuit.

    """
    if seed is not None:
        random.seed(seed)

    gates = ['h','x','z','rx','rz','s','sdg','t','tdg']
    if with_measurements is False:
        qc = QuantumCircuit(num_qubits)
        if num_qubits == 1:
            pass
        elif num_qubits > 1:
            gates += ['cx','cz','swap']
        else:
            raise ValueError("num_qubits must be larger than 1.")
    else:
        qc = QuantumCircuit(num_qubits, 1)
        gates += ['measure']

    for _ in range(depth):
        gate = random.choice(gates)

        if gate == 'cx':
            ops = random.sample(range(num_qubits), 2)
            qc.cx(ops[0], ops[1])
        elif gate == 'cz':
            ops = random.sample(range(num_qubits), 2)
            qc.cz(ops[0], ops[1])
        elif gate == 'swap':
            ops = random.sample(range(num_qubits), 2)
            qc.swap(ops[0], ops[1])
        elif gate == 'rx':
            q = random.randint(0, num_qubits - 1)
            phase = np.pi * random.uniform(-2.0, 2.0)
            qc.rx(phase, q)
        elif gate == 'rz':
            q = random.randint(0, num_qubits - 1)
            phase = np.pi * random.uniform(-2.0, 2.0)
            qc.rz(phase, q)
        elif gate == 'measure':
            q = random.randint(0, num_qubits - 1)
            qc.measure(q, 0)
        else:
            q = random.randint(0, num_qubits - 1)
            getattr(qc, gate)(q)

    return qc
