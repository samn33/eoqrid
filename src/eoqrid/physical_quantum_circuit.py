from __future__ import annotations

from qiskit import QuantumCircuit

from eoqrid.reset_singlet import ResetSinglet
from eoqrid.reset_up import ResetUp


class PhysicalQuantumCircuit:
    """
    Physical quantum circuit in exchange-only architecture.

    Attributes
    ----------
    num_dots : int
        Number of quantum dots.
    num_clbits : int
        Number of classical bits.
    qc : QuantumCircuit
        Physical quantum circuit object.
    index_layout : list[int]
        List representing the mapping of quantum circuit register to quantum dot.
    """
    def __init__(
            self,
            num_dots: int = 1,
            num_clbits: int = 0,
            index_layout: list[int] | None = None
    ) -> None:
        """
        Initialize the physical quantum circuit.

        Parameters
        ----------
        num_dots : int
            Number of quantum dots.
        num_clbits : int
            Number of classical bits.
        index_layout : list[int]
            List representing the mapping of quantum circuit register to quantum dot.
        """
        self._qc = QuantumCircuit(num_dots, num_clbits)
        if index_layout is None:
            self._index_layout = list(range(self._qc.num_qubits))
        else:
            self._index_layout = index_layout

    def is_valid(self) -> bool:
        """
        Check whether the object is in a valid state.
        
        Returns
        -------
        bool
            True if the object is valid, False otherwise.
        """
        for name in self._qc.count_ops():
            if name != 'ex' and name != 'm' and name != 'sin' and name != 'up' and name != 'barrier':
                return False
        return True

    def __str__(self) -> None:
        return str(self._qc.draw())

    def __getattr__(self, name):
        return getattr(self._qc, name)

    @property
    def num_dots(self) -> int:
        return self._qc.num_qubits

    @property
    def num_clbits(self) -> int:
        return self._qc.num_clbits

    @property
    def index_layout(self) -> list[int]:
        return self._index_layout

    @property
    def qc(self) -> QuantumCircuit:
        return self._qc

    @qc.setter
    def qc(self, value) -> None:
        if isinstance(value, QuantumCircuit):
            self._qc = value
        else:
            raise TypeError("The qc must be a QuantumCircuit object.")

    @index_layout.setter
    def index_layout(self, value) -> None:
        if isinstance(value, list):
            if all(isinstance(x, int) and x >=0 for x in value):
                self._index_layout = value
            else:
                raise TypeError("The index_layout must be a list of zero or positive integers object.")
        else:
            raise TypeError("The index_layout must be a list.")

    def to_qiskit(self) -> QuantumCircuit:
        return self._qc

    def initialize(self) -> None:
        """
        Initialize the physical quantum circuit.

        Notes
        -----
        Selects three quantum dot pairs sequentially starting from the 0th quantum dot,
        and initializes all of them to the singlet state.
        """
        if self.num_qubits % 3 != 0:
            raise ValueError("Number of qubits must be a multiple of 3.")

        if self._index_layout is None:
            for q in range(self.num_qubits // 3):
                a0, a1, a2 = q * 3, q * 3 + 1, q * 3 + 2
                self._qc.append(ResetSinglet(), [a0, a1])
                self._qc.append(ResetUp(), [a2])
        else:
            if len(self._index_layout) % 3 != 0:
                raise ValueError("Length of indices must be a multiple of 3.")
            for q in range(len(self._index_layout) // 3):
                (a0, a1, a2) = (
                    self._index_layout[q * 3],
                    self._index_layout[q * 3 + 1],
                    self._index_layout[q * 3 + 2]
                )
                self._qc.append(ResetSinglet(), [a0, a1])
                self._qc.append(ResetUp(), [a2])
