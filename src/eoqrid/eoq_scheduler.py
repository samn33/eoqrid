from __future__ import annotations

from qiskit.converters import circuit_to_dag

from eoqrid.instruction import (
    InstructionExchangeInteraction,
    InstructionMeasurement,
    InstructionResetSinglet,
    InstructionResetUp,
)
from eoqrid.instruction_layer import InstructionLayer
from eoqrid.instruction_sequence import InstructionSequence
from eoqrid.physical_quantum_circuit import PhysicalQuantumCircuit
from eoqrid.pulse_distortion import PulseDistortion, RectangularDistortion


class EoqScheduler:
    """ Scheduler for exchange-only quantum computing. """
    def schedule(
            self,
            qc_phys: PhysicalQuantumCircuit,
            pulse_distortion: PulseDistortion | None = None,
    ) -> InstructionSequence:
        """
        Generate instruction sequence.
        
        Parameters
        ----------
        qc_phys : QuantumCircuit
            Physical uantum circuit.
        pulse_distortion : PulseDistortion
            Pulse distortion (RectangularDistortion/GaussianDistortion etc).
    
        Returns
        -------
        InstructionSequence
            Instruction sequence.
        """
        if pulse_distortion is None:
            pulse_distortion = RectangularDistortion()

        qc = qc_phys.to_qiskit()
        num_dots = qc.num_qubits
        num_clbits = qc.num_clbits
        dag = circuit_to_dag(qc)

        index_layout = qc_phys.index_layout
        inst_seq = InstructionSequence(num_dots, num_clbits, index_layout, pulse_distortion)
        for depth, layer in enumerate(dag.layers()):
            inst_layer = InstructionLayer()
            for node in layer["graph"].op_nodes():
                qubits = [qc.find_bit(q).index for q in node.qargs]
                clbits = [qc.find_bit(q).index for q in node.cargs]

                match node.name:
                    case "sin":
                        inst = InstructionResetSinglet(qubits)
                    case "up":
                        inst = InstructionResetUp(qubits)
                    case "m":
                        inst = InstructionMeasurement(qubits, clbits)
                    case "ex":
                        t = node.params[0]
                        J = node.params[1]
                        width = pulse_distortion.integral_to_width(t * J)
                        inst = InstructionExchangeInteraction(
                            qubits,
                            width,
                            pulse_distortion = pulse_distortion
                        )
                    case _:
                        raise ValueError("Unknown gate.")
                inst_layer.append(inst)

            inst_seq.append(inst_layer)

        return inst_seq
