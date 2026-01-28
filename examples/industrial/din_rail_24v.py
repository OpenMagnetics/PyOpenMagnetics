"""
DIN Rail 24V Industrial Power Supply - Flyback Transformer Design

Application: Industrial automation 24V DC power supply
Real-world equivalents: Mean Well HDR series, Phoenix Contact QUINT

Specifications:
- Input: 85-264 VAC (universal input)
- Output: 24V @ 5A (120W)
- Switching frequency: 100 kHz
- Target efficiency: >89%
- Safety: IEC 62368-1 compliant
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from api.models import (
    VoltageSpec, CurrentSpec, FlybackTopology, PowerSupplySpec, PortSpec
)
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)

# Define specifications using datamodels
psu_spec = PowerSupplySpec(
    name="DIN Rail 24V Industrial PSU",
    inputs=[PortSpec(
        name="AC Input",
        voltage=VoltageSpec.ac(230, v_min_rms=85, v_max_rms=264),
        current=CurrentSpec.dc(0.8)
    )],
    outputs=[PortSpec(
        name="24V Output",
        voltage=VoltageSpec.dc(24, tolerance_pct=5),
        current=CurrentSpec.dc(5)
    )],
    efficiency=0.89,
    isolation_v=3000
)

topology = FlybackTopology(fsw_hz=100e3, max_duty=0.45)


def design_din_rail_24v():
    print("=" * 60)
    print("DIN RAIL 24V INDUSTRIAL PSU - FLYBACK TRANSFORMER")
    print("Input: 85-264 VAC | Output: 24V @ 5A (120W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .output(psu_spec.outputs[0].voltage.nominal, psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .efficiency(psu_spec.efficiency)
        .prefer("efficiency")      # Industrial values efficiency
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": psu_spec.total_output_power,
        "frequency_hz": topology.fsw_hz,
        "efficiency": psu_spec.efficiency,
        "topology": topology.name,
    }
    generate_example_report(
        results,
        "din_rail_24v",
        "DIN Rail 24V Industrial PSU - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_din_rail_24v()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
