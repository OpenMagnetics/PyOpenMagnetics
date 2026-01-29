"""
Data models for magnetic component design.

This module provides dataclass models for:
- PWM and resonant topologies (Buck, Boost, Flyback, LLC, etc.)
- Voltage, current, and power specifications
- Operating points and waveforms
"""

from .topology import (
    ModulationType,
    OperatingMode,
    PWMTopology,
    BuckTopology,
    BoostTopology,
    BuckBoostTopology,
    FlybackTopology,
    ForwardTopology,
    PushPullTopology,
    FullBridgeTopology,
    ResonantTopology,
    LLCTopology,
    LCCTopology,
)

from .specs import (
    ACDCType,
    VoltageSpec,
    CurrentSpec,
    PowerSpec,
    PortSpec,
    PowerSupplySpec,
)

from .operating_point import (
    WaveformType,
    Waveform,
    WindingExcitation,
    OperatingPointModel,
)

__all__ = [
    # Topology enums
    "ModulationType",
    "OperatingMode",
    # PWM topologies
    "PWMTopology",
    "BuckTopology",
    "BoostTopology",
    "BuckBoostTopology",
    "FlybackTopology",
    "ForwardTopology",
    "PushPullTopology",
    "FullBridgeTopology",
    # Resonant topologies
    "ResonantTopology",
    "LLCTopology",
    "LCCTopology",
    # Specification enums
    "ACDCType",
    # Specification dataclasses
    "VoltageSpec",
    "CurrentSpec",
    "PowerSpec",
    "PortSpec",
    "PowerSupplySpec",
    # Operating point enums
    "WaveformType",
    # Operating point dataclasses
    "Waveform",
    "WindingExcitation",
    "OperatingPointModel",
]
