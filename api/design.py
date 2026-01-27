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

from . import waveforms


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

    def solve(self, max_results: int = 30, core_mode: str = "available cores",
              verbose: bool = False, output_dir: Optional[str] = None,
              auto_relax: bool = False, relax_step: float = 0.1) -> list:
        """
        Run the design optimization and return results.

        Args:
            max_results: Maximum number of designs to return (default: 30)
            core_mode: "available cores" or "standard cores"
            verbose: If True, print progress information
            output_dir: If provided, save detailed results and plots here
            auto_relax: If True and no results found, automatically relax constraints
            relax_step: Relaxation step (0.1 = 10% increase per iteration)
        """
        import time
        import PyOpenMagnetics
        from .results import DesignResult

        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] Processing inputs...")

        start_time = time.time()
        processed = PyOpenMagnetics.process_inputs(self.to_mas())

        if verbose:
            process_time = time.time() - start_time
            print(f"[{time.strftime('%H:%M:%S')}] Input processing: {process_time:.2f}s")
            print(f"[{time.strftime('%H:%M:%S')}] Starting design optimization (this may take 1-2 minutes)...")
            print(f"[{time.strftime('%H:%M:%S')}] Searching {max_results} designs in '{core_mode}' mode...")

        opt_start = time.time()
        result = PyOpenMagnetics.calculate_advised_magnetics(processed, max_results, core_mode)
        opt_time = time.time() - opt_start

        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] Optimization complete: {opt_time:.2f}s")

        if isinstance(result, str):
            results = json.loads(result)
        elif isinstance(result, dict):
            data = result.get("data", result)
            if isinstance(data, str):
                if data.startswith("Exception:"):
                    if verbose:
                        print(f"[{time.strftime('%H:%M:%S')}] ERROR: {data}")
                        # Parse common errors and provide guidance
                        if "turns ratio" in data.lower() and "greater than 0" in data.lower():
                            print("\n" + "="*60)
                            print("DIAGNOSIS: Negative turns ratio detected")
                            print("="*60)
                            print("  This usually means a negative output voltage was specified.")
                            print("  Transformers use absolute voltage values - the polarity is")
                            print("  determined by winding direction, not the turns ratio.")
                            print("\n  FIX: Use positive voltage value, e.g.:")
                            print("       .output(8, 0.2)  instead of  .output(-8, 0.2)")
                            print("="*60 + "\n")
                    return []
                results = json.loads(data)
            else:
                results = data if isinstance(data, list) else [data]
        else:
            results = result if isinstance(result, list) else [result] if result else []

        design_results = [DesignResult.from_mas(r) for r in results if isinstance(r, dict) and "magnetic" in r]

        if verbose:
            total_time = time.time() - start_time
            print(f"[{time.strftime('%H:%M:%S')}] Found {len(design_results)} designs in {total_time:.2f}s total")

        # Auto-relax constraints if no results and auto_relax enabled
        if not design_results and auto_relax:
            design_results = self._try_relaxed_constraints(
                max_results, core_mode, verbose, relax_step
            )

        # Save results and generate Pareto plot if output_dir specified
        if output_dir and design_results:
            self._save_results(design_results, output_dir, verbose)

        return design_results

    def _save_results(self, results: list, output_dir: str, verbose: bool = False):
        """Save results to JSON and generate comprehensive design report."""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Save results as JSON
        results_data = []
        for i, r in enumerate(results):
            results_data.append({
                "rank": i + 1,
                "core": r.core,
                "material": r.material,
                "primary_turns": r.primary_turns,
                "primary_wire": r.primary_wire if hasattr(r, 'primary_wire') else "Unknown",
                "air_gap_mm": r.air_gap_mm,
                "core_loss_w": r.core_loss_w,
                "copper_loss_w": r.copper_loss_w,
                "total_loss_w": r.total_loss_w,
                "temp_rise_c": r.temp_rise_c if hasattr(r, 'temp_rise_c') else 0,
            })

        json_path = os.path.join(output_dir, "results.json")
        with open(json_path, "w") as f:
            json.dump(results_data, f, indent=2)

        if verbose:
            print(f"[Results saved to {json_path}]")

        # Generate comprehensive design report with matplotlib
        try:
            from .report import generate_design_report

            # Build specs dict from builder state
            specs = self._get_report_specs()

            # Generate title from topology
            topology_name = self.__class__.__name__.replace('Builder', '')
            title = f"{topology_name} Transformer Design Report"

            generate_design_report(results, output_dir, title, specs, verbose)

        except ImportError as e:
            if verbose:
                print(f"[Design report skipped - matplotlib not installed: {e}]")
            # Fall back to basic Pareto plot
            if len(results) >= 2:
                try:
                    self._generate_pareto_plot(results_data, output_dir, verbose)
                except ImportError:
                    pass

    def _get_report_specs(self) -> dict:
        """Get specifications dict for report generation."""
        specs = {}
        if hasattr(self, '_frequency'):
            specs['frequency_hz'] = self._frequency
        if hasattr(self, '_outputs') and self._outputs:
            # Handle both dict format {"voltage": v, "current": i} and tuple format (v, i)
            total_power = 0
            for output in self._outputs:
                if isinstance(output, dict):
                    total_power += output.get('voltage', 0) * output.get('current', 0)
                elif isinstance(output, (list, tuple)) and len(output) >= 2:
                    total_power += output[0] * output[1]
            specs['power_w'] = total_power
        if hasattr(self, '_efficiency'):
            specs['efficiency'] = self._efficiency
        return specs

    def _generate_pareto_plot(self, results_data: list, output_dir: str, verbose: bool = False):
        """Generate a Pareto front plot showing loss vs core size tradeoff."""
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import os

        # Extract data for plotting
        cores = [r["core"] for r in results_data]
        total_losses = [r["total_loss_w"] for r in results_data]
        core_losses = [r["core_loss_w"] for r in results_data]
        copper_losses = [r["copper_loss_w"] for r in results_data]

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Total loss ranking
        ax1 = axes[0]
        colors = ['green' if i == 0 else 'steelblue' for i in range(len(results_data))]
        bars = ax1.barh(range(len(cores)), total_losses, color=colors)
        ax1.set_yticks(range(len(cores)))
        ax1.set_yticklabels([f"{c}" for c in cores])
        ax1.set_xlabel('Total Loss (W)')
        ax1.set_title('Design Comparison - Total Loss')
        ax1.invert_yaxis()

        # Add value labels
        for bar, loss in zip(bars, total_losses):
            ax1.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                    f'{loss:.2f}W', va='center', fontsize=9)

        # Plot 2: Loss breakdown (stacked bar)
        ax2 = axes[1]
        y_pos = range(len(cores))
        ax2.barh(y_pos, core_losses, label='Core Loss', color='coral')
        ax2.barh(y_pos, copper_losses, left=core_losses, label='Copper Loss', color='steelblue')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(cores)
        ax2.set_xlabel('Loss (W)')
        ax2.set_title('Loss Breakdown')
        ax2.legend(loc='lower right')
        ax2.invert_yaxis()

        plt.tight_layout()

        plot_path = os.path.join(output_dir, "pareto_plot.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()

        if verbose:
            print(f"[Pareto plot saved to {plot_path}]")

    def _get_max_dimensions(self) -> Optional[dict]:
        if not any([self._max_width_mm, self._max_height_mm, self._max_depth_mm]):
            return None
        dims = {}
        if self._max_width_mm: dims["width"] = self._max_width_mm / 1000.0
        if self._max_height_mm: dims["height"] = self._max_height_mm / 1000.0
        if self._max_depth_mm: dims["depth"] = self._max_depth_mm / 1000.0
        return dims

    def _try_relaxed_constraints(self, max_results: int, core_mode: str,
                                  verbose: bool, relax_step: float) -> list:
        """Try relaxing constraints to find what's blocking the design."""
        import time
        import PyOpenMagnetics
        from .results import DesignResult

        if verbose:
            print(f"\n[{time.strftime('%H:%M:%S')}] No designs found. Analyzing constraints...")

        # Store original constraints
        orig_height = self._max_height_mm
        orig_width = self._max_width_mm
        orig_depth = self._max_depth_mm

        constraints_relaxed = []
        results = []

        # Try relaxing dimensions iteratively
        for iteration in range(1, 6):  # Max 5 iterations (50% relaxation)
            multiplier = 1 + (relax_step * iteration)

            if orig_height:
                self._max_height_mm = orig_height * multiplier
            if orig_width:
                self._max_width_mm = orig_width * multiplier
            if orig_depth:
                self._max_depth_mm = orig_depth * multiplier

            if verbose:
                relaxed = []
                if orig_height:
                    relaxed.append(f"height: {orig_height:.1f}→{self._max_height_mm:.1f}mm")
                if orig_width:
                    relaxed.append(f"width: {orig_width:.1f}→{self._max_width_mm:.1f}mm")
                if orig_depth:
                    relaxed.append(f"depth: {orig_depth:.1f}→{self._max_depth_mm:.1f}mm")
                print(f"[{time.strftime('%H:%M:%S')}] Iteration {iteration}: +{relax_step*iteration*100:.0f}% ({', '.join(relaxed)})")

            try:
                processed = PyOpenMagnetics.process_inputs(self.to_mas())
                result = PyOpenMagnetics.calculate_advised_magnetics(processed, max_results, core_mode)

                if isinstance(result, str):
                    parsed = json.loads(result)
                elif isinstance(result, dict):
                    data = result.get("data", result)
                    if isinstance(data, str):
                        if data.startswith("Exception:"):
                            continue
                        parsed = json.loads(data)
                    else:
                        parsed = data if isinstance(data, list) else [data]
                else:
                    parsed = result if isinstance(result, list) else [result] if result else []

                design_results = [DesignResult.from_mas(r) for r in parsed
                                  if isinstance(r, dict) and "magnetic" in r]

                if design_results:
                    if verbose:
                        print(f"[{time.strftime('%H:%M:%S')}] SUCCESS! Found {len(design_results)} designs")
                        print(f"\n{'='*60}")
                        print("BLOCKING CONSTRAINT ANALYSIS:")
                        print(f"{'='*60}")
                        if orig_height and self._max_height_mm > orig_height:
                            print(f"  HEIGHT was too restrictive:")
                            print(f"    Original: {orig_height:.1f} mm")
                            print(f"    Required: >{orig_height:.1f} mm (relaxed to {self._max_height_mm:.1f} mm)")
                        if orig_width and self._max_width_mm > orig_width:
                            print(f"  WIDTH was too restrictive:")
                            print(f"    Original: {orig_width:.1f} mm")
                            print(f"    Required: >{orig_width:.1f} mm (relaxed to {self._max_width_mm:.1f} mm)")
                        if orig_depth and self._max_depth_mm > orig_depth:
                            print(f"  DEPTH was too restrictive:")
                            print(f"    Original: {orig_depth:.1f} mm")
                            print(f"    Required: >{orig_depth:.1f} mm (relaxed to {self._max_depth_mm:.1f} mm)")
                        print(f"\nSmallest core found: {design_results[0].core}")
                        print(f"{'='*60}\n")

                    # Restore original constraints
                    self._max_height_mm = orig_height
                    self._max_width_mm = orig_width
                    self._max_depth_mm = orig_depth
                    return design_results

            except Exception as e:
                if verbose:
                    print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
                continue

        # Restore original constraints
        self._max_height_mm = orig_height
        self._max_width_mm = orig_width
        self._max_depth_mm = orig_depth

        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] Could not find designs even with +50% relaxation")
            print("\nPossible issues:")
            print("  - Frequency may be too high for available core materials")
            print("  - Power requirements may exceed smallest core capability")
            print("  - Try different core_mode ('standard cores' vs 'available cores')")

        return []


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
        insulation = waveforms.generate_insulation_requirements(self._isolation_type) if self._isolation_type else None
        return waveforms.generate_design_requirements(lm, turns_ratios, insulation=insulation,
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
            primary_current = waveforms.flyback_primary_current(vin, vout, pout, n, lm, self._frequency, self._efficiency, self._mode)
            primary_voltage = waveforms.rectangular_voltage(vin, 0, d, self._frequency)
            excitations = [{"name": "Primary", "current": primary_current, "voltage": primary_voltage}]
            for i, out in enumerate(self._outputs):
                sec_current = waveforms.flyback_secondary_current(vin, out["voltage"], out["current"],
                    n if i == 0 else n * (vout / out["voltage"]), lm, self._frequency, self._mode)
                excitations.append({"name": f"Secondary{i+1}" if len(self._outputs) > 1 else "Secondary", "current": sec_current})
            ops.append(waveforms.generate_operating_point(self._frequency, excitations, label, self._ambient_temp))
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
        return waveforms.generate_design_requirements(self._calculate_inductance(), [],
            max_dimensions=self._get_max_dimensions(), name="Buck Inductor")

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        L = self._calculate_inductance()
        ops = []
        for vin, label in [(self._vin_max, "Max Vin"), (self._vin_min, "Min Vin")]:
            if vin == self._vin_min and self._vin_max <= self._vin_min * 1.1: continue
            current = waveforms.buck_inductor_current(vin, self._vout, self._iout, L, self._frequency)
            voltage = waveforms.buck_inductor_voltage(vin, self._vout, self._frequency)
            ops.append(waveforms.generate_operating_point(self._frequency,
                [{"name": "Inductor", "current": current, "voltage": voltage}], label, self._ambient_temp))
        return ops

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        L = self._calculate_inductance()
        d_max = self._vout / self._vin_min  # Duty cycle at min Vin
        delta_i = self._ripple_ratio * self._iout
        i_peak = self._iout + delta_i / 2
        return {"vin_min": self._vin_min, "vin_max": self._vin_max, "vout": self._vout, "iout": self._iout,
                "inductance_uH": L * 1e6, "output_power_w": self._vout * self._iout, "frequency_kHz": self._frequency / 1000,
                "duty_cycle": d_max, "i_ripple_pp": delta_i, "i_peak": i_peak}


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
        return waveforms.generate_design_requirements(self._calculate_inductance(), [],
            max_dimensions=self._get_max_dimensions(), name="Boost Inductor")

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        L = self._calculate_inductance()
        ops = []
        for vin, label in [(self._vin_min, "Min Vin"), (self._vin_max, "Max Vin")]:
            if vin == self._vin_max and self._vin_max <= self._vin_min * 1.1: continue
            current = waveforms.boost_inductor_current(vin, self._vout, self._pout, L, self._frequency, self._efficiency)
            voltage = waveforms.boost_inductor_voltage(vin, self._vout, self._frequency)
            ops.append(waveforms.generate_operating_point(self._frequency,
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
        return waveforms.generate_design_requirements(self._inductance, [],
            max_dimensions=self._get_max_dimensions(), name="Inductor", tolerance=self._tolerance)

    def _generate_operating_points(self) -> list[dict]:
        self._validate_params()
        if self._waveform_type == "sinusoidal":
            current = waveforms.sinusoidal_current(self._iac_rms or 0.1, self._frequency, self._idc)
        else:
            current = waveforms.triangular_current(self._idc, self._iac_pp or 0.1, self._duty_cycle, self._frequency)
        return [waveforms.generate_operating_point(self._frequency, [{"name": "Inductor", "current": current}],
                                             "Operating Point", self._ambient_temp)]

    def get_calculated_parameters(self) -> dict:
        self._validate_params()
        return {"inductance_uH": self._inductance * 1e6, "i_dc": self._idc, "i_ripple_pp": self._iac_pp,
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
        return waveforms.generate_design_requirements(lm, turns_ratios, max_dimensions=self._get_max_dimensions(),
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
            primary_voltage = waveforms.rectangular_voltage(vin, 0, d, self._frequency)
            excitations = [{"name": "Primary", "current": primary_current, "voltage": primary_voltage}]
            for i, out in enumerate(self._outputs):
                sec_current = {"waveform": {"data": [out["current"], out["current"], 0, 0], "time": [0, ton, ton, period]}}
                excitations.append({"name": f"Secondary{i+1}" if len(self._outputs) > 1 else "Secondary", "current": sec_current})
            ops.append(waveforms.generate_operating_point(self._frequency, excitations, label, self._ambient_temp))
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
        return waveforms.generate_design_requirements(self._calculate_magnetizing_inductance(), turns_ratios,
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
        primary_current = waveforms.sinusoidal_current(i_pri_rms, self._resonant_freq)
        # LLC primary voltage is approximately sinusoidal at resonance
        v_pri_pk = vin_nom / 2  # Half-bridge LLC
        primary_voltage = waveforms.sinusoidal_current(v_pri_pk / math.sqrt(2), self._resonant_freq)  # RMS
        excitations = [{"name": "Primary", "current": primary_current, "voltage": primary_voltage}]
        for i, out in enumerate(self._outputs):
            i_sec_rms = out["current"] * math.pi / (2 * math.sqrt(2))
            excitations.append({"name": f"Secondary{i+1}" if len(self._outputs) > 1 else "Secondary",
                               "current": waveforms.sinusoidal_current(i_sec_rms, self._resonant_freq)})
        return [waveforms.generate_operating_point(self._resonant_freq, excitations, "Resonant Operation", self._ambient_temp)]

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
