from collections import defaultdict
from dataclasses import dataclass

from eoqrid.quantum_state import QuantumState


@dataclass(frozen=True)
class Result:
    """
    Execution result of a quantum circuit or simulation.

    Attributes
    ----------
    num_qubits : int
        Number of logical qubits.
    num_clbits : int
        Number of classical bits.
    num_dots : int
        Number of quantum dots (physical qubits).
    qstate : QuantumState
        Quantum state object.
    m_last : str
        Most recent measurement outcome.
    freq : defaultdict
        Measurement frequency distribution.
    """
    num_qubits : int
    num_clbits : int
    num_dots : int
    qstate : QuantumState
    m_last : str
    freq : defaultdict
