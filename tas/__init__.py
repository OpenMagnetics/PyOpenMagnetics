"""
TAS (Topology Agnostic Structure) - Power electronics interchange format.

A simplified format for basic DC-DC converter design exchange.
Uses waveforms as the universal language for topology-agnostic design.
"""

from tas.models.waveforms import TASWaveform, WaveformShape
from tas.models.components import (
    TASInductor,
    TASCapacitor,
    TASSwitch,
    TASDiode,
    TASMagnetic,
    TASComponentList,
)
from tas.models.inputs import (
    TASInputs,
    TASRequirements,
    TASOperatingPoint,
    TASModulation,
    ModulationType,
    ControlMode,
    OperatingMode,
)
from tas.models.outputs import TASOutputs, TASLossBreakdown, TASKPIs
from tas.models.tas_root import (
    TASDocument,
    TASMetadata,
    create_buck_tas,
    create_boost_tas,
    create_flyback_tas,
)

__all__ = [
    "TASDocument",
    "TASMetadata",
    "TASWaveform",
    "WaveformShape",
    "TASInductor",
    "TASCapacitor",
    "TASSwitch",
    "TASDiode",
    "TASMagnetic",
    "TASComponentList",
    "TASInputs",
    "TASRequirements",
    "TASOperatingPoint",
    "TASModulation",
    "ModulationType",
    "ControlMode",
    "OperatingMode",
    "TASOutputs",
    "TASLossBreakdown",
    "TASKPIs",
    "create_buck_tas",
    "create_boost_tas",
    "create_flyback_tas",
]

__version__ = "0.1.0"
