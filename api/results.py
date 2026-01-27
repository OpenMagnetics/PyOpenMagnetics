"""
Human-readable design result formatting.

Converts raw MAS output into engineer-friendly result objects.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WindingInfo:
    """Information about a single winding."""
    name: str
    turns: int
    wire: str
    wire_diameter_mm: Optional[float] = None
    parallels: int = 1
    isolation_side: str = "primary"


@dataclass
class BOMItem:
    """Bill of materials item."""
    component: str
    part_number: str
    quantity: int
    description: str
    manufacturer: Optional[str] = None


@dataclass
class DesignResult:
    """Human-readable design result with all relevant magnetic component info."""
    core: str
    material: str
    core_family: str
    windings: list[WindingInfo]
    air_gap_mm: float
    gap_type: str = "subtractive"
    num_gaps: int = 1
    core_loss_w: float = 0.0
    copper_loss_w: float = 0.0
    total_loss_w: float = 0.0
    temp_rise_c: float = 0.0
    max_temperature_c: float = 0.0
    bpk_tesla: float = 0.0
    saturation_margin: float = 0.0
    inductance_h: float = 0.0
    height_mm: float = 0.0
    width_mm: float = 0.0
    depth_mm: float = 0.0
    weight_g: float = 0.0
    bom: list[BOMItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    _raw_mas: Optional[dict] = field(default=None, repr=False)

    @property
    def primary_turns(self) -> Optional[int]:
        for w in self.windings:
            if w.isolation_side == "primary" or w.name.lower() == "primary":
                return w.turns
        return self.windings[0].turns if self.windings else None

    @property
    def primary_wire(self) -> Optional[str]:
        for w in self.windings:
            if w.isolation_side == "primary" or w.name.lower() == "primary":
                return w.wire
        return self.windings[0].wire if self.windings else None

    @property
    def secondary_turns(self) -> Optional[int]:
        for w in self.windings:
            if w.isolation_side == "secondary" or w.name.lower() == "secondary":
                return w.turns
        return None

    @property
    def secondary_wire(self) -> Optional[str]:
        for w in self.windings:
            if w.isolation_side == "secondary" or w.name.lower() == "secondary":
                return w.wire
        return None

    @classmethod
    def from_mas(cls, mas: dict) -> "DesignResult":
        """Create DesignResult from MAS output dict."""
        magnetic = mas.get("magnetic", {})
        outputs = mas.get("outputs", {})
        core = magnetic.get("core", {})
        coil = magnetic.get("coil", {})

        # Core info
        func_desc = core.get("functionalDescription", {})
        shape_info = func_desc.get("shape", {})
        material_info = func_desc.get("material", {})

        if isinstance(shape_info, str):
            core_name, core_family = shape_info, shape_info.split()[0] if shape_info else ""
        else:
            core_name = shape_info.get("name", "Unknown")
            core_family = shape_info.get("family", core_name.split()[0] if core_name else "")

        material_name = material_info if isinstance(material_info, str) else material_info.get("name", "Unknown")

        # Gap info
        gapping = func_desc.get("gapping", [])
        total_gap, gap_type, num_gaps = 0.0, "subtractive", 0
        for gap in gapping:
            if gap.get("type") in ("subtractive", "additive"):
                total_gap += gap.get("length", 0)
                gap_type = gap.get("type", "subtractive")
                num_gaps += 1

        # Windings
        windings = []
        for w in coil.get("functionalDescription", []):
            wire_info = w.get("wire", {})
            wire_name = wire_info if isinstance(wire_info, str) else wire_info.get("name", "Unknown")
            wire_diameter = None
            if isinstance(wire_info, dict):
                conducting = wire_info.get("conductingDiameter", {})
                if isinstance(conducting, dict) and conducting.get("nominal"):
                    wire_diameter = conducting["nominal"] * 1000
            windings.append(WindingInfo(w.get("name", f"Winding {len(windings)+1}"),
                w.get("numberTurns", 0), wire_name, wire_diameter,
                w.get("numberParallels", 1), w.get("isolationSide", "primary")))

        # Losses from outputs
        core_loss, copper_loss, temp_rise, max_temp, bpk = 0.0, 0.0, 0.0, 0.0, 0.0
        if outputs:
            op_output = outputs[0] if isinstance(outputs, list) and outputs else outputs if isinstance(outputs, dict) else {}
            cl = op_output.get("coreLosses", {})
            if isinstance(cl, dict):
                core_loss = cl.get("coreLosses", 0.0) or 0.0
                bpk = cl.get("magneticFluxDensityPeak", 0.0) or 0.0
                temp_rise = cl.get("maximumCoreTemperatureRise", 0.0) or 0.0
                max_temp = cl.get("maximumCoreTemperature", 0.0) or 0.0
            elif isinstance(cl, (int, float)):
                core_loss = float(cl)
            wl = op_output.get("windingLosses", {})
            copper_loss = wl.get("windingLosses", 0.0) if isinstance(wl, dict) else float(wl) if isinstance(wl, (int, float)) else 0.0

        # Dimensions
        geom_desc = core.get("geometricalDescription", {})
        if isinstance(geom_desc, list) and geom_desc:
            geom_desc = geom_desc[0]
        elif not isinstance(geom_desc, dict):
            geom_desc = {}
        height = (geom_desc.get("height", 0.0) or 0.0) * 1000
        width = (geom_desc.get("width", 0.0) or 0.0) * 1000
        depth = (geom_desc.get("depth", 0.0) or 0.0) * 1000

        saturation_margin = max(0, (0.35 - bpk) / 0.35) if bpk > 0 else 0.0
        warnings = []
        if bpk > 0.3: warnings.append(f"High flux density ({bpk*1000:.0f} mT)")
        if temp_rise > 40: warnings.append(f"High temperature rise ({temp_rise:.0f}K)")
        if saturation_margin < 0.15: warnings.append("Low saturation margin")

        bom = [BOMItem("Core", core_name, 1, f"{material_name} ferrite core",
                       material_info.get("manufacturer") if isinstance(material_info, dict) else None)]
        for w in windings:
            bom.append(BOMItem(f"{w.name} Wire", w.wire, 1, f"{w.turns} turns, {w.parallels} parallel(s)"))

        return cls(core_name, material_name, core_family, windings, total_gap * 1000, gap_type, num_gaps,
                   core_loss, copper_loss, core_loss + copper_loss, temp_rise, max_temp, bpk,
                   saturation_margin, 0.0, height, width, depth, 0.0, bom, warnings, mas)

    def summary(self) -> str:
        lines = [f"Core: {self.core} ({self.material})", f"Air Gap: {self.air_gap_mm:.2f} mm", ""]
        for w in self.windings:
            line = f"{w.name}: {w.turns} turns of {w.wire}"
            if w.parallels > 1: line += f" ({w.parallels} parallel)"
            lines.append(line)
        lines.extend(["", f"Core Loss: {self.core_loss_w:.3f} W", f"Copper Loss: {self.copper_loss_w:.3f} W",
                      f"Total Loss: {self.total_loss_w:.3f} W", "", f"B_peak: {self.bpk_tesla*1000:.1f} mT",
                      f"Temp Rise: {self.temp_rise_c:.1f} K"])
        if self.warnings:
            lines.extend(["", "Warnings:"] + [f"  - {w}" for w in self.warnings])
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()
