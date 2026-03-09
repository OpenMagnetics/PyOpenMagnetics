"""
Waveform and Operating Point dataclass models.

Provides structured representations for periodic waveforms and
operating point specifications used in magnetic component simulation.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class WaveformType(Enum):
    """Waveform shape type."""
    TRIANGULAR = "triangular"
    SINUSOIDAL = "sinusoidal"
    RECTANGULAR = "rectangular"
    TRAPEZOIDAL = "trapezoidal"
    CUSTOM = "custom"


@dataclass
class Waveform:
    """Generic periodic waveform.

    Represents a waveform as sample points over one period.

    Attributes:
        data: Sample values (voltage or current)
        time: Time points in seconds
        waveform_type: Type of waveform
    """
    data: List[float]                      # Sample values
    time: List[float]                      # Time points (s)
    waveform_type: WaveformType = WaveformType.CUSTOM

    @classmethod
    def triangular(cls, v_min: float, v_max: float, duty: float,
                   period: float) -> "Waveform":
        """Create triangular waveform.

        Args:
            v_min: Minimum value (at start)
            v_max: Maximum value (at peak)
            duty: Duty cycle (rise time / period)
            period: Period in seconds

        Returns:
            Waveform with triangular shape
        """
        t_rise = duty * period
        return cls(
            data=[v_min, v_max, v_min],
            time=[0.0, t_rise, period],
            waveform_type=WaveformType.TRIANGULAR
        )

    @classmethod
    def rectangular(cls, v_high: float, v_low: float, duty: float,
                    period: float) -> "Waveform":
        """Create rectangular (square) waveform.

        Args:
            v_high: High level value
            v_low: Low level value
            duty: Duty cycle (high time / period)
            period: Period in seconds

        Returns:
            Waveform with rectangular shape
        """
        t_on = duty * period
        return cls(
            data=[v_high, v_high, v_low, v_low],
            time=[0.0, t_on, t_on, period],
            waveform_type=WaveformType.RECTANGULAR
        )

    @classmethod
    def sinusoidal(cls, amplitude: float, frequency: float, dc_offset: float = 0.0,
                   num_points: int = 64) -> "Waveform":
        """Create sinusoidal waveform.

        Args:
            amplitude: Peak amplitude
            frequency: Frequency in Hz
            dc_offset: DC offset value
            num_points: Number of sample points

        Returns:
            Waveform with sinusoidal shape
        """
        import math
        period = 1.0 / frequency
        data = []
        time = []
        for i in range(num_points + 1):
            t = i * period / num_points
            v = dc_offset + amplitude * math.sin(2 * math.pi * frequency * t)
            time.append(t)
            data.append(v)
        return cls(
            data=data,
            time=time,
            waveform_type=WaveformType.SINUSOIDAL
        )

    def to_dict(self) -> dict:
        """Convert to MAS-compatible dict format."""
        return {
            "waveform": {
                "data": self.data,
                "time": self.time
            }
        }


@dataclass
class WindingExcitation:
    """Excitation for a single winding.

    Attributes:
        name: Winding name (e.g., "Primary", "Secondary")
        current: Current waveform (optional)
        voltage: Voltage waveform (optional)
        frequency_hz: Operating frequency in Hz
    """
    name: str = "Primary"
    current: Optional[Waveform] = None
    voltage: Optional[Waveform] = None
    frequency_hz: float = 100000

    def to_dict(self) -> dict:
        """Convert to MAS-compatible dict format."""
        result = {
            "name": self.name,
            "frequency": self.frequency_hz,
        }
        if self.current:
            result["current"] = self.current.to_dict()
        if self.voltage:
            result["voltage"] = self.voltage.to_dict()
        return result


@dataclass
class OperatingPointModel:
    """Complete operating point specification.

    Defines a single operating condition with all winding excitations.

    Attributes:
        name: Operating point name (e.g., "Low Line", "Full Load")
        excitations: List of winding excitations
        ambient_temperature_c: Ambient temperature in Celsius
        weight: Weighting factor for multi-OP analysis
    """
    name: str = "Operating Point"
    excitations: List[WindingExcitation] = field(default_factory=list)
    ambient_temperature_c: float = 25.0
    weight: float = 1.0                    # For multi-OP weighted analysis

    def to_mas(self) -> dict:
        """Convert to MAS-compliant dict.

        Returns:
            Dict in MAS operatingPoint format
        """
        return {
            "name": self.name,
            "conditions": {
                "ambientTemperature": self.ambient_temperature_c
            },
            "excitationsPerWinding": [exc.to_dict() for exc in self.excitations]
        }

    @classmethod
    def from_mas(cls, mas_op: dict) -> "OperatingPointModel":
        """Create from MAS operatingPoint dict.

        Args:
            mas_op: MAS operating point dict

        Returns:
            OperatingPointModel instance
        """
        conditions = mas_op.get("conditions", {})
        excitations = []

        for exc_data in mas_op.get("excitationsPerWinding", []):
            current = None
            voltage = None

            if "current" in exc_data and exc_data["current"]:
                curr_wf = exc_data["current"].get("waveform", {})
                if curr_wf:
                    current = Waveform(
                        data=curr_wf.get("data", []),
                        time=curr_wf.get("time", [])
                    )

            if "voltage" in exc_data and exc_data["voltage"]:
                volt_wf = exc_data["voltage"].get("waveform", {})
                if volt_wf:
                    voltage = Waveform(
                        data=volt_wf.get("data", []),
                        time=volt_wf.get("time", [])
                    )

            excitations.append(WindingExcitation(
                name=exc_data.get("name", "Winding"),
                current=current,
                voltage=voltage,
                frequency_hz=exc_data.get("frequency", 100000)
            ))

        return cls(
            name=mas_op.get("name", "Operating Point"),
            excitations=excitations,
            ambient_temperature_c=conditions.get("ambientTemperature", 25.0)
        )
