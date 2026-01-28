"""
Boost Half-Bridge Inductor with Multiple Operating Points

Application: 48V automotive mild hybrid / EV auxiliary power system
Real-world equivalents: Continental 48V DC-DC, Valeo i-StARS

This example demonstrates designing an inductor for a half-bridge boost
converter that must operate efficiently across multiple voltage and power
conditions - a critical requirement for automotive applications.

Topology: Half-bridge boost (bidirectional)
- Charges 800V HV battery from 400V intermediate
- Can also operate in buck mode for regeneration

Operating Conditions:
- Mode 1: Low voltage boost (400V -> 800V, 10kW)
- Mode 2: High voltage pass-through (800V -> 800V, light)
- Mode 3: Medium voltage boost (200V -> 400V, 20kW)

Each mode has different thermal and efficiency weights based on
real-world usage patterns (highway cruise vs city driving vs charging).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import math
from dataclasses import dataclass
from api.design import Design
from api.models import (
    VoltageSpec, CurrentSpec, BoostTopology, PowerSupplySpec, PortSpec
)
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)

# Define specifications using datamodels
psu_spec = PowerSupplySpec(
    name="Boost Half-Bridge Multi-OP Inductor",
    inputs=[PortSpec(
        name="Low Voltage Bus",
        voltage=VoltageSpec.dc_range(200, 450),
        current=CurrentSpec.dc(100)
    )],
    outputs=[PortSpec(
        name="High Voltage Bus",
        voltage=VoltageSpec.dc(850, tolerance_pct=5),
        current=CurrentSpec.dc(50)
    )],
    efficiency=0.98,
    isolation_v=None  # Non-isolated
)

topology = BoostTopology(fsw_hz=100e3)

@dataclass
class OperatingPoint:
    """Operating point definition for multi-mode analysis."""
    name: str
    v_low: float      # Lower voltage side (V)
    v_high: float     # Higher voltage side (V)
    power: float      # Transfer power (W)
    weight: float     # Efficiency weighting factor
    frequency: float  # Switching frequency (Hz)

    @property
    def duty_cycle(self) -> float:
        """Calculate duty cycle for boost operation."""
        return self.v_low / self.v_high

    @property
    def i_dc(self) -> float:
        """Calculate DC (average) inductor current."""
        return self.power / self.v_low

    def inductor_ripple_pp(self, inductance: float) -> float:
        """Calculate peak-to-peak current ripple."""
        # For half-bridge boost: delta_i = V_low * D / (L * f)
        return self.v_low * self.duty_cycle / (inductance * self.frequency)


def calculate_boost_waveforms(op: OperatingPoint, inductance: float) -> dict:
    """
    Calculate inductor waveforms for a boost converter operating point.

    Returns detailed waveform metrics for analysis and comparison.
    """
    period = 1.0 / op.frequency
    duty = op.duty_cycle
    t_on = duty * period

    # Current calculations
    i_dc = op.i_dc
    delta_i = op.inductor_ripple_pp(inductance)
    i_min = i_dc - delta_i / 2
    i_max = i_dc + delta_i / 2

    # Voltage waveform (inductor sees)
    # During switch ON: V_L = V_high - V_low (negative for boost)
    # During switch OFF: V_L = V_high (positive)
    v_on = op.v_high - op.v_low   # Actually the voltage during OFF in half-bridge
    v_off = -op.v_low             # During ON

    # RMS calculations
    i_rms = math.sqrt(i_dc**2 + (delta_i**2) / 12)  # Triangular ripple
    v_rms = math.sqrt(duty * v_on**2 + (1-duty) * v_off**2)

    return {
        "name": op.name,
        "weight": op.weight,
        "v_low": op.v_low,
        "v_high": op.v_high,
        "power": op.power,
        "duty_cycle": duty,
        "frequency": op.frequency,
        "i_dc": i_dc,
        "i_ripple_pp": delta_i,
        "i_min": i_min,
        "i_max": i_max,
        "i_rms": i_rms,
        "i_peak": i_max,
        "v_rms": v_rms,
    }


def design_multi_op_inductor():
    """Design inductor optimized for multiple operating points."""
    print("=" * 70)
    print("BOOST HALF-BRIDGE INDUCTOR - MULTI-OPERATING POINT DESIGN")
    print("Application: 48V Mild Hybrid / EV Auxiliary Converter")
    print("=" * 70)

    # Define operating points with real-world weighting
    operating_points = [
        OperatingPoint(
            name="V_ls_P_max (City driving)",
            v_low=200,
            v_high=850,
            power=20000,  # 20kW
            weight=0.2,   # 20% of time
            frequency=100e3,
        ),
        OperatingPoint(
            name="V_hs_P_max (Highway cruise)",
            v_low=425,
            v_high=850,
            power=42500,  # 42.5kW
            weight=0.4,   # 40% of time
            frequency=100e3,
        ),
        OperatingPoint(
            name="V_ls_P_ls (Light load)",
            v_low=200,
            v_high=400,
            power=20000,  # 20kW at reduced voltage
            weight=0.4,   # 40% of time
            frequency=100e3,
        ),
    ]

    # Print operating points
    print("\nOperating Points:")
    print("-" * 70)
    for op in operating_points:
        print(f"\n{op.name}:")
        print(f"  V_low: {op.v_low}V -> V_high: {op.v_high}V")
        print(f"  Power: {op.power/1000:.1f}kW, Weight: {op.weight*100:.0f}%")
        print(f"  Duty cycle: {op.duty_cycle*100:.1f}%")
        print(f"  I_dc: {op.i_dc:.1f}A")

    # Calculate critical inductance (BCM at worst case)
    # L_crit = V_low * D * (1-D) / (2 * f * I_out)
    worst_case = operating_points[0]  # Low voltage, high power
    L_crit = (worst_case.v_low * worst_case.duty_cycle * (1 - worst_case.duty_cycle) /
              (2 * worst_case.frequency * worst_case.i_dc))

    # Target inductance (typically 2-3x critical for CCM)
    L_target = 2.5 * L_crit

    print(f"\n" + "-" * 70)
    print("INDUCTANCE CALCULATION")
    print("-" * 70)
    print(f"\nCritical inductance (BCM): {L_crit*1e6:.2f} uH")
    print(f"Target inductance (CCM):   {L_target*1e6:.2f} uH")

    # Analyze waveforms at target inductance
    print(f"\n" + "-" * 70)
    print("WAVEFORM ANALYSIS")
    print("-" * 70)

    waveforms = []
    for op in operating_points:
        wf = calculate_boost_waveforms(op, L_target)
        waveforms.append(wf)

        print(f"\n{wf['name']}:")
        print(f"  I_dc:        {wf['i_dc']:.1f} A")
        print(f"  I_ripple_pp: {wf['i_ripple_pp']:.1f} A")
        print(f"  I_rms:       {wf['i_rms']:.1f} A")
        print(f"  I_peak:      {wf['i_peak']:.1f} A")
        print(f"  V_rms:       {wf['v_rms']:.0f} V")

    # Calculate weighted RMS values
    weighted_i_rms_sq = sum(wf['weight'] * wf['i_rms']**2 for wf in waveforms)
    weighted_i_rms = math.sqrt(weighted_i_rms_sq)
    max_i_peak = max(wf['i_peak'] for wf in waveforms)
    max_i_dc = max(wf['i_dc'] for wf in waveforms)

    print(f"\n" + "-" * 70)
    print("AGGREGATED REQUIREMENTS")
    print("-" * 70)
    print(f"\nWeighted I_rms:  {weighted_i_rms:.1f} A")
    print(f"Max I_peak:      {max_i_peak:.1f} A")
    print(f"Max I_dc:        {max_i_dc:.1f} A")

    # Material recommendations for high DC bias applications
    print(f"\n" + "-" * 70)
    print("RECOMMENDED MATERIALS")
    print("-" * 70)
    print("\nFor high DC bias inductors, consider powder core materials:")
    print("  - High Flux (Magnetics): Best DC bias, Bsat=1.5T")
    print("  - Sendust/Kool Mu: Good all-around, Bsat=1.0T")
    print("  - Mega Flux/XFlux: Highest saturation, Bsat=1.6T")
    print("  - MPP: Lowest loss but lower DC bias capability")

    # Design using PyOpenMagnetics
    print(f"\n" + "-" * 70)
    print("DESIGN SOLUTION")
    print("-" * 70)

    # Use the dominant operating point for primary design
    dominant_op = max(operating_points, key=lambda x: x.weight * x.power)

    design = (
        Design.inductor()
        .inductance(L_target, tolerance=0.2)  # ±20% tolerance
        .idc(max_i_dc)
        .iac_pp(max(wf['i_ripple_pp'] for wf in waveforms))
        .fsw(100e3)
        .ambient_temperature(85)  # Automotive high temp
        .max_temperature_rise(40)  # Conservative for reliability
        .prefer("efficiency")
    )

    params = design.get_calculated_parameters()
    print(f"\nDesign Parameters:")
    print(f"  Target L:    {params['inductance_uH']:.1f} uH")
    print(f"  I_dc:        {params['i_dc']:.1f} A")
    print(f"  I_ripple:    {params['i_ripple_pp']:.1f} A")
    print(f"  I_peak:      {params['i_peak']:.1f} A")

    print(f"\nSearching for optimal core designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("\nNo suitable designs found with standard cores.")
        print("Consider:")
        print("  - Custom toroidal powder core")
        print("  - Multiple paralleled smaller cores")
        print("  - Planar transformer construction")
        return None

    print_results_summary(results)

    specs = {
        "power_w": psu_spec.total_output_power,
        "frequency_hz": topology.fsw_hz,
        "topology": "half_bridge_boost",
    }
    generate_example_report(
        results,
        "boost_half_bridge_multi_op",
        "Boost Half-Bridge Multi-OP Inductor - Design Report",
        specs=specs
    )

    return results[0] if results else None


def main():
    """Run the multi-operating point design example."""
    best = design_multi_op_inductor()

    if best:
        print("=" * 70)
        print("FINAL RECOMMENDATION")
        print("=" * 70)
        print(f"\nCore:      {best.core}")
        print(f"Material:  {best.material}")
        print(f"Turns:     {best.primary_turns}")
        print(f"Wire:      {best.primary_wire}")
        print(f"Air gap:   {best.air_gap_mm:.2f} mm")
        print(f"Total loss: {best.total_loss_w:.2f} W")

        print("\nAutomotive Notes:")
        print("  - Verify AEC-Q200 qualification for core/wire")
        print("  - Design for -40C to +125C operation")
        print("  - Include potting for vibration resistance")
        print("  - Consider thermal interface to heatsink")


if __name__ == "__main__":
    main()
