"""
Voltage, Current, and Power specification dataclass models.

Provides complete electrical specifications with all measurement types
(nominal, min, max, RMS, peak, peak-to-peak, etc.) for power supply design.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import math


class ACDCType(Enum):
    """AC or DC voltage/current type."""
    AC = "ac"
    DC = "dc"


@dataclass
class VoltageSpec:
    """Complete voltage specification with all measurement types.

    Attributes:
        nominal: Nominal/typical value in Volts
        min: Minimum value in Volts
        max: Maximum value in Volts
        rms: RMS value in Volts (for AC)
        avg: Average value in Volts
        peak: Peak value in Volts
        peak_to_peak: Peak-to-peak value in Volts
        ac_dc: AC or DC type
    """
    nominal: float                         # Nominal/typical value (V)
    min: Optional[float] = None            # Minimum value (V)
    max: Optional[float] = None            # Maximum value (V)
    rms: Optional[float] = None            # RMS value (V) - for AC
    avg: Optional[float] = None            # Average value (V)
    peak: Optional[float] = None           # Peak value (V)
    peak_to_peak: Optional[float] = None   # Peak-to-peak (V)
    ac_dc: ACDCType = ACDCType.DC

    @classmethod
    def dc(cls, nominal: float, tolerance_pct: float = 5.0) -> "VoltageSpec":
        """Create DC voltage spec with tolerance.

        Args:
            nominal: Nominal voltage in Volts
            tolerance_pct: Tolerance percentage (default 5%)

        Returns:
            VoltageSpec configured for DC with min/max from tolerance
        """
        delta = nominal * tolerance_pct / 100
        return cls(
            nominal=nominal,
            min=nominal - delta,
            max=nominal + delta,
            avg=nominal,
            ac_dc=ACDCType.DC
        )

    @classmethod
    def dc_range(cls, v_min: float, v_max: float) -> "VoltageSpec":
        """Create DC voltage spec from min/max range.

        Args:
            v_min: Minimum voltage in Volts
            v_max: Maximum voltage in Volts

        Returns:
            VoltageSpec with nominal at midpoint
        """
        return cls(
            nominal=(v_min + v_max) / 2,
            min=v_min,
            max=v_max,
            avg=(v_min + v_max) / 2,
            ac_dc=ACDCType.DC
        )

    @classmethod
    def ac(cls, v_rms: float, v_min_rms: Optional[float] = None,
           v_max_rms: Optional[float] = None) -> "VoltageSpec":
        """Create AC voltage spec.

        Args:
            v_rms: RMS voltage in Volts
            v_min_rms: Minimum RMS voltage (optional)
            v_max_rms: Maximum RMS voltage (optional)

        Returns:
            VoltageSpec configured for AC with peak values calculated
        """
        v_peak = v_rms * math.sqrt(2)
        return cls(
            nominal=v_rms,
            min=v_min_rms,
            max=v_max_rms,
            rms=v_rms,
            peak=v_peak,
            peak_to_peak=2 * v_peak,
            ac_dc=ACDCType.AC
        )


@dataclass
class CurrentSpec:
    """Complete current specification with all measurement types.

    Attributes:
        nominal: Nominal/typical value in Amps
        min: Minimum value in Amps
        max: Maximum value in Amps
        rms: RMS value in Amps
        avg: Average value in Amps
        peak: Peak value in Amps
        peak_to_peak: Peak-to-peak ripple in Amps
        dc_bias: DC component in Amps
    """
    nominal: float                         # Nominal/typical value (A)
    min: Optional[float] = None            # Minimum value (A)
    max: Optional[float] = None            # Maximum value (A)
    rms: Optional[float] = None            # RMS value (A)
    avg: Optional[float] = None            # Average value (A)
    peak: Optional[float] = None           # Peak value (A)
    peak_to_peak: Optional[float] = None   # Peak-to-peak ripple (A)
    dc_bias: Optional[float] = None        # DC component (A)

    @classmethod
    def dc(cls, i_dc: float, ripple_pp: float = 0.0) -> "CurrentSpec":
        """Create DC current spec with optional ripple.

        Args:
            i_dc: DC current in Amps
            ripple_pp: Peak-to-peak ripple current (default 0)

        Returns:
            CurrentSpec with RMS calculated for triangle wave on DC
        """
        i_peak = i_dc + ripple_pp / 2
        i_min = i_dc - ripple_pp / 2
        # RMS of triangle wave on DC: sqrt(Idc^2 + (Ipp^2/12))
        i_rms = math.sqrt(i_dc**2 + (ripple_pp**2 / 12))
        return cls(
            nominal=i_dc,
            min=i_min,
            max=i_peak,
            rms=i_rms,
            avg=i_dc,
            peak=i_peak,
            peak_to_peak=ripple_pp,
            dc_bias=i_dc
        )


@dataclass
class PowerSpec:
    """Power specification.

    Attributes:
        nominal_w: Nominal power in Watts
        min_w: Minimum power in Watts
        max_w: Maximum power in Watts
    """
    nominal_w: float                       # Nominal power (W)
    min_w: Optional[float] = None          # Minimum power (W)
    max_w: Optional[float] = None          # Maximum power (W)

    @classmethod
    def from_vi(cls, voltage: VoltageSpec, current: CurrentSpec) -> "PowerSpec":
        """Calculate power from voltage and current specs.

        Args:
            voltage: Voltage specification
            current: Current specification

        Returns:
            PowerSpec with nominal/min/max calculated from V*I
        """
        p_nom = voltage.nominal * current.nominal
        p_min = (voltage.min or voltage.nominal) * (current.min or 0)
        p_max = (voltage.max or voltage.nominal) * (current.max or current.nominal)
        return cls(nominal_w=p_nom, min_w=p_min, max_w=p_max)


@dataclass
class PortSpec:
    """Input or output port specification.

    Attributes:
        name: Port name (e.g., "Input", "Output 1")
        voltage: Voltage specification
        current: Current specification
    """
    name: str = "port"
    voltage: VoltageSpec = field(default_factory=lambda: VoltageSpec(nominal=0))
    current: CurrentSpec = field(default_factory=lambda: CurrentSpec(nominal=0))

    @property
    def power(self) -> PowerSpec:
        """Calculate power from voltage and current."""
        return PowerSpec.from_vi(self.voltage, self.current)


@dataclass
class PowerSupplySpec:
    """Complete power supply specification.

    Defines a complete power supply with inputs, outputs, and targets.

    Attributes:
        name: Power supply name/description
        inputs: List of input port specifications
        outputs: List of output port specifications
        efficiency: Target efficiency (0-1)
        isolation_v: Isolation voltage in Volts, None for non-isolated
    """
    name: str = "Power Supply"
    inputs: List[PortSpec] = field(default_factory=list)
    outputs: List[PortSpec] = field(default_factory=list)
    efficiency: float = 0.90               # Target efficiency
    isolation_v: Optional[float] = None    # Isolation voltage (V), None = non-isolated

    @property
    def total_output_power(self) -> float:
        """Calculate total output power in Watts."""
        return sum(p.power.nominal_w for p in self.outputs)

    @property
    def total_input_power(self) -> float:
        """Calculate required input power based on output and efficiency."""
        return self.total_output_power / self.efficiency

    @property
    def is_isolated(self) -> bool:
        """Check if this is an isolated power supply."""
        return self.isolation_v is not None
