"""
PWM and Resonant topology dataclass models.

Provides structured representations of power converter topologies
with their key parameters and operating characteristics.
"""

from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum


class ModulationType(Enum):
    """Modulation type for power converters."""
    PWM = "pwm"
    PFM = "pfm"
    HYBRID = "hybrid"


class OperatingMode(Enum):
    """Inductor/transformer operating mode."""
    CCM = "ccm"      # Continuous conduction mode
    DCM = "dcm"      # Discontinuous conduction mode
    BCM = "bcm"      # Boundary/critical conduction mode


# =============================================================================
# PWM Topologies
# =============================================================================

@dataclass
class PWMTopology:
    """Base class for PWM-based topologies."""
    name: str
    fsw_hz: float                          # Switching frequency
    modulation: ModulationType = ModulationType.PWM
    mode: OperatingMode = OperatingMode.CCM


@dataclass
class BuckTopology(PWMTopology):
    """Buck (step-down) converter topology.

    Attributes:
        fsw_hz: Switching frequency in Hz
        duty_cycle: Calculated from Vout/Vin
        sync_rectification: Use synchronous rectification (SR MOSFET)
    """
    name: str = "buck"
    fsw_hz: float = 100e3
    duty_cycle: Optional[float] = None
    sync_rectification: bool = False


@dataclass
class BoostTopology(PWMTopology):
    """Boost (step-up) converter topology.

    Attributes:
        fsw_hz: Switching frequency in Hz
        duty_cycle: Calculated from 1 - Vin/Vout
    """
    name: str = "boost"
    fsw_hz: float = 100e3
    duty_cycle: Optional[float] = None


@dataclass
class BuckBoostTopology(PWMTopology):
    """Buck-Boost (inverting) converter topology.

    Can step voltage up or down with inverted polarity.

    Attributes:
        fsw_hz: Switching frequency in Hz
        duty_cycle: Calculated from Vout/(Vin + Vout)
    """
    name: str = "buck_boost"
    fsw_hz: float = 100e3
    duty_cycle: Optional[float] = None


@dataclass
class FlybackTopology(PWMTopology):
    """Flyback isolated converter topology.

    Most common isolated topology for <150W applications.

    Attributes:
        fsw_hz: Switching frequency in Hz
        turns_ratio: Primary to secondary turns ratio (Np/Ns)
        clamp_type: Snubber/clamp circuit type
        max_duty: Maximum duty cycle (typically 0.45-0.5)
    """
    name: str = "flyback"
    fsw_hz: float = 100e3
    turns_ratio: float = 1.0
    clamp_type: Literal["rcd", "active", "none"] = "rcd"
    max_duty: float = 0.5


@dataclass
class ForwardTopology(PWMTopology):
    """Forward isolated converter topology.

    Higher power density than flyback, requires output inductor.

    Attributes:
        fsw_hz: Switching frequency in Hz
        turns_ratio: Primary to secondary turns ratio
        variant: Single-switch, two-switch, or active clamp
        reset_method: Core reset mechanism
        max_duty: Maximum duty cycle
    """
    name: str = "forward"
    fsw_hz: float = 100e3
    turns_ratio: float = 1.0
    variant: Literal["single", "two_switch", "active_clamp"] = "two_switch"
    reset_method: Literal["tertiary", "active_clamp", "rcd"] = "tertiary"
    max_duty: float = 0.5


@dataclass
class PushPullTopology(PWMTopology):
    """Push-Pull isolated converter topology.

    Good for low input voltage applications (12V, 24V).

    Attributes:
        fsw_hz: Switching frequency in Hz
        turns_ratio: Primary to secondary turns ratio
        max_duty: Maximum duty cycle per switch (total effective = 2x)
    """
    name: str = "push_pull"
    fsw_hz: float = 100e3
    turns_ratio: float = 1.0
    max_duty: float = 0.45  # Per switch


@dataclass
class FullBridgeTopology(PWMTopology):
    """Full-Bridge isolated converter topology.

    High power topology with 4 switches on primary side.

    Attributes:
        fsw_hz: Switching frequency in Hz
        turns_ratio: Primary to secondary turns ratio
        phase_shift: Use phase-shifted ZVS control
        max_duty: Maximum effective duty cycle
    """
    name: str = "full_bridge"
    fsw_hz: float = 100e3
    turns_ratio: float = 1.0
    phase_shift: bool = False
    max_duty: float = 0.95


# =============================================================================
# Resonant Topologies
# =============================================================================

@dataclass
class ResonantTopology:
    """Base class for resonant topologies."""
    name: str
    f_res_hz: float                        # Resonant frequency
    fsw_min_hz: float                      # Min switching frequency
    fsw_max_hz: float                      # Max switching frequency


@dataclass
class LLCTopology(ResonantTopology):
    """LLC resonant converter topology.

    High efficiency topology using resonant tank circuit.
    Achieves ZVS for primary switches and ZCS for secondary rectifiers.

    Attributes:
        f_res_hz: Resonant frequency (calculated from Lr and Cr)
        fsw_min_hz: Minimum switching frequency
        fsw_max_hz: Maximum switching frequency
        Lm_h: Magnetizing inductance in Henries
        Lr_h: Resonant (leakage) inductance in Henries
        Cr_f: Resonant capacitance in Farads
        turns_ratio: Transformer turns ratio
        Q: Quality factor at full load
        k: Inductance ratio Lm/Lr
        gain_min: Minimum voltage gain
        gain_max: Maximum voltage gain
    """
    name: str = "llc"
    f_res_hz: float = 100e3
    fsw_min_hz: float = 80e3
    fsw_max_hz: float = 150e3
    Lm_h: float = 0.0                      # Magnetizing inductance
    Lr_h: float = 0.0                      # Resonant inductance
    Cr_f: float = 0.0                      # Resonant capacitance
    turns_ratio: float = 1.0
    Q: float = 0.3                         # Quality factor at full load
    k: float = 5.0                         # Inductance ratio Lm/Lr
    gain_min: float = 0.9                  # Min voltage gain
    gain_max: float = 1.1                  # Max voltage gain

    def calculate_resonant_frequency(self) -> float:
        """Calculate resonant frequency from Lr and Cr."""
        import math
        if self.Lr_h > 0 and self.Cr_f > 0:
            return 1 / (2 * math.pi * (self.Lr_h * self.Cr_f) ** 0.5)
        return self.f_res_hz


@dataclass
class LCCTopology(ResonantTopology):
    """LCC resonant converter topology.

    Uses series inductor with series and parallel capacitors.

    Attributes:
        f_res_hz: Resonant frequency
        fsw_min_hz: Minimum switching frequency
        fsw_max_hz: Maximum switching frequency
        Lr_h: Resonant inductance in Henries
        Cs_f: Series capacitance in Farads
        Cp_f: Parallel capacitance in Farads
        turns_ratio: Transformer turns ratio
    """
    name: str = "lcc"
    f_res_hz: float = 100e3
    fsw_min_hz: float = 80e3
    fsw_max_hz: float = 150e3
    Lr_h: float = 0.0
    Cs_f: float = 0.0                      # Series capacitance
    Cp_f: float = 0.0                      # Parallel capacitance
    turns_ratio: float = 1.0
