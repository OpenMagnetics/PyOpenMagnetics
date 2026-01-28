"""
Laptop 19V 90W Adapter - Flyback Transformer Design

Application: Traditional laptop power adapter (barrel connector)
Real-world equivalents: HP/Dell/Lenovo 90W laptop adapters

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 19V @ 4.74A (90W)
- Switching frequency: 65 kHz (classic design)
- Target efficiency: >88%
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
    name="Laptop 19V 90W Adapter",
    inputs=[PortSpec(
        name="AC Input",
        voltage=VoltageSpec.ac(230, v_min_rms=85, v_max_rms=265),
        current=CurrentSpec.dc(0.7)
    )],
    outputs=[PortSpec(
        name="DC Output",
        voltage=VoltageSpec.dc(19, tolerance_pct=5),
        current=CurrentSpec.dc(4.74)
    )],
    efficiency=0.88,
    isolation_v=3000
)

topology = FlybackTopology(fsw_hz=65e3, max_duty=0.45)


def design_laptop_19v_90w():
    print("=" * 60)
    print("LAPTOP 19V 90W ADAPTER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 19V @ 4.74A (90W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .output(psu_spec.outputs[0].voltage.nominal, psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .efficiency(psu_spec.efficiency)
        .prefer("cost")            # Cost-optimized design
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
        "laptop_19v_90w",
        "Laptop 19V 90W Adapter - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_laptop_19v_90w()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
