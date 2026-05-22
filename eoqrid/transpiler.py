from __future__ import annotations
import numpy as np
import networkx as nx
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager, Target
from qiskit.transpiler.passes import BasisTranslator
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel
from qiskit.circuit.library import SwapGate

from eoqrid.exchange_interaction import ExchangeInteraction
from eoqrid.measurement import Measurement

class Transpiler:
    """
    Transpiler
    
    Attributes
    ----------
    topology : nx.Graph
        quantum chip topology

    """
    def __init__(self, topology: nx.Graph = None) -> None:
       """
       Parameters
       ----------
       topology : nx.Graph
           quantum chip topology

       Returns
       -------
       None
        
       """
       self._topology = topology

    @property
    def topology(self) -> nx.Graph:
        return self._topology

    @topology.setter
    def topology(self, value) -> None:
        self._topology = value

    def optimize(self, qc_native: QuantumCircuit, optimization_level: int = 0, seed: int | None = None) -> QuantumCircuit:
        """
        optimize the native quantum circuit.

        Parameters
        ----------
        qc_native : QuantumCircuit
            quantum circuits for native device.
        optimization_level : int
            optimization level.
        seed : int | None, default None
            seed of random generation.

        Returns
        -------
        qc_native : QuantumCircuit
            optimized quantum circuits for native device.
 
        """
        if qc_native.num_qubits != max(self._topology.nodes) + 1:
            raise ValueError("the number of nodes in the topology and the number of qubits do not match.")

        self._num_qubits = qc_native.num_qubits // 3
        self._num_dots = qc_native.num_qubits
        self._num_clbits = qc_native.num_clbits

        coupling_list = []
        for a, b in list(self._topology.edges()):
            coupling_list.append((a, b))
            coupling_list.append((b, a))
        
        target = Target(num_qubits=self._num_dots)
        target.add_instruction(ExchangeInteraction(1.0, 1.0),
                               {pair: None for pair in coupling_list})
        target.add_instruction(SwapGate(), {pair: None for pair in coupling_list})
         
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

        for i, inst in enumerate(qc_native):
            operation = inst.operation
            qubits = inst.qubits
            params = inst.params
            qid = [q._index for q in qubits]
        
            match operation.name:
                case 'ex':
                    if 'weight' in self._topology[qid[0]][qid[1]]:
                        J = self._topology[qid[0]][qid[1]]['weight']
                    else:
                        J = 1.0
                    t = params[0]
                    qc_native.data[i] = (ExchangeInteraction(t, J), [qid[0], qid[1]], [])
                case 'swap':
                    if 'weight' in self._topology[qid[0]][qid[1]]:
                        J = self._topology[qid[0]][qid[1]]['weight']
                    else:
                        J = 1.0
                    t = np.pi / J
                    qc_native.data[i] = (ExchangeInteraction(t, J), [qid[0], qid[1]], [])
                case _:
                    raise ValueError(f"{operation.name} is not supported.")

        return qc_native
        
    def run(self, qc: QuantumCircuit, optimization_level: int = 0, seed: int | None = None) -> list:
        """
        transpile the quantum circuit.

        Parameters
        ----------
        qc : QuantumCircuit
            quantum circuits.
        optimization_level : int, default 1
            optimization level.
        seed : int | None, default None
            seed of random generation.

        Returns
        -------
        qc_native : QuantumCircuit
            transpileed quantum circuits.
 
        """
        self._num_qubits = qc.num_qubits
        self._num_dots = qc.num_qubits * 3
        self._num_clbits = qc.num_clbits

        target_basis = ['rz', 'x', 'z', 'h', 'cx', 'swap']
        bt_pass = BasisTranslator(sel, target_basis)
        pm = PassManager(bt_pass)

        qc_native = QuantumCircuit(self._num_dots, self._num_clbits)
        for inst in pm.run(qc):
            operation = inst.operation
            qubits = inst.qubits
            clbits = inst.clbits
            params = inst.params
            qid = [q._index for q in qubits]
            cid = [c._index for c in clbits]

            #m_str = ""
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

        if 'measure' not in qc.count_ops():
            qc_native = self.optimize(qc_native, optimization_level, seed)

        return qc_native

    def _sw(self, a: int, b: int) -> QuantumCircuit:
        """
        SWAP gate to native quantum circuit.

        Parameters
        ----------
        a : int
            index of qubit.
        b : int
            index of qubit.
        
        Returns
        -------
        qc_native : QuantumCircuit
            native quantum circuits.
 
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
        Rz gate to native quantum circuit.

        Parameters
        ----------
        q : int
            index of qubit.
        phase : float
            phase of rotation.
        
        Returns
        -------
        qc_native : QuantumCircuit
            native quantum circuits.
 
        """
        a0, a1 = q * 3, q * 3 + 1
        exchange_integral = 1.0
        time = -phase
    
        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time, exchange_integral), [a0, a1])
        
        return qc_native
    
    def _z(self, q: int) -> QuantumCircuit:
        """
        Pauli-Z gate to native quantum circuit.

        Parameters
        ----------
        q : int
            index of qubit.
        
        Returns
        -------
        QuantumCircuit
            native quantum circuits.
 
        """
        return self._rz(q, phase=np.pi)
    
    def _x(self, q: int) -> QuantumCircuit:
        """
        Pauli-X gate to native quantum circuit.

        Parameters
        ----------
        q : int
            index of qubit.
        
        Returns
        -------
        qc_native : QuantumCircuit
            native quantum circuits.
 
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        theta = np.arccos(1.0 / 3.0)
        exchange_integral_01 = 1.0
        exchange_integral_12 = 1.0
        time_01 = -theta
        time_12 = -(np.pi - theta)

        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time_12, exchange_integral_12), [a1, a2])
        qc_native.append(ExchangeInteraction(time_01, exchange_integral_01), [a0, a1])
        qc_native.append(ExchangeInteraction(time_12, exchange_integral_12), [a1, a2])
        
        return qc_native
    
    def _h(self, q: int) -> QuantumCircuit:
        """
        Hadamard gate to native quantum circuit.

        Parameters
        ----------
        q : int
            index of qubit.
        
        Returns
        -------
        qc_native : QuantumCircuit
            native quantum circuits.
 
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        theta = np.arccos(1.0/3.0)
        exchange_integral_01 = 1.0
        exchange_integral_12 = 1.0
        time_01 = -(np.pi - theta) / 2.0
        time_12 = -(np.pi + theta)

        qc_native = QuantumCircuit(self._num_dots)
        qc_native.append(ExchangeInteraction(time_01, exchange_integral_01), [a0, a1])
        qc_native.append(ExchangeInteraction(time_12, exchange_integral_12), [a1, a2])
        qc_native.append(ExchangeInteraction(time_01, exchange_integral_01), [a0, a1])

        return qc_native
    
    def _cx(self, a: int, b: int) -> QuantumCircuit:
        """
        CNOT gate to native quantum circuit (Fong-Wandzura CNOT).

        Parameters
        ----------
        a : int
            index of qubit (control).
        b : int
            index of qubit (target).
        
        Returns
        -------
        qc_native : QuantumCircuit
            native quantum circuits.
 
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

    def _m(self, q, c) -> QuantumCircuit:
        """
        Measurement instruction to native quantum circuit.

        Parameters
        ----------
        q : int
            index of qubit.
        c : int
            index of clbit (classical bit).
        
        Returns
        -------
        qc_native : QuantumCircuit
            native quantum circuits.
 
        """
        a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
        qc_native = QuantumCircuit(self._num_dots, self._num_clbits)
        qc_native.append(Measurement(), [a0, a1, a2], [c])
        return qc_native
