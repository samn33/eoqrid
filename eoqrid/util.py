import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from qiskit import QuantumCircuit

from eoqrid.dot_architecture import DotArchitecture
from eoqrid.physical_quantum_circuit import PhysicalQuantumCircuit


def plot_qc(qc: QuantumCircuit | PhysicalQuantumCircuit) -> None:
    """
    Plot the quantum circuit.

    Parameters
    ----------
    qc : QuantumCircuit or PhysicalQuantumCircuit
        Logical or physical quantum circuit.
    """
    if isinstance(qc, QuantumCircuit):
        qc_plot = qc
    elif isinstance(qc, PhysicalQuantumCircuit):
        qc_plot = qc.to_qiskit()
    
    style = {
        "displaycolor": {
            "ex": 'darkred',
            "m": 'darkgreen',
            "sin": 'dimgrey',
        }
    }
    qc_plot.draw('mpl', style=style)

    plt.show()


def plot_graph(G: nx.Graph) -> None:
    """
    Plot the graph.

    Parameters
    ----------
    G : nx.Graph
        graph
    """
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="grey",
        edgecolors="black",
        linewidths=0.1,
        edge_color="black",
        node_size=500,
        font_size=12,
        font_weight="bold",
    )

    node_color = []
    for i, readout in G.nodes(data="readout"):
        match readout:
            case [False, False]:
                node_color.append("lightblue")
            case [True, False]:
                node_color.append("pink")
            case [False, True]:
                node_color.append("lightgreen")
            case [True, True]:
                node_color.append("yellow")

    nx.draw_networkx_nodes(G, pos, node_color = node_color)
    
    plt.show()


def plot_arch(arch: DotArchitecture) -> None:
    """
    Plot the quantum dot architecture layout.

    Parameters
    ----------
    arch : DotArchitecture
        Quantum dot architecture layout.
    """
    plot_graph(arch.topology)


def random_arch(
        n: int,
        m:int,
        num_readout_pairs: int = 0,
        seed: int | None = None
) -> DotArchitecture:
    """
    Generate a random quantum dot architecture layout.

    Parameters
    ----------
    n : int
        Number of nodes (quantum dots).
    m : int
        Number of edges (couplings between dots, where m >= n - 1).
    num_readout_pairs : int, default 0
        Number of readout pairs.
    seed : int or None, default None
        Random seed for generation reproducibility.

    Returns
    -------
    DotArchitecture
        Randomized quantum dot architecture layout.
    """
    if seed is not None:
        random.seed(seed)

    G = nx.random_labeled_tree(n)

    while G.number_of_edges() < m:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v)

    edge_id_list = []
    if num_readout_pairs > 0:
        edge_id_list = random.sample(range(len(G.edges())), num_readout_pairs)

    arch = DotArchitecture(G)
    for i in edge_id_list:
        a, b = list(G.edges)[i]
        arch.add_readout_pair(a, b)
        
    return arch


def random_quantum_circuit(
        num_qubits: int,
        depth: int,
        num_measurements: int = 0,
        seed: int | None = None
) -> QuantumCircuit:
    """
    Generate a random quantum circuit.

    Parameters
    ----------
    num_qubits : int
        Number of logical qubits.
    depth : int
        Depth of the quantum circuit.
    num_measurements : int, default 0
        Number of measurements.
    seed : int or None, default None
        Random seed for circuit generation reproducibility.

    Returns
    -------
    QuantumCircuit
        Randomized quantum circuit.
    """
    if depth - num_measurements < 0:
        raise ValueError("depth must be equal or larger than number of measurements.")
    if seed is not None:
        random.seed(seed)

    gates = ['h','x','z','rx','rz','s','sdg','t','tdg']
    qc = QuantumCircuit(num_qubits, num_measurements)
    if num_qubits == 1:
        pass
    elif num_qubits > 1:
        gates += ['cx','cz','swap']
    else:
        raise ValueError("num_qubits must be larger than 1.")

    gates_list = []
    for _ in range(depth - num_measurements):
        gates_list.append(random.choice(gates))

    if num_measurements > 0:
        gates_list += (["measure"] * num_measurements)

    for gate in random.sample(gates_list, len(gates_list)):

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
            c = random.randint(0, num_measurements - 1)
            qc.measure(q, c)
        else:
            q = random.randint(0, num_qubits - 1)
            getattr(qc, gate)(q)

    return qc
