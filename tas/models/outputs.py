"""
TAS Output models - Simplified results for basic DC-DC converters.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TASLossBreakdown:
    """Loss breakdown by component."""
    core_loss: float = 0.0  # W
    winding_loss: float = 0.0  # W
    switch_conduction: float = 0.0  # W
    switch_switching: float = 0.0  # W
    diode_conduction: float = 0.0  # W
    capacitor_esr: float = 0.0  # W

    @property
    def total(self) -> float:
        """Total losses."""
        return (self.core_loss + self.winding_loss +
                self.switch_conduction + self.switch_switching +
                self.diode_conduction + self.capacitor_esr)

    def to_dict(self) -> dict:
        return {
            "core_loss": self.core_loss,
            "winding_loss": self.winding_loss,
            "switch_conduction": self.switch_conduction,
            "switch_switching": self.switch_switching,
            "diode_conduction": self.diode_conduction,
            "capacitor_esr": self.capacitor_esr,
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TASLossBreakdown":
        return cls(
            core_loss=d.get("core_loss", 0.0),
            winding_loss=d.get("winding_loss", 0.0),
            switch_conduction=d.get("switch_conduction", 0.0),
            switch_switching=d.get("switch_switching", 0.0),
            diode_conduction=d.get("diode_conduction", 0.0),
            capacitor_esr=d.get("capacitor_esr", 0.0),
        )


@dataclass
class TASKPIs:
    """Key performance indicators."""
    efficiency: float = 0.0  # 0-1
    power_density: Optional[float] = None  # W/cm³
    cost: Optional[float] = None  # USD

    def to_dict(self) -> dict:
        result = {"efficiency": self.efficiency}
        if self.power_density is not None:
            result["power_density"] = self.power_density
        if self.cost is not None:
            result["cost"] = self.cost
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASKPIs":
        return cls(
            efficiency=d.get("efficiency", 0.0),
            power_density=d.get("power_density"),
            cost=d.get("cost"),
        )


@dataclass
class TASOutputs:
    """Simplified outputs section."""
    losses: Optional[TASLossBreakdown] = None
    kpis: Optional[TASKPIs] = None
    notes: str = ""

    def to_dict(self) -> dict:
        result = {}
        if self.losses:
            result["losses"] = self.losses.to_dict()
        if self.kpis:
            result["kpis"] = self.kpis.to_dict()
        if self.notes:
            result["notes"] = self.notes
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASOutputs":
        return cls(
            losses=TASLossBreakdown.from_dict(d["losses"]) if d.get("losses") else None,
            kpis=TASKPIs.from_dict(d["kpis"]) if d.get("kpis") else None,
            notes=d.get("notes", ""),
        )
