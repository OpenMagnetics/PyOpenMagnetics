"""
PoE Injector - Flyback Transformer Design

Application: Power over Ethernet injector for access points/cameras
Real-world equivalents: Ubiquiti PoE adapters, Cisco PoE injectors

Specifications:
- Input: 36-57VDC (PoE input range)
- Output: 12V @ 2.5A (30W) isolated
- Switching frequency: 200 kHz
- Isolation: Functional (IEEE 802.3af/at)
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
    name="PoE Injector",
    inputs=[PortSpec(
        name="PoE Input",
        voltage=VoltageSpec.dc_range(36, 57),
        current=CurrentSpec.dc(1.0)
    )],
    outputs=[PortSpec(
        name="Isolated Output",
        voltage=VoltageSpec.dc(12, tolerance_pct=5),
        current=CurrentSpec.dc(2.5)
    )],
    efficiency=0.88,
    isolation_v=1500
)

topology = FlybackTopology(fsw_hz=200e3, max_duty=0.45)


def design_poe_injector():
    print("=" * 60)
    print("POE INJECTOR - FLYBACK TRANSFORMER")
    print("Input: 36-57VDC | Output: 12V @ 2.5A (30W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_dc(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .output(psu_spec.outputs[0].voltage.nominal, psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .efficiency(psu_spec.efficiency)
        .max_height(12)            # Compact PoE module
        .max_width(15)
        .prefer("size")
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
        "poe_injector",
        "PoE Injector - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_poe_injector()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
