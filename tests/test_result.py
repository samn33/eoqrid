import pytest
from dataclasses import FrozenInstanceError

from eoqrid import Result


def test_constructor():

    res = Result(
        num_qubits = 2,
        num_clbits = 3,
        num_dots = 6,
        qstate = None,
        m_last = '00',
        freq = {'00': 5, '11': 5},
    )
    assert res.num_qubits == 2
    assert res.num_clbits == 3
    assert res.freq == {'00': 5, '11': 5}

def test_constructor_exception():

    res = Result(
        num_qubits = 2,
        num_clbits = 3,
        num_dots = 6,
        qstate = None,
        m_last = '00',
        freq = {'00': 5, '11': 5},
    )
    with pytest.raises(FrozenInstanceError):
        res.num_qubits = 1

    with pytest.raises(FrozenInstanceError):
        res.num_clbits = 1

    with pytest.raises(FrozenInstanceError):
        res.freq = {'0': 5, '1': 5}
