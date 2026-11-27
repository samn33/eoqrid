from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class PulseDistortion(ABC):
    name: str
    
    @abstractmethod
    def amplitude(self, t: float, width):
        pass

    @abstractmethod
    def duration(self, width: float):
        pass

    @abstractmethod
    def integral(self, width: float):
        pass

    @abstractmethod
    def integral_to_width(self, integral: float):
        pass

class RectangularDistortion(PulseDistortion):

    def __init__(self, peak: float = 1.0) -> None:
        if peak <= 0.0:
            raise ValueError("The peak must be positive value.")
        self.name = "Rectangular Distortion"
        self.peak = peak

    def amplitude(self, t: float, width: float):
        if 0 <= t <= width:
            return self.peak
        return 0.0

    def duration(self, width: float):
        return width

    def integral(self, width: float) -> float:
        return width * self.peak

    def integral_to_width(self, integral: float):
        return integral / self.peak

class GaussianDistortion(PulseDistortion):

    def __init__(self, peak: float = 1.0, width_per_sigma: float = 3.0) -> None:
        if peak <= 0.0:
            raise ValueError("The peak must be positive value.")
        self.name = "Gaussian Distortion"
        self.peak = peak
        self.width_per_sigma = width_per_sigma
        self._exp45 = np.exp(-4.5)

    def amplitude(self, t: float, width: float):
        sigma = width / self.width_per_sigma
        mu = 3.0 * sigma
        if t < 0.0 or t > 6.0 * sigma:
            return 0.0
        return (
            self.peak
            * (np.exp(-((t - mu)**2) / (2* (sigma ** 2))) - self._exp45)
            / (1.0 - self._exp45)
        )

    def duration(self, width: float):
        sigma = width / self.width_per_sigma
        return 6.0 * sigma

    def integral(self, width: float) -> float:
        sigma = width / self.width_per_sigma
        return (
            self.peak * sigma
            * (np.sqrt(2.0 * np.pi) * 0.9973 - 6.0 * self._exp45)
            / (1.0 - self._exp45)
        )

    def integral_to_width(self, integral: float):
        return (
            self.width_per_sigma * integral
            * (1.0 - self._exp45)
            / (self.peak * (np.sqrt(2 * np.pi) * 0.9973 - 6 * self._exp45))
        )
