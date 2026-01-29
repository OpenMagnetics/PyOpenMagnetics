"""
TAS Inputs models - Requirements and operating points for basic DC-DC converters.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

from tas.models.waveforms import TASWaveform


class OperatingMode(Enum):
    """Converter operating mode."""
    CCM = "ccm"  # Continuous conduction mode
    DCM = "dcm"  # Discontinuous conduction mode
    BCM = "bcm"  # Boundary conduction mode


class ModulationType(Enum):
    """Basic modulation schemes for DC-DC converters."""
    PWM = "pwm"          # Pulse Width Modulation (fixed frequency)
    PFM = "pfm"          # Pulse Frequency Modulation (variable frequency)
    HYSTERETIC = "hysteretic"  # Hysteretic control


class ControlMode(Enum):
    """Control loop architecture."""
    VOLTAGE_MODE = "voltage_mode"
    CURRENT_MODE = "current_mode"


@dataclass
class TASModulation:
    """
    Modulation and control specification for DC-DC converters.

    The modulation type fundamentally affects waveform behavior.
    """
    type: ModulationType = ModulationType.PWM
    control_mode: ControlMode = ControlMode.VOLTAGE_MODE
    frequency_fixed: bool = True
    max_duty: float = 0.9
    min_duty: float = 0.0

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "control_mode": self.control_mode.value,
            "frequency_fixed": self.frequency_fixed,
            "max_duty": self.max_duty,
            "min_duty": self.min_duty,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TASModulation":
        return cls(
            type=ModulationType(d["type"]) if d.get("type") else ModulationType.PWM,
            control_mode=ControlMode(d["control_mode"]) if d.get("control_mode") else ControlMode.VOLTAGE_MODE,
            frequency_fixed=d.get("frequency_fixed", True),
            max_duty=d.get("max_duty", 0.9),
            min_duty=d.get("min_duty", 0.0),
        )


@dataclass
class TASRequirements:
    """Electrical requirements for the converter."""
    v_in_min: float = 0.0
    v_in_max: float = 0.0
    v_in_nominal: Optional[float] = None
    v_out: float = 0.0
    i_out_max: float = 0.0
    p_out_max: Optional[float] = None
    efficiency_target: float = 0.9
    isolation_voltage: Optional[float] = None  # V, None = non-isolated

    def to_dict(self) -> dict:
        result = {
            "v_in_min": self.v_in_min,
            "v_in_max": self.v_in_max,
            "v_out": self.v_out,
            "i_out_max": self.i_out_max,
            "efficiency_target": self.efficiency_target,
        }
        if self.v_in_nominal is not None:
            result["v_in_nominal"] = self.v_in_nominal
        if self.p_out_max is not None:
            result["p_out_max"] = self.p_out_max
        if self.isolation_voltage is not None:
            result["isolation_voltage"] = self.isolation_voltage
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASRequirements":
        return cls(
            v_in_min=d.get("v_in_min", 0.0),
            v_in_max=d.get("v_in_max", 0.0),
            v_in_nominal=d.get("v_in_nominal"),
            v_out=d.get("v_out", 0.0),
            i_out_max=d.get("i_out_max", 0.0),
            p_out_max=d.get("p_out_max"),
            efficiency_target=d.get("efficiency_target", 0.9),
            isolation_voltage=d.get("isolation_voltage"),
        )


@dataclass
class TASOperatingPoint:
    """
    Operating point with waveform-based excitations.

    The modulation field captures how the converter is controlled,
    which fundamentally affects the waveform shapes.
    """
    name: str = "nominal"
    description: str = ""
    frequency: float = 100e3  # Hz
    duty_cycle: Optional[float] = None  # 0-1
    mode: OperatingMode = OperatingMode.CCM
    modulation: Optional[TASModulation] = None
    waveforms: Dict[str, TASWaveform] = field(default_factory=dict)
    ambient_temperature: float = 25.0  # C

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "frequency": self.frequency,
            "mode": self.mode.value,
            "ambient_temperature": self.ambient_temperature,
        }
        if self.description:
            result["description"] = self.description
        if self.duty_cycle is not None:
            result["duty_cycle"] = self.duty_cycle
        if self.modulation:
            result["modulation"] = self.modulation.to_dict()
        if self.waveforms:
            result["waveforms"] = {k: v.to_dict() for k, v in self.waveforms.items()}
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASOperatingPoint":
        mode = OperatingMode(d["mode"]) if d.get("mode") else OperatingMode.CCM
        modulation = TASModulation.from_dict(d["modulation"]) if d.get("modulation") else None
        waveforms = {k: TASWaveform.from_dict(v) for k, v in d.get("waveforms", {}).items()}
        return cls(
            name=d.get("name", "nominal"),
            description=d.get("description", ""),
            frequency=d.get("frequency", 100e3),
            duty_cycle=d.get("duty_cycle"),
            mode=mode,
            modulation=modulation,
            waveforms=waveforms,
            ambient_temperature=d.get("ambient_temperature", 25.0),
        )


@dataclass
class TASInputs:
    """Complete inputs section of a TAS document."""
    requirements: TASRequirements = field(default_factory=TASRequirements)
    operating_points: List[TASOperatingPoint] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {"requirements": self.requirements.to_dict()}
        if self.operating_points:
            result["operating_points"] = [op.to_dict() for op in self.operating_points]
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASInputs":
        return cls(
            requirements=TASRequirements.from_dict(d.get("requirements", {})),
            operating_points=[
                TASOperatingPoint.from_dict(op)
                for op in d.get("operating_points", [])
            ],
        )
