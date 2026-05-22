from collections import defaultdict
from dataclasses import dataclass

from eoqrid.quantum_state import QuantumState

@dataclass(frozen=True)
class Result:
    """
    Result of execution

    Attributes
    ----------
    num_qubits : int
        number of quantum bits (logical qubits).
    num_clbits : int
        number of classical bits.
    num_dots : int
        number of dots (physical qubits).
        num_dots = 3 * num_qubits.
    qstate : QuantumState
        quantum state object.
    m_last : str
        last measurement value
    freq : defaultdict
        measurement frequency
    
    """
    num_qubits : int
    num_clbits : int
    num_dots : int
    qstate : QuantumState
    m_last : str
    freq : defaultdict
