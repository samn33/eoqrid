from __future__ import annotations
import numpy as np
from qiskit.quantum_info import Statevector

EPS = 1e-8

class QuantumState:
    """
    Quantum State

    Attributes
    ----------
    num_qubits : int
        number of quantum bits (logical qubits).
    num_dots : int
        number of quantum dots (physical qubits).
    statevector : Statevector
        qiskit Statevector object.
    data : np.ndarray
        numpy array of state vector.
    qiskit_data : np.ndarray
        numpy array of state vector (qiskit bit order).
    logical_qstate : np.ndarray
        numpy array of logical quantum state vector.
    physical_qstate : np.ndarray
        numpy array of physical quantum state vector.
    
    """
    def __init__(self, num_qubits: int) -> None:
        """
        Parameters
        ----------
        num_qubits : int
            number of quantum bits (logical qubits).

        Returns
        -------
        None
        
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
        
        self._statevector = Statevector(self._base[0])

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
        get the logical state.

        Parameters
        ----------
        None

        Returns
        -------
        np.ndarray
            numpy array of logical quantum state vector.

        """
        return np.array([np.vdot(base, self._statevector.data) for base in self._base])

    def _physical_qstate(self) -> np.ndarray:
        """
        get the physical state.

        Parameters
        ----------
        None

        Returns
        -------
        np.ndarray
            numpy array of physical quantum state vector.

        """
        return self._statevector.reverse_qargs().data

    def draw(self, ignore_zeros=False, preal=0, mode: str = "logical") -> None:
        """
        draw the quantum state
        (elements of the state vector and probabilities).
        
        Parameters
        ----------
        ignore_zeros : bool, default False
            if True, only non-zero amplitudes are printed.
        preal : int, default 0
            state id to make positive real amplitude.
            (if -1 is set, do not go out the global phase factor)
        mode : str
            logical or physical.
        
        Returns
        -------
        None
    
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
                print("c[{}] = {:+.4f}{:+.4f}*i : {:.4f} {}"
                      .format(bits, v.real, v.imag, abs(v)**2, bar_str))

    def leakage(self) -> float:
        """
        get the leakage for the quantum state.

        Parameters
        ----------
        None

        Returns
        -------
        float
            leakage

        """
        proj_qstate = np.zeros(len(self.physical_qstate), dtype=complex)
        for i, b in enumerate(self._base):
            proj_qstate = proj_qstate + (self.logical_qstate[i] * b) # qiskit_order

        return 1.0 - abs(np.vdot(self.qiskit_data, proj_qstate))
