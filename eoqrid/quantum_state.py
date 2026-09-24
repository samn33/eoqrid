from __future__ import annotations

import numpy as np
from qiskit.quantum_info import Statevector

EPS = 1e-8

class QuantumState:
    """
    Representation of a quantum state in exchange-only architecture.

    Attributes
    ----------
    num_qubits : int
        Number of logical qubits.
    num_dots : int
        Number of quantum dots (physical qubits).
    statevector : Statevector
        Qiskit Statevector object.
    data : np.ndarray
        NumPy array representing the state vector.
    qiskit_data : np.ndarray
        NumPy array representing the state vector in Qiskit qubit ordering.
    logical_qstate : np.ndarray
        NumPy array representing the logical quantum state vector.
    physical_qstate : np.ndarray
        NumPy array representing the physical quantum state vector.
    """
    def __init__(self, num_qubits: int) -> None:
        """
        Initialize the quantum state.

        Parameters
        ----------
        num_qubits : int
            Number of logical qubits.
        """
        self._num_qubits = num_qubits
        self._num_dots = num_qubits * 3

        # [qiskit order]
        # 3rd,2nd,1st -> pos of array        
        # 000 (uuu) -> 0
        # 001 (uud) -> 1
        # 010 (udu) -> 2
        # 011 (udd) -> 3
        # 100 (duu) -> 4
        # 101 (dud) -> 5
        # 110 (ddu) -> 6
        # 111 (ddd) -> 7

        udu = np.array([1.0 if i == 2 else 0.0 for i,e in enumerate([0]*8)])
        uud = np.array([1.0 if i == 1 else 0.0 for i,e in enumerate([0]*8)])
        duu = np.array([1.0 if i == 4 else 0.0 for i,e in enumerate([0]*8)])
        self._base_element = [
            np.array(udu - uud) / np.sqrt(2.0), # logical |0>
            np.array(2.0 * duu - udu - uud) / np.sqrt(6.0) # logical |1>
        ]

        self._base = []
        for index in range(2 ** self._num_qubits):
            base_tmp = np.array([1.0], dtype=complex)
            for i in [int(x) for x in format(index, f'0{self._num_qubits}b')]:
                base_tmp = np.kron(self._base_element[i], base_tmp)
            self._base.append(base_tmp)
        
        #self._statevector = Statevector(self._base[0])
        self._statevector = Statevector.from_label(f"{'0' * self._num_dots}")

    @property
    def num_qubits(self) -> int:
        return self._num_qubits

    @property
    def statevector(self) -> Statevector:
        return self._statevector

    @statevector.setter
    def statevector(self, value) -> None:
        self._statevector = value

    @property
    def data(self) -> np.ndarray:
        return self._data(qiskit_order=False)

    @property
    def logical_qstate(self) -> np.ndarray:
        return self._logical_qstate()

    @property
    def physical_qstate(self) -> np.ndarray:
        return self._physical_qstate()

    @property
    def qiskit_data(self) -> np.ndarray:
        return self._data(qiskit_order=True)

    def _data(self, qiskit_order: bool = False) -> np.ndarray:
        if qiskit_order is True:
            return self._statevector.data
        else:
            return self._statevector.reverse_qargs().data

    def _logical_qstate(self) -> np.ndarray:
        """
        Get the logical quantum state vector.

        Returns
        -------
        np.ndarray
            NumPy array representing the logical quantum state vector.
        """
        return np.array([np.vdot(base, self._statevector.data) for base in self._base])

    def _physical_qstate(self) -> np.ndarray:
        """
        Get the physical quantum state vector.

        Returns
        -------
        np.ndarray
            NumPy array representing the physical quantum state vector.
        """
        return self._statevector.reverse_qargs().data

    def draw(self, ignore_zeros=False, preal=0, mode: str = "logical") -> None:
        """
        Draw the quantum state components.

        Prints the elements of the state vector along with their probabilities.

        Parameters
        ----------
        ignore_zeros : bool, default False
            If True, prints only non-zero amplitudes.
        preal : int, default 0
            State index used to make its amplitude a positive real number.
            If -1, the global phase factor is not adjusted.
        mode : {'logical', 'physical'}, default 'logical'
            Quantum state representation mode to draw.

        Examples
        --------
        >>> qstate.draw()
        c[00] = +0.7071+0.0000*i : 0.5000 |++++++
        c[01] = +0.0000+0.0000*i : 0.0000 |
        c[10] = +0.0000+0.0000*i : 0.0000 |
        c[11] = +0.7071+0.0000*i : 0.5000 |++++++
        ...
        >>> qstate.draw(ignore_zeros=True)
        c[00] = +0.7071+0.0000*i : 0.5000 |++++++
        c[11] = +0.7071+0.0000*i : 0.5000 |++++++
        """
        if mode == "logical":
            vec = self.logical_qstate
            digits = self._num_qubits
        elif mode == "physical":
            vec = self.physical_qstate
            digits = self._num_dots

        if preal >= 0:
            exp_i_phase = 1.+0.j
            if abs(vec[preal].imag) > EPS:
                exp_i_phase = vec[preal] / abs(vec[preal])
            elif vec[preal].real < 0.0:
                exp_i_phase = -exp_i_phase
            vec = vec / exp_i_phase

        for i, v in enumerate(vec):
            bits = "{:0{digits}b}".format(i, digits=digits)
            absval2 = abs(v) * abs(v)
            if absval2 < EPS:
                bar_len = 0
            else:
                bar_len = int(absval2 / 0.1 + 1.5)
            bar_str = "|" + "+" * bar_len
            if ignore_zeros is True and absval2 < EPS:
                continue
            else:
                print(f"c[{bits}] = {v.real:+.4f}{v.imag:+.4f}*i : {abs(v)**2:.4f} {bar_str}"
                      )

    def leakage(self) -> float:
        """
        Get the leakage of the quantum state.

        Returns
        -------
        float
            Leakage of the quantum state.
        """
        proj_qstate = np.zeros(len(self.physical_qstate), dtype=complex)
        for i, b in enumerate(self._base):
            proj_qstate = proj_qstate + (self.logical_qstate[i] * b) # qiskit_order

        proj_qstate = proj_qstate / np.linalg.norm(proj_qstate)

        qstate_data = self.qiskit_data / np.linalg.norm(self.qiskit_data)
        return 1.0 - abs(np.vdot(qstate_data, proj_qstate))
