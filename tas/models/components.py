"""
TAS Component models - Simple component definitions for basic DC-DC converters.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ComponentType(Enum):
    """Component type enumeration."""
    INDUCTOR = "inductor"
    CAPACITOR = "capacitor"
    SWITCH = "switch"
    DIODE = "diode"
    MAGNETIC = "magnetic"


@dataclass
class TASInductor:
    """Inductor component."""
    name: str
    inductance: float = 0.0  # H
    dcr: float = 0.0  # Ohms
    saturation_current: Optional[float] = None  # A
    core_material: Optional[str] = None
    core_shape: Optional[str] = None
    description: str = ""

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": "inductor",
            "inductance": self.inductance,
            "dcr": self.dcr,
        }
        if self.saturation_current is not None:
            result["saturation_current"] = self.saturation_current
        if self.core_material:
            result["core_material"] = self.core_material
        if self.core_shape:
            result["core_shape"] = self.core_shape
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASInductor":
        return cls(
            name=d.get("name", ""),
            inductance=d.get("inductance", 0.0),
            dcr=d.get("dcr", 0.0),
            saturation_current=d.get("saturation_current"),
            core_material=d.get("core_material"),
            core_shape=d.get("core_shape"),
            description=d.get("description", ""),
        )


@dataclass
class TASCapacitor:
    """Capacitor component."""
    name: str
    capacitance: float = 0.0  # F
    esr: float = 0.0  # Ohms
    voltage_rating: Optional[float] = None  # V
    description: str = ""

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": "capacitor",
            "capacitance": self.capacitance,
            "esr": self.esr,
        }
        if self.voltage_rating is not None:
            result["voltage_rating"] = self.voltage_rating
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASCapacitor":
        return cls(
            name=d.get("name", ""),
            capacitance=d.get("capacitance", 0.0),
            esr=d.get("esr", 0.0),
            voltage_rating=d.get("voltage_rating"),
            description=d.get("description", ""),
        )


@dataclass
class TASSwitch:
    """Switch component (MOSFET)."""
    name: str
    rds_on: float = 0.0  # Ohms
    v_ds_max: Optional[float] = None  # V
    i_d_max: Optional[float] = None  # A
    qg_total: Optional[float] = None  # C
    description: str = ""

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": "switch",
            "rds_on": self.rds_on,
        }
        if self.v_ds_max is not None:
            result["v_ds_max"] = self.v_ds_max
        if self.i_d_max is not None:
            result["i_d_max"] = self.i_d_max
        if self.qg_total is not None:
            result["qg_total"] = self.qg_total
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASSwitch":
        return cls(
            name=d.get("name", ""),
            rds_on=d.get("rds_on", 0.0),
            v_ds_max=d.get("v_ds_max"),
            i_d_max=d.get("i_d_max"),
            qg_total=d.get("qg_total"),
            description=d.get("description", ""),
        )


@dataclass
class TASDiode:
    """Diode component."""
    name: str
    vf: float = 0.0  # V
    v_rrm: Optional[float] = None  # V
    description: str = ""

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": "diode",
            "vf": self.vf,
        }
        if self.v_rrm is not None:
            result["v_rrm"] = self.v_rrm
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASDiode":
        return cls(
            name=d.get("name", ""),
            vf=d.get("vf", 0.0),
            v_rrm=d.get("v_rrm"),
            description=d.get("description", ""),
        )


@dataclass
class TASMagnetic:
    """Magnetic component (transformer)."""
    name: str
    magnetizing_inductance: float = 0.0  # H
    leakage_inductance: float = 0.0  # H
    turns_ratio: float = 1.0
    core_material: Optional[str] = None
    core_shape: Optional[str] = None
    description: str = ""

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": "magnetic",
            "magnetizing_inductance": self.magnetizing_inductance,
            "leakage_inductance": self.leakage_inductance,
            "turns_ratio": self.turns_ratio,
        }
        if self.core_material:
            result["core_material"] = self.core_material
        if self.core_shape:
            result["core_shape"] = self.core_shape
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASMagnetic":
        return cls(
            name=d.get("name", ""),
            magnetizing_inductance=d.get("magnetizing_inductance", 0.0),
            leakage_inductance=d.get("leakage_inductance", 0.0),
            turns_ratio=d.get("turns_ratio", 1.0),
            core_material=d.get("core_material"),
            core_shape=d.get("core_shape"),
            description=d.get("description", ""),
        )


@dataclass
class TASComponentList:
    """Container for all components."""
    inductors: List[TASInductor] = field(default_factory=list)
    capacitors: List[TASCapacitor] = field(default_factory=list)
    switches: List[TASSwitch] = field(default_factory=list)
    diodes: List[TASDiode] = field(default_factory=list)
    magnetics: List[TASMagnetic] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {}
        if self.inductors:
            result["inductors"] = [c.to_dict() for c in self.inductors]
        if self.capacitors:
            result["capacitors"] = [c.to_dict() for c in self.capacitors]
        if self.switches:
            result["switches"] = [c.to_dict() for c in self.switches]
        if self.diodes:
            result["diodes"] = [c.to_dict() for c in self.diodes]
        if self.magnetics:
            result["magnetics"] = [c.to_dict() for c in self.magnetics]
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASComponentList":
        return cls(
            inductors=[TASInductor.from_dict(c) for c in d.get("inductors", [])],
            capacitors=[TASCapacitor.from_dict(c) for c in d.get("capacitors", [])],
            switches=[TASSwitch.from_dict(c) for c in d.get("switches", [])],
            diodes=[TASDiode.from_dict(c) for c in d.get("diodes", [])],
            magnetics=[TASMagnetic.from_dict(c) for c in d.get("magnetics", [])],
        )

    @property
    def all_components(self) -> list:
        """Get all components as a flat list."""
        return self.inductors + self.capacitors + self.switches + self.diodes + self.magnetics
