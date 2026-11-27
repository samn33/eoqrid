import numpy as np
from qiskit import QuantumCircuit

from eoqrid import (
    EoqEngine,
    GaussianDistortion,
    PulseDistortion,
    RectangularDistortion,
)
from eoqrid.util import plot_pdist


class MyDistortion(PulseDistortion):

    def __init__(self, peak: float = 1.0) -> None:
        self.name = "My Distortion"
        self.peak = peak

    def amplitude(self, t: float, width):
        amp = 0.0
        if 0.0 <= t <= 2.0 * width:
            amp = self.peak * (np.sin(t * np.pi / (2.0 * width)))
        return amp

    def duration(self, width: float):
        return 2.0 * width

    def integral(self, width: float):
        return 4.0 * self.peak * width / np.pi

    def integral_to_width(self, integral: float):
        return np.pi * integral / (4.0 * self.peak)

num_dots = 3
num_qubits = num_dots // 3
eoq = EoqEngine(num_dots)

# Logical quantum circuit
qc = QuantumCircuit(num_qubits)
qc.h(0)

# Transpile to physical quantum circuit
qc_phys = eoq.transpile(qc, optimization_level=3)
print(qc_phys)

# Pulse distortion
pdist = RectangularDistortion(peak=2.0)
plot_pdist(pdist, width=5.0)
pdist = GaussianDistortion(peak=3.0)
plot_pdist(pdist, width=5.0)
pdist = MyDistortion(peak=4.0)
plot_pdist(pdist, width=5.0)

# Instruction sequence
inst_seq = eoq.schedule(qc_phys, pulse_distortion = pdist)
print(inst_seq)

# Result
res = eoq.drive(inst_seq)
res.qstate.draw()
