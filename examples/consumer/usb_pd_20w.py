"""
USB PD 20W Charger - Flyback Transformer Design

Application: Compact USB Power Delivery charger supporting 5V/9V/12V profiles
Real-world equivalents: Apple 20W USB-C charger, Samsung 25W charger

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 12V @ 1.67A (20W, PD profile)
- Switching frequency: 100 kHz
- Target efficiency: >87%
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
    name="USB PD 20W Charger",
    inputs=[PortSpec(
        name="AC Input",
        voltage=VoltageSpec.ac(230, v_min_rms=85, v_max_rms=265),
        current=CurrentSpec.dc(0.3)
    )],
    outputs=[PortSpec(
        name="USB-C Output",
        voltage=VoltageSpec.dc(12, tolerance_pct=5),
        current=CurrentSpec.dc(1.67)
    )],
    efficiency=0.87,
    isolation_v=3000
)

topology = FlybackTopology(fsw_hz=100e3, max_duty=0.45)


def design_usb_pd_20w():
    print("=" * 60)
    print("USB PD 20W CHARGER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 12V @ 1.67A (20W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .output(psu_spec.outputs[0].voltage.nominal, psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .efficiency(psu_spec.efficiency)
        .max_height(15)            # Compact form factor (mm)
        .max_width(20)
        .prefer("size")            # Optimize for small size
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found. Try relaxing constraints.")
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
        "usb_pd_20w",
        "USB PD 20W Charger - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_usb_pd_20w()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
