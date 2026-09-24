from __future__ import annotations

import copy
import itertools
from collections import deque

import networkx as nx
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel
from qiskit.circuit.library import Reset, SwapGate
from qiskit.transpiler import PassManager, Target
from qiskit.transpiler.passes import BasisTranslator

from eoqrid.dot_architecture import DotArchitecture
from eoqrid.exchange_interaction import ExchangeInteraction
from eoqrid.measurement import Measurement
from eoqrid.physical_quantum_circuit import PhysicalQuantumCircuit
from eoqrid.singlet import Singlet

EPS = 1e-8

class EoqTranspiler:
    """
    Transpiler for exchange-only quantum computing.
    
    Attributes
    ----------
    arch : DotArchitecture
        Quantum dot architecture layout.
    """
    def __init__(self, arch: DotArchitecture) -> None:
        """
        Initialize the exchange-only quantum computing simulator.
       
        Parameters
        ----------
        arch : DotArchitecture
            Quantum dot architecture.
        """
        self._arch = arch

    @property
    def arch(self) -> DotArchitecture:
        return self._arch

    def _qc_is_logical(self, qc: QuantumCircuit) -> bool:
        """
        Check whether a quantum circuit is logical.

        Parameters
        ----------
        qc : QuantumCircuit
            Quantum circuit to check.

        Returns
        -------
        bool
            True if the quantum circuit is logical, False otherwise.
        """
        for name in qc.count_ops():
            if name == 'ex' or name == 'm' or name == 'sin' or name == 'reset':
                return False
        return True
        
    def _decompose(self, qc: QuantumCircuit) -> QuantumCircuit:
        """
        Decompose a logical quantum circuit into elementary gates.

        Parameters
        ----------
        qc : QuantumCircuit
            Logical quantum circuit to decompose.

        Returns
        -------
        QuantumCircuit
            Decomposed logical quantum circuit.
        """
        self._num_qubits = qc.num_qubits
        self._num_dots = qc.num_qubits * 3
        self._num_clbits = qc.num_clbits

        target_basis = ['rz', 'x', 'z', 'h', 'cx', 'swap']
        bt_pass = BasisTranslator(sel, target_basis)
        pm = PassManager(bt_pass)

        qc_native = QuantumCircuit(self._num_dots, self._num_clbits)

        for q in range(self._num_qubits):
            qc_native = qc_native.compose(self._singlet(q))
        
        for inst in pm.run(qc):
            operation = inst.operation
            qubits = inst.qubits
            clbits = inst.clbits
            params = inst.params
            qid = [q._index for q in qubits]
            cid = [c._index for c in clbits]

            match operation.name:
                case 'rz':
                    phase = params[0]
                    qc_native = qc_native.compose(self._rz(qid[0], phase=phase))
                case 'x':
                    qc_native = qc_native.compose(self._x(qid[0]))
                case 'z':
                    qc_native = qc_native.compose(self._z(qid[0]))
                case 'h':
                    qc_native = qc_native.compose(self._h(qid[0]))
                case 'cx':
                    qc_native = qc_native.compose(self._cx(qid[0], qid[1]))
                case 'swap':
                    qc_native = qc_native.compose(self._sw(qid[0], qid[1]))
                case 'measure':
                    qc_native = qc_native.compose(self._m(qid[0], cid[0]))
                case _:
                    raise ValueError(f"{operation.name} is not supported.")

        return qc_native

    def _find_swaps(self, graph: nx.Graph, start_pair: tuple, goal_pair: tuple):
        """
        Find the shortest procedure to move an adjacent pair (u, v) to the destination pair
        with the minimum number of swaps on the NetworkX graph object (BFS)
    
        """
        start_state = tuple(start_pair)
        goal_state = tuple(goal_pair)

        if start_state == goal_state:
            return []

        visited = {start_state: None}
        queue = deque([start_state])

        while queue:
            u_curr, v_curr = queue.popleft()
            next_states = []

            # direct swap (inversion)
            next_states.append((v_curr, u_curr))

            # move u to adjacent node
            for nbr in graph.neighbors(u_curr):
                if nbr != v_curr:
                    next_states.append((nbr, v_curr))

            # move v to adjacent node
            for nbr in graph.neighbors(v_curr):
                if nbr != u_curr:
                    next_states.append((u_curr, nbr))

            # search/update using BFS
            for next_st in next_states:
                if next_st == goal_state:
                    visited[next_st] = (u_curr, v_curr)
                    path = []
                    curr = goal_state
                    while curr is not None:
                        path.append(curr)
                        curr = visited[curr]
                    swaps = []
                    for state_now, state_next in itertools.pairwise(path):
                        if state_now[0] != state_next[0] and state_now[1] == state_next[1]:
                            swaps.append((state_next[0], state_now[0]))
                        elif state_now[0] == state_next[0] and state_now[1] != state_next[1]:
                            swaps.append((state_next[1], state_now[1]))
                        elif state_now[0] == state_next[1] and state_now[1] == state_next[0]:
                            swaps.append((state_next[0], state_now[0]))
                        else:
                            raise ValueError("some error has occured.")

                    return swaps[::-1]

                if next_st not in visited:
                    visited[next_st] = (u_curr, v_curr)
                    queue.append(next_st)

        return None

    def _find_minimum_swaps(self, pair: tuple[int, int]) -> list[tuple[int, int]]:

        swaps_min = None
        for i, readout_pair in enumerate(self._arch._readout_pairs):
            swaps = self._find_swaps(self._arch.topology, pair, readout_pair)
            swapslen_min = len(swaps)
            if swaps is None:
                continue
            if i == 0 or len(swaps) < swapslen_min:
                swapslen_min = len(swaps)
                swaps_min = swaps
                readout_pair_min = readout_pair
            else:
                continue

        if swaps_min is None:
            raise ValueError("routing not found.")

        return swaps_min, readout_pair_min

    def _optimize(
            self,
            qc_native_in: QuantumCircuit,
            optimization_level: int = 0,
            seed: int | None = None
    ) -> QuantumCircuit:
        """
        Optimize a native quantum circuit.

        Parameters
        ----------
        qc_native_in : QuantumCircuit
            Input native quantum circuit to optimize.
        optimization_level : int, default 0
            Optimization level (0, 1, 2, or 3).
        seed : int or None, default None
            Random seed.

        Returns
        -------
        QuantumCircuit
            Optimized native quantum circuit.
        """
        qc_native = qc_native_in.copy()
        if qc_native.num_qubits > max(self._arch.topology.nodes) + 1:
            raise ValueError("the number of nodes in the topology and the number of qubits do not match.")

        self._num_qubits = qc_native.num_qubits // 3
        self._num_dots = qc_native.num_qubits
        self._num_clbits = qc_native.num_clbits

        coupling_list = []
        for a, b in list(self._arch.topology.edges()):
            coupling_list.append((a, b))
            coupling_list.append((b, a))
        
        target = Target(num_qubits=self._num_dots)
        ex_properties = {(a, b): None for (a, b) in coupling_list} | {(b, a): None for (a, b) in coupling_list}
        m_properties = ex_properties
        ini_properties = ex_properties

        target.add_instruction(ExchangeInteraction(1.0, 1.0), properties=ex_properties)
        target.add_instruction(SwapGate(), properties=ex_properties)
        target.add_instruction(Measurement(), properties=m_properties)
        target.add_instruction(Singlet(), properties=ini_properties)
        target.add_instruction(Reset())
         
        initial_layout = list(range(self._num_dots))
        if seed is not None:
            qc_native = transpile(
                qc_native,
                target = target,
                optimization_level = optimization_level,
                initial_layout = initial_layout,
                seed_transpiler = seed,
            )
        else:
            qc_native = transpile(
                qc_native,
                target = target,
                optimization_level = optimization_level,
                initial_layout = initial_layout,
            )

        qc_native_out = QuantumCircuit(qc_native.num_qubits, qc_native.num_clbits)
        qc_native_out._layout = copy.deepcopy(qc_native.layout)

        for i, inst in enumerate(qc_native):
            operation = inst.operation
            qubits = inst.qubits
            clbits = inst.clbits
            params = inst.params
            qid = [q._index for q in qubits]
            cid = [c._index for c in clbits]

            # translate swap to exchange interaction
            match operation.name:
                case 'swap':
                    qc_native_out.append(ExchangeInteraction(np.pi, 1.0), [qid[0], qid[1]], [])
                case 'ex':
                    qc_native_out.append(ExchangeInteraction(params[0], params[1]), [qid[0], qid[1]], [])
                case 'sin':
                    qc_native_out.append(Singlet(), [qid[0], qid[1]])
                case 'reset':
                    qc_native_out.append(Reset(), [qid[0]])
                case 'm':
                    swaps, readout_pair = self._find_minimum_swaps(tuple(qid))
                    for a, b in swaps:
                        qc_native_out.append(ExchangeInteraction(np.pi, 1.0), [a, b], [])
                    qc_native_out.append(Measurement(), [readout_pair[0], readout_pair[1]], [cid[0]])
                    for a, b in reversed(swaps):
                        qc_native_out.append(ExchangeInteraction(np.pi, 1.0), [a, b], [])
                case _:
                    raise ValueError(f"{operation.name} is not supported.")

        return qc_native_out
        
    def transpile(
            self,
            qc: QuantumCircuit,
            optimization_level: int = 0,
            seed: int | None = None
    ) -> PhysicalQuantumCircuit:
        """
        Transpile a logical quantum circuit.

        Parameters
        ----------
        qc : QuantumCircuit
            Logical quantum circuit.
        optimization_level : int, default 0
            Optimization level (0, 1, 2, or 3).
        seed : int or None, default None
            Random seed.

        Returns
        -------
        PhysicalQuantumCircuit
            Transpiled physical quantum circuit.
        """
        if not isinstance(qc, QuantumCircuit):
            raise TypeError("the qc must be a QuantumCircuit object.")
        if not self._qc_is_logical(qc):
            raise ValueError("the qc must be logical.")
        if optimization_level not in (0, 1, 2, 3):
            raise ValueError("the optimization_level must be 0, 1, 2, or 3.")

        qc_native = self._decompose(qc)
        qc_native = self._optimize(qc_native, optimization_level, seed)

        return PhysicalQuantumCircuit(qc_native)

    def _sw(self, a: int, b: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for a SWAP gate.

        Parameters
        ----------
        a : int
            Index of the first qubit.
        b : int
            Index of the second qubit.

        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the SWAP gate.
        """
        (a0, a1, a2) = (a * 3, a * 3 + 1, a * 3 + 2)
        (b0, b1, b2) = (b * 3, b * 3 + 1, b * 3 + 2)

        exchange_integral_0 = 1.0
        exchange_integral_1 = 1.0
        exchange_integral_2 = 1.0
        time_0 = np.pi / exchange_integral_0
        time_1 = np.pi / exchange_integral_1
        time_2 = np.pi / exchange_integral_2

        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time_0, exchange_integral_0), [a0, b0])
        qc_native.append(ExchangeInteraction(time_1, exchange_integral_1), [a1, b1])
        qc_native.append(ExchangeInteraction(time_2, exchange_integral_2), [a2, b2])

        return qc_native
    
    def _rz(self, q: int, phase: float = 0.0) -> QuantumCircuit:
        """
        Generate a native quantum circuit for an Rz gate.

        Parameters
        ----------
        q : int
            Index of the qubit.
        phase : float, default 0.0
            Rotation phase in radians.

        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the Rz gate.
        """
        a0, a1 = q * 3, q * 3 + 1
        exchange_integral = 1.0
        time = -phase

        if abs(time % (2.0 * np.pi)) <= EPS:
            return QuantumCircuit(self._num_dots)
        elif time > 0.0:
            time = time - (time // (2.0 * np.pi)) * (2.0 * np.pi)
        elif time < 0.0:
            time = -time
            time = time - (time // (2.0 * np.pi)) * (2.0 * np.pi)
            time = 2.0 * np.pi - time

        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time, exchange_integral), [a0, a1])
        
        return qc_native
    
    def _z(self, q: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for a Pauli-Z gate.

        Parameters
        ----------
        q : int
            Index of the qubit.
        
        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the Pauli-Z gate.
        """
        return self._rz(q, phase=np.pi)
    
    def _x(self, q: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for a Pauli-X gate.

        Parameters
        ----------
        q : int
            Index of the qubit.
        
        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the Pauli-X gate.
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        theta = np.arccos(1.0 / 3.0)
        exchange_integral_01 = 1.0
        exchange_integral_12 = 1.0
        time_01 = 2.0 * np.pi - theta
        time_12 = np.pi + theta

        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time_12, exchange_integral_12), [a1, a2])
        qc_native.append(ExchangeInteraction(time_01, exchange_integral_01), [a0, a1])
        qc_native.append(ExchangeInteraction(time_12, exchange_integral_12), [a1, a2])
        
        return qc_native
    
    def _h(self, q: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for a Hadamard gate.

        Parameters
        ----------
        q : int
            Index of the qubit.
        
        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the Hadamard gate.
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        theta = np.arccos(1.0/3.0)
        exchange_integral_01 = 1.0
        exchange_integral_12 = 1.0

        time_01 = (3.0 * np.pi + theta) / 2.0
        time_12 = np.pi - theta

        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time_01, exchange_integral_01), [a0, a1])
        qc_native.append(ExchangeInteraction(time_12, exchange_integral_12), [a1, a2])
        qc_native.append(ExchangeInteraction(time_01, exchange_integral_01), [a0, a1])

        return qc_native
    
    def _cx(self, a: int, b: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for a CNOT gate.

        Parameters
        ----------
        a : int
            Index of the control qubit.
        b : int
            Index of the target qubit.

        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the CNOT gate.
        """
        (a6, a5, a4) = (a * 3, a * 3 + 1, a * 3 + 2)
        (a1, a2, a3) = (b * 3, b * 3 + 1, b * 3 + 2)

        phase_1 = np.arccos(1.0 / np.sqrt(3.0))
        phase_2 = np.arccos(2.0 * np.sqrt(2.0) / 3.0)
        phase_3 = np.arccos(-2.0 * np.sqrt(2.0) / 3.0)
        phase_4 = np.arccos(1.0 / np.sqrt(3.0))
        
        qc_native = QuantumCircuit(self._num_dots)

        qc_native.append(ExchangeInteraction(2.0 * np.pi - phase_1, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a5, a4])
        qc_native.append(ExchangeInteraction(phase_2, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a6, a5])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a4, a3])
        qc_native.append(ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a4, a3])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a5, a4])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a4, a3])
        qc_native.append(ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a5, a4])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a4, a3])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a5, a4])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(np.pi / 2.0, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a4, a3])
        qc_native.append(ExchangeInteraction(3.0 * np.pi / 2.0, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a4, a3])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a2, a1])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a6, a5])
        qc_native.append(ExchangeInteraction(phase_3, 1.0), [a3, a2])
        qc_native.append(ExchangeInteraction(np.pi, 1.0), [a5, a4])
        qc_native.append(ExchangeInteraction(phase_4, 1.0), [a2, a1])

        return qc_native

    def _m(self, q: int, c: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for a Measurement instruction.

        Parameters
        ----------
        q : int
            Index of the qubit.
        c : int
            Index of the classical bit.
        
        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing the Measurement instruction.
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        qc_native = QuantumCircuit(self._num_dots, self._num_clbits)
        qc_native.append(Measurement(), [a0, a1], [c])
        qc_native.append(Singlet(), [a0, a1])
        qc_native.append(Reset(), [a2])
        return qc_native

    def _singlet(self, q: int) -> QuantumCircuit:
        """
        Generate a native quantum circuit for preparing a singlet state.

        Parameters
        ----------
        q : int
            Index of the qubit.

        Returns
        -------
        QuantumCircuit
            Native quantum circuit implementing singlet state preparation.
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        qc_native = QuantumCircuit(self._num_dots, self._num_clbits)
        qc_native.append(Singlet(), [a0, a1])
        qc_native.append(Reset(), [a2])
        return qc_native
