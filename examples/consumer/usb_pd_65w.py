"""
USB PD 65W Laptop Charger - Flyback Transformer Design

Application: USB-C laptop charger with GaN technology
Real-world equivalents: MacBook Air charger, Dell XPS charger, Anker 65W GaN

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 20V @ 3.25A (65W)
- Switching frequency: 130 kHz (GaN compatible)
- Target efficiency: >90%
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
    name="USB PD 65W Laptop Charger",
    inputs=[PortSpec(
        name="AC Input",
        voltage=VoltageSpec.ac(230, v_min_rms=85, v_max_rms=265),
        current=CurrentSpec.dc(0.5)
    )],
    outputs=[PortSpec(
        name="USB-C Output",
        voltage=VoltageSpec.dc(20, tolerance_pct=5),
        current=CurrentSpec.dc(3.25)
    )],
    efficiency=0.90,
    isolation_v=3000
)

topology = FlybackTopology(fsw_hz=130e3, max_duty=0.45)


def design_usb_pd_65w():
    print("=" * 60)
    print("USB PD 65W LAPTOP CHARGER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 20V @ 3.25A (65W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .output(psu_spec.outputs[0].voltage.nominal, psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .efficiency(psu_spec.efficiency)
        .max_height(18)            # Compact GaN form factor
        .max_width(25)
        .prefer("efficiency")      # Efficiency is key for laptops
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

    # Generate reports
    specs = {
        "power_w": psu_spec.total_output_power,
        "frequency_hz": topology.fsw_hz,
        "efficiency": psu_spec.efficiency,
        "topology": topology.name,
    }
    generate_example_report(
        results,
        "usb_pd_65w",
        "USB PD 65W Charger - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_usb_pd_65w()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
