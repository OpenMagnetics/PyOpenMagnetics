"""
TAS Waveform models - MAS-compatible waveform definitions.

Waveforms are the universal language that makes TAS topology-agnostic.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum
import math


class WaveformShape(Enum):
    """Standard waveform shapes."""
    TRIANGULAR = "triangular"
    RECTANGULAR = "rectangular"
    CUSTOM = "custom"


@dataclass
class TASWaveform:
    """
    MAS-compatible waveform representation.

    Represents a periodic waveform as time/data sample pairs.
    """
    data: List[float]
    time: List[float]
    shape: WaveformShape = WaveformShape.CUSTOM
    unit: str = ""

    @classmethod
    def triangular(cls, v_min: float, v_max: float, duty: float,
                   period: float, unit: str = "") -> "TASWaveform":
        """Create triangular waveform (typical inductor current)."""
        t_rise = duty * period
        return cls(
            data=[v_min, v_max, v_min],
            time=[0.0, t_rise, period],
            shape=WaveformShape.TRIANGULAR,
            unit=unit,
        )

    @classmethod
    def rectangular(cls, v_high: float, v_low: float, duty: float,
                    period: float, unit: str = "") -> "TASWaveform":
        """Create rectangular waveform (typical switch voltage)."""
        t_on = duty * period
        return cls(
            data=[v_high, v_high, v_low, v_low],
            time=[0.0, t_on, t_on, period],
            shape=WaveformShape.RECTANGULAR,
            unit=unit,
        )

    def to_mas(self) -> dict:
        """Convert to MAS-compatible dict format."""
        return {"waveform": {"data": self.data, "time": self.time}}

    @classmethod
    def from_mas(cls, mas_dict: dict, unit: str = "") -> "TASWaveform":
        """Create from MAS waveform dict."""
        wf = mas_dict.get("waveform", mas_dict)
        return cls(
            data=wf.get("data", []),
            time=wf.get("time", []),
            unit=unit,
        )

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "data": self.data,
            "time": self.time,
            "shape": self.shape.value if self.shape else None,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TASWaveform":
        """Create from dict."""
        shape = WaveformShape(d["shape"]) if d.get("shape") else WaveformShape.CUSTOM
        return cls(
            data=d.get("data", []),
            time=d.get("time", []),
            shape=shape,
            unit=d.get("unit", ""),
        )

    @property
    def period(self) -> float:
        """Get waveform period in seconds."""
        return max(self.time) if self.time else 0.0

    @property
    def frequency(self) -> float:
        """Get waveform frequency in Hz."""
        p = self.period
        return 1.0 / p if p > 0 else 0.0

    @property
    def peak(self) -> float:
        """Get peak (maximum) value."""
        return max(self.data) if self.data else 0.0

    @property
    def min(self) -> float:
        """Get minimum value."""
        return min(self.data) if self.data else 0.0

    @property
    def peak_to_peak(self) -> float:
        """Get peak-to-peak value."""
        return self.peak - self.min
