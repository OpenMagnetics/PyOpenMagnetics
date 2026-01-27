"""
Fluent Design API for magnetic component design.

Provides topology builders for flyback, buck, boost, forward, LLC, and inductor designs.

Example:
    from api.design import Design
    results = Design.buck().vin(12,24).vout(5).iout(3).fsw(500e3).solve()
"""

import math
import json
from abc import ABC, abstractmethod
from typing import Self, Optional, Any
from dataclasses import dataclass

from . import mas


@dataclass
class DesignSpec:
    """Intermediate representation of a design specification."""
    topology: str
    params: dict
    constraints: dict
    operating_points: list


# =============================================================================
# Base Builder
# =============================================================================

class TopologyBuilder(ABC):
    """Abstract base class for power converter topology builders."""

    def __init__(self):
        self._params: dict[str, Any] = {}
        self._constraints: dict[str, Any] = {}
        self._core_families: Optional[list[str]] = None
        self._max_height_mm: Optional[float] = None
        self._max_width_mm: Optional[float] = None
        self._max_depth_mm: Optional[float] = None
        self._priority: str = "efficiency"
        self._ambient_temp: float = 25.0
        self._max_temp_rise: Optional[float] = None

    def max_height(self, mm: float) -> Self:
        self._max_height_mm = mm
        return self

    def max_width(self, mm: float) -> Self:
        self._max_width_mm = mm
        return self

    def max_depth(self, mm: float) -> Self:
        self._max_depth_mm = mm
        return self

    def max_dimensions(self, width_mm: float, height_mm: float, depth_mm: float) -> Self:
        self._max_width_mm, self._max_height_mm, self._max_depth_mm = width_mm, height_mm, depth_mm
        return self

    def core_families(self, families: list[str]) -> Self:
        self._core_families = families
        return self

    def prefer(self, priority: str) -> Self:
        if priority not in ("efficiency", "cost", "size"):
            raise ValueError(f"Invalid priority: {priority}")
        self._priority = priority
        return self

    def ambient_temperature(self, celsius: float) -> Self:
        self._ambient_temp = celsius
        return self

    def max_temperature_rise(self, kelvin: float) -> Self:
        self._max_temp_rise = kelvin
        return self

    @abstractmethod
    def _generate_operating_points(self) -> list[dict]: ...
    @abstractmethod
    def _generate_design_requirements(self) -> dict: ...
    @abstractmethod
    def _topology_name(self) -> str: ...

    def build(self) -> DesignSpec:
        return DesignSpec(self._topology_name(), self._params.copy(),
                          self._constraints.copy(), self._generate_operating_points())

    def to_mas(self) -> dict:
        return {"designRequirements": self._generate_design_requirements(),
                "operatingPoints": self._generate_operating_points()}

    def solve(self, max_results: int = 5, core_mode: str = "available cores") -> list:
        import PyOpenMagnetics
        from .results import DesignResult

        processed = PyOpenMagnetics.process_inputs(self.to_mas())
        result = PyOpenMagnetics.calculate_advised_magnetics(processed, max_results, core_mode)

        if isinstance(result, str):
            results = json.loads(result)
        elif isinstance(result, dict):
            data = result.get("data", result)
            if isinstance(data, str):
                if data.startswith("Exception:"):
                    return []
                results = json.loads(data)
            else:
                results = data if isinstance(data, list) else [data]
        else:
            results = result if isinstance(result, list) else [result] if result else []

        return [DesignResult.from_mas(r) for r in results if isinstance(r, dict) and "magnetic" in r]

    def _get_max_dimensions(self) -> Optional[dict]:
        if not any([self._max_width_mm, self._max_height_mm, self._max_depth_mm]):
            return None
        dims = {}
        if self._max_width_mm: dims["width"] = self._max_width_mm / 1000.0
        if self._max_height_mm: dims["height"] = self._max_height_mm / 1000.0
        if self._max_depth_mm: dims["depth"] = self._max_depth_mm / 1000.0
        return dims


# =============================================================================
# Flyback Builder
# =============================================================================

class FlybackBuilder(TopologyBuilder):
    """Flyback transformer design builder."""

    def __init__(self):
        super().__init__()
        self._vin_min: Optional[float] = None
        self._vin_max: Optional[float] = None
        self._vin_is_ac: bool = False
        self._outputs: list[dict] = []
        self._frequency: float = 100e3
        self._efficiency: float = 0.85
        self._mode: str = "ccm"
        self._isolation_type: Optional[str] = None
        self._magnetizing_inductance: Optional[float] = None
        self._turns_ratio: Optional[float] = None

    def _topology_name(self) -> str: return "flyback"

    def vin_ac(self, min_v: float, max_v: float) -> Self:
        self._vin_min, self._vin_max, self._vin_is_ac = min_v, max_v, True
        return self

    def vin_dc(self, min_v: float, max_v: Optional[float] = None) -> Self:
        self._vin_min, self._vin_max, self._vin_is_ac = min_v, max_v or min_v, False
        return self

    def output(self, voltage: float, current: float) -> Self:
        self._outputs.append({"voltage": voltage, "current": current})
        return self

    def fsw(self, frequency: float) -> Self:
        self._frequency = frequency
        return self

    def efficiency(self, target: float) -> Self:
        self._efficiency = target
        return self

    def mode(self, mode: str) -> Self:
        if mode not in ("ccm", "dcm", "bcm"):
            raise ValueError(f"Invalid mode: {mode}")
        self._mode = mode
        return self

    def isolation(self, insulation_type: str, standard: Optional[str] = None) -> Self:
        self._isolation_type = insulation_type
        return self

    def _get_dc_bus_voltages(self) -> tuple[float, float]:
        if self._vin_min is None:
            raise ValueError("Input voltage not specified")
        if self._vin_is_ac:
            return self._vin_min * math.sqrt(2) * 0.9, self._vin_max * math.sqrt(2)
        return self._vin_min, self._vin_max

    def _calculate_total_output_power(self) -> float:
        if not self._outputs:
            raise ValueError("No outputs specified")
        return sum(out["voltage"] * out["current"] for out in self._outputs)

    def _calculate_turns_ratio(self, vin: float) -> float:
        if self._turns_ratio: return self._turns_ratio
        return (vin * 0.45) / (self._outputs[0]["voltage"] * 0.55)

    def _calculate_duty_cycle(self, vin: float, n: float) -> float:
        vout_reflected = n * self._outputs[0]["voltage"]
        return vout_reflected / (vin + vout_reflected)

    def _calculate_magnetizing_inductance(self, vin_min: float, n: float) -> float:
        if self._magnetizing_inductance: return self._magnetizing_inductance
        pout = self._calculate_total_output_power()
        pin = pout / self._efficiency
        d = self._calculate_duty_cycle(vin_min, n)
        ton = d / self._frequency
        if self._mode == "dcm":
            ipk_target = 2.5 * (pin / vin_min)
            return vin_min * ton / ipk_target
        else:
            i_avg = pin / vin_min
            delta_i = 0.3 * 2 * i_avg
            return vin_min * ton / delta_i

    def _generate_design_requirements(self) -> dict:
        vin_min, vin_max = self._get_dc_bus_voltages()
        n = self._calculate_turns_ratio(vin_min)
        lm = self._calculate_magnetizing_inductance(vin_min, n)
        turns_ratios = [n]
        if len(self._outputs) > 1:
            for out in self._outputs[1:]:
                turns_ratios.append(self._outputs[0]["voltage"] / out["voltage"])
        insulation = mas.generate_insulation_requirements(self._isolation_type) if self._isolation_type else None
        return mas.generate_design_requirements(lm, turns_ratios, insulation=insulation,
            max_dimensions=self._get_max_dimensions(), name="Flyback Transformer")

    def _generate_operating_points(self) -> list[dict]:
        vin_min, vin_max = self._get_dc_bus_voltages()
        n = self._calculate_turns_ratio(vin_min)
        lm = self._calculate_magnetizing_inductance(vin_min, n)
        pout = self._calculate_total_output_power()
        vout = self._outputs[0]["voltage"]
        ops = []
        for vin, label in [(vin_min, "Low Line"), (vin_max, "High Line")]:
            if vin == vin_max and vin_max <= vin_min * 1.1: continue
            d = self._calculate_duty_cycle(vin, n)
            primary_current = mas.flyback_primary_current(vin, vout, pout, n, lm, self._frequency, self._efficiency, self._mode)
            primary_voltage = mas.rectangular_voltage(vin, 0, d, self._frequency)
            excitations = [{"name": "Primary", "current": primary_current, "voltage": primary_voltage}]
            for i, out in enumerate(self._outputs):
                sec_current = mas.flyback_secondary_current(vin, out["voltage"], out["current"],
                    n if i == 0 else n * (vout / out["voltage"]), lm, self._frequency, self._mode)
                excitations.append({"name": f"Secondary{i+1}" if len(self._outputs) > 1 else "Secondary", "current": sec_current})
            ops.append(mas.generate_operating_point(self._frequency, excitations, label, self._ambient_temp))
        return ops

    def get_calculated_parameters(self) -> dict:
        vin_min, vin_max = self._get_dc_bus_voltages()
        n = self._calculate_turns_ratio(vin_min)
        lm = self._calculate_magnetizing_inductance(vin_min, n)
        return {"vin_dc_min": vin_min, "vin_dc_max": vin_max, "turns_ratio": n,
                "magnetizing_inductance_uH": lm * 1e6, "duty_cycle_low_line": self._calculate_duty_cycle(vin_min, n),
                "output_power_w": self._calculate_total_output_power(), "frequency_kHz": self._frequency / 1000}


# =============================================================================
# Buck Builder
# =============================================================================

class BuckBuilder(TopologyBuilder):
    """Buck converter inductor design builder."""

    def __init__(self):
        super().__init__()
        self._vin_min: Optional[float] = None
        self._vin_max: Optional[float] = None
        self._vout: Optional[float] = None
        self._iout: Optional[float] = None
        self._frequency: float = 100e3
        self._ripple_ratio: float = 0.3
        self._inductance: Optional[float] = None

    def _topology_name(self) -> str: return "buck"

    def vin(self, min_v: float, max_v: Optional[float] = None) -> Self:
        self._vin_min, self._vin_max = min_v, max_v or min_v
        return self

    def vout(self, voltage: float) -> Self:
        self._vout = voltage
        return self

    def iout(self, current: float) -> Self:
        self._iout = current
        return self

    def fsw(self, frequency: float) -> Self:
        self._frequency = frequency
        return self

    def ripple_ratio(self, ratio: float) -> Self:
        self._ripple_ratio = ratio
        return self

    def inductance(self, value: float) -> Self:
        self._inductance = value
        return self

    def _validate_params(self):
        if self._vin_min is None: raise ValueError("Input voltage not specified")
        if self._vout is None: raise ValueError("Output voltage not specified")
        if self._iout is None: raise ValueError("Output current not specified")
        if self._vout >= self._vin_min: raise ValueError("Buck: Vout must be less than Vin_min")

    def _calculate_inductance(self) -> float:
        if self._inductance: return self._inductance
        d = self._vout / self._vin_max
        ton = d / self._frequency
        delta_i = self._ripple_ratio * self._iout
        return (self._vin_max - self._vout) * ton / delta_i

    def _generate_design_requirements(self) -> dict:
        self._validate_params()
        return mas.generate_design_requirements(self._calculate_inductance(), [],
            max_dimensions=self._get_max_dimensions(), name="Buck Inductor")

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        L = self._calculate_inductance()
        ops = []
        for vin, label in [(self._vin_max, "Max Vin"), (self._vin_min, "Min Vin")]:
            if vin == self._vin_min and self._vin_max <= self._vin_min * 1.1: continue
            current = mas.buck_inductor_current(vin, self._vout, self._iout, L, self._frequency)
            voltage = mas.buck_inductor_voltage(vin, self._vout, self._frequency)
            ops.append(mas.generate_operating_point(self._frequency,
                [{"name": "Inductor", "current": current, "voltage": voltage}], label, self._ambient_temp))
        return ops

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        L = self._calculate_inductance()
        return {"vin_min": self._vin_min, "vin_max": self._vin_max, "vout": self._vout, "iout": self._iout,
                "inductance_uH": L * 1e6, "output_power_w": self._vout * self._iout, "frequency_kHz": self._frequency / 1000}


# =============================================================================
# Boost Builder
# =============================================================================

class BoostBuilder(TopologyBuilder):
    """Boost converter inductor design builder."""

    def __init__(self):
        super().__init__()
        self._vin_min: Optional[float] = None
        self._vin_max: Optional[float] = None
        self._vout: Optional[float] = None
        self._pout: Optional[float] = None
        self._frequency: float = 100e3
        self._ripple_ratio: float = 0.3
        self._inductance: Optional[float] = None
        self._efficiency: float = 0.9

    def _topology_name(self) -> str: return "boost"

    def vin(self, min_v: float, max_v: Optional[float] = None) -> Self:
        self._vin_min, self._vin_max = min_v, max_v or min_v
        return self

    def vout(self, voltage: float) -> Self:
        self._vout = voltage
        return self

    def pout(self, power: float) -> Self:
        self._pout = power
        return self

    def fsw(self, frequency: float) -> Self:
        self._frequency = frequency
        return self

    def efficiency(self, target: float) -> Self:
        self._efficiency = target
        return self

    def _validate_params(self):
        if self._vin_min is None: raise ValueError("Input voltage not specified")
        if self._vout is None: raise ValueError("Output voltage not specified")
        if self._pout is None: raise ValueError("Output power not specified")
        if self._vout <= self._vin_max: raise ValueError("Boost: Vout must be greater than Vin_max")

    def _calculate_inductance(self) -> float:
        if self._inductance: return self._inductance
        d = 1 - (self._vin_min / self._vout)
        ton = d / self._frequency
        pin = self._pout / self._efficiency
        iin_avg = pin / self._vin_min
        delta_i = self._ripple_ratio * iin_avg
        return self._vin_min * ton / delta_i

    def _generate_design_requirements(self) -> dict:
        self._validate_params()
        return mas.generate_design_requirements(self._calculate_inductance(), [],
            max_dimensions=self._get_max_dimensions(), name="Boost Inductor")

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        L = self._calculate_inductance()
        ops = []
        for vin, label in [(self._vin_min, "Min Vin"), (self._vin_max, "Max Vin")]:
            if vin == self._vin_max and self._vin_max <= self._vin_min * 1.1: continue
            current = mas.boost_inductor_current(vin, self._vout, self._pout, L, self._frequency, self._efficiency)
            voltage = mas.boost_inductor_voltage(vin, self._vout, self._frequency)
            ops.append(mas.generate_operating_point(self._frequency,
                [{"name": "Inductor", "current": current, "voltage": voltage}], label, self._ambient_temp))
        return ops

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        return {"vin_min": self._vin_min, "vin_max": self._vin_max, "vout": self._vout, "pout": self._pout,
                "inductance_uH": self._calculate_inductance() * 1e6, "frequency_kHz": self._frequency / 1000}


# =============================================================================
# Inductor Builder
# =============================================================================

class InductorBuilder(TopologyBuilder):
    """Standalone inductor design builder."""

    def __init__(self):
        super().__init__()
        self._inductance: Optional[float] = None
        self._tolerance: float = 0.1
        self._idc: float = 0.0
        self._iac_pp: float = 0.0
        self._iac_rms: float = 0.0
        self._frequency: float = 100e3
        self._duty_cycle: float = 0.5
        self._waveform_type: str = "triangular"

    def _topology_name(self) -> str: return "inductor"

    def inductance(self, value: float, tolerance: float = 0.1) -> Self:
        self._inductance, self._tolerance = value, tolerance
        return self

    def idc(self, current: float) -> Self:
        self._idc = current
        return self

    def iac_pp(self, current: float) -> Self:
        self._iac_pp = current
        self._iac_rms = current / (2 * math.sqrt(3))
        return self

    def fsw(self, frequency: float) -> Self:
        self._frequency = frequency
        return self

    def duty_cycle(self, duty: float) -> Self:
        self._duty_cycle = duty
        return self

    def _validate_params(self):
        if self._inductance is None: raise ValueError("Inductance not specified")

    def _generate_design_requirements(self) -> dict:
        self._validate_params()
        return mas.generate_design_requirements(self._inductance, [],
            max_dimensions=self._get_max_dimensions(), name="Inductor", tolerance=self._tolerance)

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        if self._waveform_type == "sinusoidal":
            current = mas.sinusoidal_current(self._iac_rms or 0.1, self._frequency, self._idc)
        else:
            current = mas.triangular_current(self._idc, self._iac_pp or 0.1, self._duty_cycle, self._frequency)
        return [mas.generate_operating_point(self._frequency, [{"name": "Inductor", "current": current}],
                                             "Operating Point", self._ambient_temp)]

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        return {"inductance_uH": self._inductance * 1e6, "idc": self._idc, "iac_pp": self._iac_pp,
                "i_peak": self._idc + self._iac_pp / 2, "frequency_kHz": self._frequency / 1000}


# =============================================================================
# Forward Builder
# =============================================================================

class ForwardBuilder(TopologyBuilder):
    """Forward converter transformer design builder."""

    def __init__(self):
        super().__init__()
        self._variant: str = "two_switch"
        self._vin_min: Optional[float] = None
        self._vin_max: Optional[float] = None
        self._outputs: list[dict] = []
        self._frequency: float = 100e3
        self._efficiency: float = 0.9
        self._max_duty: float = 0.45
        self._magnetizing_inductance: Optional[float] = None

    def _topology_name(self) -> str: return f"forward_{self._variant}"

    def variant(self, variant_type: str) -> Self:
        if variant_type not in ("single_switch", "two_switch", "active_clamp"):
            raise ValueError(f"Invalid variant: {variant_type}")
        self._variant = variant_type
        self._max_duty = 0.45 if variant_type == "single_switch" else 0.5
        return self

    def vin_dc(self, min_v: float, max_v: Optional[float] = None) -> Self:
        self._vin_min, self._vin_max = min_v, max_v or min_v
        return self

    def output(self, voltage: float, current: float) -> Self:
        self._outputs.append({"voltage": voltage, "current": current})
        return self

    def fsw(self, frequency: float) -> Self:
        self._frequency = frequency
        return self

    def _validate_params(self):
        if self._vin_min is None: raise ValueError("Input voltage not specified")
        if not self._outputs: raise ValueError("No outputs specified")

    def _calculate_turns_ratio(self) -> float:
        return self._outputs[0]["voltage"] / (self._vin_max * self._max_duty)

    def _calculate_magnetizing_inductance(self) -> float:
        if self._magnetizing_inductance: return self._magnetizing_inductance
        pout = sum(o["voltage"] * o["current"] for o in self._outputs)
        pin = pout / self._efficiency
        i_pri_avg = pin / self._vin_min
        i_mag_target = 0.05 * i_pri_avg
        ton = self._max_duty / self._frequency
        return self._vin_min * ton / (2 * i_mag_target)

    def _generate_design_requirements(self) -> dict:
        self._validate_params()
        n = self._calculate_turns_ratio()
        lm = self._calculate_magnetizing_inductance()
        turns_ratios = [n] + [n * (o["voltage"] / self._outputs[0]["voltage"]) for o in self._outputs[1:]]
        return mas.generate_design_requirements(lm, turns_ratios, max_dimensions=self._get_max_dimensions(),
                                                name=f"Forward Transformer ({self._variant})")

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        n = self._calculate_turns_ratio()
        lm = self._calculate_magnetizing_inductance()
        ops = []
        for vin, label in [(self._vin_min, "Min Vin"), (self._vin_max, "Max Vin")]:
            if vin == self._vin_max and self._vin_max <= self._vin_min * 1.1: continue
            d = min((self._outputs[0]["voltage"] / vin) / n, self._max_duty)
            ton, period = d / self._frequency, 1 / self._frequency
            i_sec = self._outputs[0]["current"]
            i_pri = i_sec * n
            delta_i_mag = vin * ton / lm
            primary_current = {"waveform": {"data": [i_pri - delta_i_mag/2, i_pri + delta_i_mag/2, 0, 0],
                                            "time": [0, ton, ton, period]}}
            primary_voltage = mas.rectangular_voltage(vin, 0, d, self._frequency)
            excitations = [{"name": "Primary", "current": primary_current, "voltage": primary_voltage}]
            for i, out in enumerate(self._outputs):
                sec_current = {"waveform": {"data": [out["current"], out["current"], 0, 0], "time": [0, ton, ton, period]}}
                excitations.append({"name": f"Secondary{i+1}" if len(self._outputs) > 1 else "Secondary", "current": sec_current})
            ops.append(mas.generate_operating_point(self._frequency, excitations, label, self._ambient_temp))
        return ops

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        return {"variant": self._variant, "turns_ratio": self._calculate_turns_ratio(),
                "magnetizing_inductance_mH": self._calculate_magnetizing_inductance() * 1e3,
                "frequency_kHz": self._frequency / 1000}


# =============================================================================
# LLC Builder
# =============================================================================

class LLCBuilder(TopologyBuilder):
    """LLC resonant converter transformer design builder."""

    def __init__(self):
        super().__init__()
        self._vin_min: Optional[float] = None
        self._vin_max: Optional[float] = None
        self._outputs: list[dict] = []
        self._resonant_freq: Optional[float] = None
        self._magnetizing_inductance: Optional[float] = None
        self._leakage_inductance: Optional[float] = None
        self._quality_factor: float = 0.3
        self._efficiency: float = 0.95

    def _topology_name(self) -> str: return "llc"

    def vin_dc(self, min_v: float, max_v: Optional[float] = None) -> Self:
        self._vin_min, self._vin_max = min_v, max_v or min_v
        return self

    def output(self, voltage: float, current: float) -> Self:
        self._outputs.append({"voltage": voltage, "current": current})
        return self

    def resonant_frequency(self, freq: float) -> Self:
        self._resonant_freq = freq
        return self

    def quality_factor(self, q: float) -> Self:
        self._quality_factor = q
        return self

    def _validate_params(self):
        if self._vin_min is None: raise ValueError("Input voltage not specified")
        if not self._outputs: raise ValueError("No outputs specified")
        if self._resonant_freq is None: raise ValueError("Resonant frequency not specified")

    def _calculate_turns_ratio(self) -> float:
        vin_nom = (self._vin_min + self._vin_max) / 2
        return vin_nom / (2 * self._outputs[0]["voltage"])

    def _calculate_leakage_inductance(self) -> float:
        if self._leakage_inductance: return self._leakage_inductance
        n = self._calculate_turns_ratio()
        rac = (8 / (math.pi**2)) * (n**2) * self._outputs[0]["voltage"] / self._outputs[0]["current"]
        return self._quality_factor * rac / (2 * math.pi * self._resonant_freq)

    def _calculate_magnetizing_inductance(self) -> float:
        if self._magnetizing_inductance: return self._magnetizing_inductance
        return self._calculate_leakage_inductance() * 7

    def _generate_design_requirements(self) -> dict:
        self._validate_params()
        n = self._calculate_turns_ratio()
        turns_ratios = [n] + [n * (o["voltage"] / self._outputs[0]["voltage"]) for o in self._outputs[1:]]
        return mas.generate_design_requirements(self._calculate_magnetizing_inductance(), turns_ratios,
            leakage_inductance=self._calculate_leakage_inductance(), max_dimensions=self._get_max_dimensions(),
            name="LLC Transformer")

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        n = self._calculate_turns_ratio()
        lm = self._calculate_magnetizing_inductance()
        i_load_reflected = (self._outputs[0]["current"] * 2 * math.sqrt(2) / math.pi) / n
        vin_nom = (self._vin_min + self._vin_max) / 2
        i_mag_pk = vin_nom / (4 * lm * self._resonant_freq)
        i_pri_rms = math.sqrt((i_load_reflected / math.sqrt(2))**2 + (i_mag_pk / math.sqrt(2))**2)
        primary_current = mas.sinusoidal_current(i_pri_rms, self._resonant_freq)
        excitations = [{"name": "Primary", "current": primary_current}]
        for i, out in enumerate(self._outputs):
            i_sec_rms = out["current"] * math.pi / (2 * math.sqrt(2))
            excitations.append({"name": f"Secondary{i+1}" if len(self._outputs) > 1 else "Secondary",
                               "current": mas.sinusoidal_current(i_sec_rms, self._resonant_freq)})
        return [mas.generate_operating_point(self._resonant_freq, excitations, "Resonant Operation", self._ambient_temp)]

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        return {"turns_ratio": self._calculate_turns_ratio(),
                "magnetizing_inductance_uH": self._calculate_magnetizing_inductance() * 1e6,
                "leakage_inductance_uH": self._calculate_leakage_inductance() * 1e6,
                "resonant_frequency_kHz": self._resonant_freq / 1000}


# =============================================================================
# Design Factory
# =============================================================================

class Design:
    """Factory class for creating topology builders."""

    @staticmethod
    def flyback() -> FlybackBuilder: return FlybackBuilder()

    @staticmethod
    def buck() -> BuckBuilder: return BuckBuilder()

    @staticmethod
    def boost() -> BoostBuilder: return BoostBuilder()

    @staticmethod
    def inductor() -> InductorBuilder: return InductorBuilder()

    @staticmethod
    def forward() -> ForwardBuilder: return ForwardBuilder()

    @staticmethod
    def llc() -> LLCBuilder: return LLCBuilder()
