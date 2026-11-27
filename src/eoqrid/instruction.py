from __future__ import annotations

from abc import ABC, abstractmethod

from eoqrid.pulse_distortion import PulseDistortion

# Temporary settings
WIDTH_RESET_SINGLET = 1.0
WIDTH_RESET_UP      = 1.0
WIDTH_MEASUREMENT   = 1.0
DURATION_RESET_SINGLET = 1.0
DURATION_RESET_UP      = 1.0
DURATION_MEASUREMENT   = 1.0


class Instruction(ABC):

    name: str
    width: float
    
    def __init__(self, qregs: list[int]) -> None:
        self.qregs = qregs

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> str:
        pass

    @abstractmethod
    def duration(self) -> int:
        pass
        
class InstructionResetSinglet(Instruction):

    def __init__(self, qregs: list[int]) -> None:
        super().__init__(qregs)
        self.name = "sin"
        self.width = WIDTH_RESET_SINGLET

    def __str__(self) -> str:
        return self.to_string()
    
    def to_string(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> str:
        return {
            "name": self.name,
            "qregs": self.qregs,
            "pulse_width": self.width,
            "estimated_duration": self.duration()
        }

    def duration(self) -> int:
        return DURATION_RESET_SINGLET

class InstructionResetUp(Instruction):

    def __init__(self, qregs: list[int]) -> None:
        super().__init__(qregs)
        self.name = "up"
        self.width = WIDTH_RESET_UP
    
    def __str__(self) -> str:
        return self.to_string()
    
    def to_string(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> str:
        return {
            "name": self.name,
            "qregs": self.qregs,
            "pulse_width": self.width,
            "estimated_duration": self.duration()
        }

    def duration(self) -> int:
        return DURATION_RESET_UP

class InstructionMeasurement(Instruction):

    def __init__(self, qregs: list[int], cregs: list[int]) -> None:
        super().__init__(qregs)
        self.name = "m"
        self.width = WIDTH_MEASUREMENT
        self.cregs = cregs 
    
    def __str__(self) -> str:
        return self.to_string()
    
    def to_string(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> str:
        return {
            "name": self.name,
            "qregs": self.qregs,
            "cregs": self.cregs,
            "pulse_width": self.width,
            "estimated_duration": self.duration()
        }

    def duration(self) -> int:
        return DURATION_MEASUREMENT

class InstructionExchangeInteraction(Instruction):

    def __init__(
            self,
            qregs: list[int],
            width: float,
            pulse_distortion: PulseDistortion,
    ) -> None:
        super().__init__(qregs)
        self.name = "ex"
        self.width = width
        self.pulse_distortion = pulse_distortion

    def __str__(self) -> str:
        return self.to_string()
    
    def to_string(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> str:
        return {
            "name": self.name,
            "qregs": self.qregs,
            "pulse_width": float(self.width),
            "estimated_duration": float(self.duration()),
        }

    def duration(self) -> int:
        return self.pulse_distortion.duration(self.width)

    def integral(self) -> float:
        return self.pulse_distortion.integral(self.width)
