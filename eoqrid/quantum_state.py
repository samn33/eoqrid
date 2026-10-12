from __future__ import annotations

import numpy as np
from qiskit.quantum_info import Statevector


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
    logical_qstate : np.ndarray
        NumPy array representing the logical quantum state vector.
    physical_qstate : np.ndarray
        NumPy array representing the physical quantum state vector.
    """
    def __init__(
            self,
            num_dots: int,
            index_layout: list[int] | None = None,
    ) -> None:
        """
        Initialize the quantum state.

        Parameters
        ----------
        num_dots : int
            Number of dots.
        """
        self._num_dots = num_dots
        self._num_qubits = num_dots // 3
        self._statevector = Statevector.from_label(f"{'0' * self._num_dots}")
        if index_layout is None:
            self._index_layout = list(range(self._num_dots))
        else:
            if len(index_layout) != self._num_dots:
                raise ValueError("Length of logical indices is not same as the number of dots.")
            if len(set(index_layout)) != len(index_layout):
                raise ValueError("There are duplicates in the index")
            self._index_layout = index_layout

    @property
    def num_dots(self) -> int:
        return self._num_dots

    @property
    def statevector(self) -> Statevector:
        return self._statevector

    @statevector.setter
    def statevector(self, value) -> None:
        self._statevector = value

    def _is_power_of_two(self, n: int) -> bool:
        return n > 0 and (n & (n - 1)) == 0

    def _reverse_bits(self, n: int, digits: int) -> int:
        b_str = f"{n:0{digits}b}"
        rev_str = b_str[::-1]
        return int(rev_str, 2)

    def _reverse_qargs(self, data: np.ndarray) -> np.ndarray:
        if not self._is_power_of_two(len(data)):
            raise ValueError("Length of data must be a power of two.")
        bit_length = (len(data) - 1).bit_length()
        data_out = np.zeros(len(data), dtype= complex)
        for i, d in enumerate(data):
            i_rev = self._reverse_bits(i, bit_length)
            data_out[i_rev] = d
        return data_out

    @property
    def index_layout(self) -> list:
        return self._index_layout
    
    @index_layout.setter
    def index_layout(self, index_layout) -> None:
        if len(index_layout) != self._num_dots:
            raise ValueError("Length of logical indices is not same as the number of dots.")
        if len(set(index_layout)) != len(index_layout):
            raise ValueError("There are duplicates in the index")
        self._index_layout = index_layout

    @property
    def logical_qstate(self) -> np.ndarray:
        if self._num_dots % 3 != 0:
            raise ValueError("Can't get a logical quantum state.")

        return self._logical_qstate()

    @property
    def physical_qstate(self) -> np.ndarray:
        return self._physical_qstate()

    @property
    def _base(self) -> list:
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
        base_element = [
            np.array(udu - uud) / np.sqrt(2.0), # logical |0>
            np.array(2.0 * duu - udu - uud) / np.sqrt(6.0) # logical |1>
        ]
        
        base = []
        for index in range(2 ** self._num_qubits):
            base_tmp = np.array([1.0], dtype=complex)
            for i in [int(x) for x in format(index, f'0{self._num_qubits}b')]:
                base_tmp = np.kron(base_element[i], base_tmp)
            base.append(base_tmp)
            
        return base
        
    def _logical_qstate(self) -> np.ndarray:
        """
        Get the logical quantum state vector.
    
        Returns
        -------
        np.ndarray
            NumPy array representing the logical quantum state vector.
        """
        statevector = Statevector(self.physical_qstate)
        return np.array([np.vdot(base, statevector.reverse_qargs().data) for base in self._base])

    def _physical_qstate(self) -> np.ndarray:
        """
        Get the physical quantum state vector.

        Returns
        -------
        np.ndarray
            NumPy array representing the physical quantum state vector.
        """
        data = np.zeros(2 ** self._num_dots, dtype=complex)
        for p_id in range(2 ** self._num_dots):
            b_str = f"{p_id:0{self._num_dots}b}"
            b_list = list(map(int, list(b_str)))[::-1]
            bb_list = [0] * self._num_dots
            l_id = 0
            for k in range(self._num_dots):
                bb_list[self._index_layout[k]] = b_list[k]
                if b_list[k] == 1:
                    l_id += (1 << self._index_layout[k])
            data[p_id] = self._statevector.data[l_id]

        return self._reverse_qargs(data)

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
        EPS = 1e-8

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
                print(f"c[{bits}] = {v.real:+.4f}{v.imag:+.4f}*i : {abs(v)**2:.4f} {bar_str}")

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
        qstate_data = self._reverse_qargs(self.physical_qstate)
        return 1.0 - abs(np.vdot(qstate_data, proj_qstate))
