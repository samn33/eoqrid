from __future__ import annotations

import json
from collections import UserList

from eoqrid.exchange_interaction import ExchangeInteraction
from eoqrid.measurement import Measurement
from eoqrid.physical_quantum_circuit import PhysicalQuantumCircuit
from eoqrid.pulse_distortion import PulseDistortion
from eoqrid.reset_singlet import ResetSinglet
from eoqrid.reset_up import ResetUp


class InstructionSequence(UserList):
    """
    Instruction sequence.
    
    Attributes
    ----------
    num_dots : int
        Number of quantum dots (physical qubits).
    num_clbits : int
        Number of classical bits.
    index_layout : list[int]
        List representing the mapping of quantum circuit register to quantum dot.
    pulse_distortion : PulseDistortion
        Pulse distortion to model how voltage-pulse durations map to exchange interactions on the quantum chip.
    """
    def __init__(
            self,
            num_dots: int,
            num_clbits: int,
            index_layout: list[int],
            pulse_distortion: PulseDistortion
    ) -> None:
        """
        Initialize the instruction sequence.

        Parameters
        ----------
        num_dots : int
            Number of quantum dots (physical qubits).
        num_clbits : int
            Number of classical bits.
        index_layout : list[int]
            List representing the mapping of quantum circuit register to quantum dot.
        pulse_distortion : PulseDistortion
            Pulse distortion to model how voltage-pulse durations map to exchange interactions on the quantum chip.
        """
        super().__init__()
        self.num_dots = num_dots
        self.num_clbits = num_clbits
        self.index_layout = index_layout
        self.pulse_distortion = pulse_distortion

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        s = "** Instruction Sequence **\n"
        s += f"num_dots: {self.num_dots}, "
        s += f"num_clbits: {self.num_clbits}\n"
        s += f"pulse model: {self.pulse_distortion.name}\n"
        s += f"total duration: {self.duration()}\n"
        for i, inst_layer in enumerate(self.data):
            s += f"- layer: {i}, duration: {inst_layer.duration()}\n"
            s += f"{inst_layer.to_string()}\n"
        return s.rstrip()

    def to_dict(self) -> dict:
        instruction_list = [
            [inst.to_dict() for inst in inst_layer.data]
            for inst_layer in self.data
        ]
        return {
            "num_dots": self.num_dots,
            "num_clbits": self.num_clbits,
            "pulse_distortion": self.pulse_distortion.name,
            "total_duration": self.duration(),
            "instructions": instruction_list,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def duration(self) -> float:
        return sum([inst_layer.duration() for inst_layer in self.data])
    
    def to_physical_quantum_circuit(self) -> PhysicalQuantumCircuit:
        """
        Convert to physical quantum circuit.

        """
        qc_phys = PhysicalQuantumCircuit(
            num_dots = self.num_dots,
            num_clbits = self.num_clbits,
            index_layout = self.index_layout,
        )
        for inst_layer in self.data:
            for inst in inst_layer:
                match inst.name:
                    case "sin":
                        qc_phys.append(ResetSinglet(), inst.qregs)
                    case "up":
                        qc_phys.append(ResetUp(), inst.qregs)
                    case "m":
                        qc_phys.append(Measurement(), inst.qregs, inst.cregs)
                    case "ex":
                        qc_phys.append(ExchangeInteraction(inst.integral(), 1.0), inst.qregs)
                    case _:
                        raise ValueError("Unknown instruction.")
            qc_phys.barrier()
        return qc_phys
