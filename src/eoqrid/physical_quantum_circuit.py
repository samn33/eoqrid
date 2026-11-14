from __future__ import annotations

from qiskit import QuantumCircuit

from eoqrid.reset_singlet import ResetSinglet
from eoqrid.reset_up import ResetUp


class PhysicalQuantumCircuit:
    """
    Physical quantum circuit in exchange-only architecture.

    Attributes
    ----------
    qc : QuantumCircuit
        Physical quantum circuit object.
    num_dots : int
        Number of quantum dots.
    """
    def __init__(
            self,
            qc: QuantumCircuit | int,
            index_layout: list[int] | None = None
    ) -> None:
        """
        Initialize the physical quantum circuit.

        Parameters
        ----------
        qc : QuantumCircuit or int
            Physical quantum circuit or an integer to create a default quantum circuit.
        """
        if isinstance(qc, int):
            self._qc = QuantumCircuit(qc)
        elif isinstance(qc, QuantumCircuit):
            self._qc = qc
        else:
            raise TypeError("qc must be QuantumCircuit or integer.")

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
            if name != 'ex' and name != 'm' and name != 'sin' and name != 'up':
                return False
        return True

    def __str__(self) -> None:
        return str(self._qc.draw())

    def __getattr__(self, name):
        return getattr(self._qc, name)

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
            
