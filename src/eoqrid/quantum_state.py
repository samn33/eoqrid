from __future__ import annotations

import copy
import warnings

import numpy as np
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace, purity

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
    density_matrix : DensityMatrix
        Qiskit DensityMatrix object.
    logical_sv_data : np.ndarray
        NumPy array representing the logical quantum state vector.
    physical_sv_data : np.ndarray
        NumPy array representing the physical quantum state vector.
    physical_rho_data : np.ndarray
        NumPy array representing the physical density matrix.
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
        self._density_matrix = DensityMatrix(self._statevector)
        if index_layout is None:
            self._index_layout = list(range(self._num_dots))
        else:
            if len(index_layout) != self._num_dots:
                raise ValueError("Length of logical indices is not same as the number of dots.")
            if len(set(index_layout)) != len(index_layout):
                raise ValueError("There are duplicates in the index")
            self._index_layout = index_layout

    def __str__(self) -> str:
        s = ""
        s += "State Vector:\n"
        s += f"{self._statevector.reverse_qargs().data}\n"
        s += "Density Matrix:\n"
        s += f"{self._density_matrix.reverse_qargs().data}"
        return s
        
    @property
    def num_dots(self) -> int:
        return self._num_dots

    @num_dots.setter
    def num_dots(self, value) -> None:
        self._num_dots = value

    @property
    def num_qubits(self) -> int:
        return self._num_qubits

    @num_qubits.setter
    def num_qubits(self, value) -> None:
        self._num_qubits = value

    @property
    def statevector(self) -> Statevector:
        return self._statevector

    @property
    def density_matrix(self) -> DensityMatrix:
        return self._density_matrix

    @statevector.setter
    def statevector(self, value) -> None:
        if not isinstance(value, Statevector):
            raise TypeError("statevector must be Statevector object.")
        self._statevector = value
        self._density_matrix = DensityMatrix(value)

    @density_matrix.setter
    def density_matrix(self, value) -> None:
        if not isinstance(value, DensityMatrix):
            raise TypeError("density_matrix must be DensityMatrix object.")
        self._density_matrix = value

        p = purity(self._density_matrix)
        if abs(p.real - 1.0) > EPS:
            self._statevector = None
        eigenvalues, eigenvectors = np.linalg.eigh(self._density_matrix.data)
        pure_vector = eigenvectors[:, np.argmax(eigenvalues)]
        self._statevector = Statevector(pure_vector)

    def _is_power_of_two(self, n: int) -> bool:
        return n > 0 and (n & (n - 1)) == 0

    def _reverse_bits(self, n: int, digits: int) -> int:
        b_str = f"{n:0{digits}b}"
        rev_str = b_str[::-1]
        return int(rev_str, 2)

    def _reverse_qargs_1d(self, data: np.ndarray) -> np.ndarray:
        if not self._is_power_of_two(len(data)):
            raise ValueError("Length of data must be a power of two.")
        bit_length = (len(data) - 1).bit_length()
        data_out = np.zeros(len(data), dtype= complex)
        for i, d in enumerate(data):
            i_rev = self._reverse_bits(i, bit_length)
            data_out[i_rev] = d
        return data_out

    def _reverse_qargs_2d(self, data: np.ndarray) -> np.ndarray:
        n_row, n_col = data.shape
        if not self._is_power_of_two(n_row):
            raise ValueError("Row of data must be a power of two.")
        if not self._is_power_of_two(n_col):
            raise ValueError("Column of data must be a power of two.")
        if n_row != n_col:
            raise ValueError("Row and column must be same size.")

        bit_length = (n_row - 1).bit_length()
        data_out = np.zeros((n_row, n_col), dtype= complex)
        for i, row in enumerate(data):
            i_rev = self._reverse_bits(i, bit_length)
            for j, d in enumerate(row):
                j_rev = self._reverse_bits(j, bit_length)
                data_out[i_rev][j_rev] = d
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
    def physical_qstate(self) -> np.ndarray:
        warnings.warn(
            "physical_qstate is deprecated and will be removed in a future version. Please use physical_sv_data instead.",
            DeprecationWarning,
            stacklevel = 2,
        )
        return self._physical_sv_data()

    @property
    def physical_sv_data(self) -> np.ndarray:
        return self._physical_sv_data()

    @property
    def logical_qstate(self) -> np.ndarray:
        warnings.warn(
            "logical_qstate is deprecated and will be removed in a future version. Please use logical_sv_data instead.",
            DeprecationWarning,
            stacklevel = 2,
        )
        if self._num_dots % 3 != 0:
            raise ValueError("Can't get a logical quantum state.")
        return self._logical_sv_data()

    @property
    def logical_sv_data(self) -> np.ndarray:
        if self._num_dots % 3 != 0:
            raise ValueError("Can't get a logical quantum state.")
        return self._logical_sv_data()

    @property
    def physical_rho_data(self) -> np.ndarray:
        return self._physical_rho_data()

    @property
    def logical_rho_data(self) -> np.ndarray:
        if self._num_dots % 3 != 0:
            raise ValueError("Can't get a logical quantum state.")
        return self._logical_rho_data()

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

    def purity(self) -> float:
        return purity(self._density_matrix).real

    def is_pure(self) -> bool:
        return not self.is_mixed()
    
    def is_mixed(self) -> bool:
        p = self.purity()
        return abs(p - 1.0) > EPS

    def _physical_sv_data(self) -> np.ndarray:
        """
        Get the physical quantum state vector.

        Returns
        -------
        np.ndarray
            NumPy array representing the physical quantum state vector.
        """
        sv = self.statevector
        data = np.zeros(2 ** self._num_dots, dtype=complex)
        for l_id in range(2 ** self._num_dots):
            b_str = f"{l_id:0{self._num_dots}b}"
            b_list = list(map(int, list(b_str)))[::-1]
            bb_list = [0] * self._num_dots
            p_id = 0
            for k in range(self._num_dots):
                bb_list[self._index_layout[k]] = b_list[k]
                if b_list[k] == 1:
                    p_id += (1 << self._index_layout[k])
            data[l_id] = sv.data[p_id]

        return self._reverse_qargs_1d(data)

    def _logical_sv_data(self) -> np.ndarray:
        """
        Get the logical quantum state vector.
    
        Returns
        -------
        np.ndarray
            NumPy array representing the logical quantum state vector.
        """
        statevector = Statevector(self.physical_sv_data)
        return np.array([np.vdot(base, statevector.reverse_qargs().data) for base in self._base])

    def _physical_rho_data(self) -> np.ndarray:
        """
        Get the physical density matrix.

        Returns
        -------
        np.ndarray
            NumPy array representing the physical density matrix.
        """
        rho = self.density_matrix

        data = np.zeros((2 ** self._num_dots, 2 ** self._num_dots), dtype=complex)
        for row_l_id in range(2 ** self._num_dots):
            b_str = f"{row_l_id:0{self._num_dots}b}"
            b_list = list(map(int, list(b_str)))[::-1]
            bb_list = [0] * self._num_dots
            row_p_id = 0
            for k in range(self._num_dots):
                bb_list[self._index_layout[k]] = b_list[k]
                if b_list[k] == 1:
                    row_p_id += (1 << self._index_layout[k])

            for col_l_id in range(2 ** self._num_dots):
                b_str = f"{col_l_id:0{self._num_dots}b}"
                b_list = list(map(int, list(b_str)))[::-1]
                bb_list = [0] * self._num_dots
                col_p_id = 0
                for k in range(self._num_dots):
                    bb_list[self._index_layout[k]] = b_list[k]
                    if b_list[k] == 1:
                        col_p_id += (1 << self._index_layout[k])

                data[row_l_id][col_l_id] = rho.data[row_p_id][col_p_id]

        return self._reverse_qargs_2d(data)

    def _logical_rho_data(self) -> np.ndarray:
        """
        Get the logical density matrix.
    
        Returns
        -------
        np.ndarray
            NumPy array representing the logical density matrix.
        """
        data = self.physical_rho_data
        base_mat = np.array([v for v in self._base])
        return base_mat.conj() @ data @ base_mat.T

    def _draw_pure_state(self, ignore_zeros=False, preal=0, mode: str = "logical") -> None:
        """
        Draw the pure quantum state as a vector.

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
            vec = self.logical_sv_data
            digits = self._num_qubits
        elif mode == "physical":
            vec = self.physical_sv_data
            digits = self._num_dots
        else:
            raise ValueError("The mode must be phyisical or logical.")

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

    def _draw_mixed_state(self, ignore_zeros=False, mode: str = "logical") -> None:
        """
        Draw the mixed quantum state as a matrix.

        Prints the elements of the state vector along with their probabilities.

        Parameters
        ----------
        ignore_zeros : bool, default False
            If True, prints only non-zero amplitudes.
        preal : int, default 0
            State index used to make its amplitude a positive real number.
            If -1, the global phase factor is not adjusted.
        """
        if mode == "logical":
            mat = self.logical_rho_data
            digits = self._num_qubits
        elif mode == "physical":
            mat = self.physical_rho_data
            digits = self._num_dots
        else:
            raise ValueError("The mode must be phyisical or logical.")

        for i, line in enumerate(mat):
            bits_i = "{:0{digits}b}".format(i, digits=digits)
            for j, c in enumerate(line):
                bits_j = "{:0{digits}b}".format(j, digits=digits)
                absval2 = abs(c) * abs(c)
                if absval2 < EPS:
                    bar_len = 0
                else:
                    bar_len = int(absval2 / 0.1 + 1.5)
                bar_str = "|" + "+" * bar_len
                if ignore_zeros is True and absval2 < EPS:
                    continue
                else:
                    print(f"c[{bits_i}][{bits_j}] = {c.real:+.4f}{c.imag:+.4f}*i : {abs(c)**2:.4f} {bar_str}")

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
        """
        if self.is_mixed():
            self._draw_mixed_state(ignore_zeros)
        else:
            self._draw_pure_state(ignore_zeros, preal, mode)

    def leakage(self) -> float:
        """
        Get the leakage of the quantum state.
    
        Returns
        -------
        float
            Leakage of the quantum state.
        """
        proj_sv_data = np.zeros(len(self.physical_sv_data), dtype=complex)
        for i, b in enumerate(self._base):
            proj_sv_data = proj_sv_data + (self.logical_sv_data[i] * b) # qiskit_order
    
        proj_sv_data = proj_sv_data / np.linalg.norm(proj_sv_data)
        qstate_data = self._reverse_qargs_1d(self.physical_sv_data)
        return 1.0 - abs(np.vdot(qstate_data, proj_sv_data))

    def _sqrt_hermitian_matrix(self, mat, tol: float = 1e-12):
        eigenvalues, eigenvectors = np.linalg.eigh(mat)
        eigenvalues = np.where(eigenvalues < tol, 0, eigenvalues)
        sqrt_diag = np.sqrt(eigenvalues)

        return eigenvectors @ np.diag(sqrt_diag) @ eigenvectors.conj().T
        
    def _fidelity_for_pure_state(self, other: QuantumState, mode: str) -> float:
        """ fidelity for self(pure state) and other(pure state) """
        if mode == "physical":
            fid = (
                np.abs(np.vdot(self.physical_sv_data, other.physical_sv_data))
                / (np.linalg.norm(self.physical_sv_data)
                   * np.linalg.norm(other.physical_sv_data))
            )
        elif mode == "logical":
            fid = (
                np.abs(np.vdot(self.logical_sv_data, other.logical_sv_data))
                / (np.linalg.norm(self.logical_sv_data)
                   * np.linalg.norm(other.logical_sv_data))
            )
        else:
            raise ValueError("The mode must be phyisical or logical.")
        return fid

    def _fidelity_for_mixed_state(self, other: QuantumState, mode: str) -> float:
        """ fidelity for self(mixed state) and other(mixed state) """
        if mode == "physical":
            self_rho = self.physical_rho_data
            other_rho = other.physical_rho_data
        elif mode == "logical":
            self_rho = self.logical_rho_data
            other_rho = other.logical_rho_data
        else:
            raise ValueError("The mode must be phyisical or logical.")
        
        sqrt_other_rho = self._sqrt_hermitian_matrix(other_rho)
        mat = self._sqrt_hermitian_matrix(
            sqrt_other_rho @ self_rho @ sqrt_other_rho
        )
        fid = np.real(np.trace(mat)) ** 2
        return fid

    def fidelity(self, other: QuantumState, mode: str = "logical") -> float:
        """
        Get the fidelity with other quantum state.
    
        Parameters
        ----------
        other : QuantumState
            Other quantum state.
        mode : {'logical', 'physical'}, default 'logical'
            Quantum state representation mode to calculate fidelity.

        Returns
        -------
        float
            Fidelity with other quantum state.
        """
        if self.is_pure() and other.is_pure():
            fid = self._fidelity_for_pure_state(other, mode)
        else:
            fid = self._fidelity_for_mixed_state(other, mode)
        return fid

    def partial_trace(self, indices: list[int]) -> QuantumState:
        """
        Get the partial quantum state by parcial trace.
    
        Parameters
        ----------
        indices : list[int]
            Physical qubit indices to traced out.

        Returns
        -------
        QuantumState
            Partial quantum state.
        """
        qs = copy.deepcopy(self)
        rho = partial_trace(self._density_matrix, [self._index_layout[i] for i in indices]) 
        qs.density_matrix = rho
        qs.num_dots = len(self._index_layout) - len(indices)
        qs.num_qubits = qs._num_dots // 3

        index_layout = [index for i, index in enumerate(self._index_layout) if i not in indices]
        trace_out = [self._index_layout[i] for i in indices]
        for t in sorted(trace_out, reverse=True):
            for i in range(qs.num_dots):
                if index_layout[i] >= t:
                    index_layout[i] -= 1
        qs.index_layout = index_layout

        return qs
