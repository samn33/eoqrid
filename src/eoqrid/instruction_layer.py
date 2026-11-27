from __future__ import annotations

from collections import UserList


class InstructionLayer(UserList):
    """
    Instruction layer.

    """
    def __str__(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        s = ""
        for inst in self.data:
            s += f"{inst.to_string()}\n"
        return s.rstrip()

    def duration(self) -> float:
        return max([inst.duration() for inst in self.data])
