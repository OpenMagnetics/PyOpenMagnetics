"""
48V to 12V 1kW DC-DC Converter - Buck Inductor Design

Application: Automotive mild-hybrid 48V to 12V auxiliary power converter
Real-world equivalents: Mercedes 48V EQ Boost, Audi e-tron DC-DC

Specifications:
- Input: 36-52V (48V nominal with battery variation)
- Output: 12V @ 83A (1kW)
- Switching frequency: 100 kHz
- Bidirectional capable
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from api.models import (
    VoltageSpec, CurrentSpec, BuckTopology, PowerSupplySpec, PortSpec
)
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)

# Define specifications using datamodels
psu_spec = PowerSupplySpec(
    name="Automotive 48V to 12V DC-DC",
    inputs=[PortSpec(
        name="48V Battery",
        voltage=VoltageSpec.dc_range(36, 52),
        current=CurrentSpec.dc(25)
    )],
    outputs=[PortSpec(
        name="12V Auxiliary",
        voltage=VoltageSpec.dc(12, tolerance_pct=5),
        current=CurrentSpec.dc(83)
    )],
    efficiency=0.95,
    isolation_v=None  # Non-isolated
)

topology = BuckTopology(fsw_hz=100e3)


def design_48v_to_12v_1kw():
    print("=" * 60)
    print("AUTOMOTIVE 48V TO 12V DC-DC - BUCK INDUCTOR")
    print("Input: 36-52V | Output: 12V @ 83A (1kW)")
    print("=" * 60)

    design = (
        Design.buck()
        .vin(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .vout(psu_spec.outputs[0].voltage.nominal)
        .iout(psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .ripple_ratio(0.3)         # 30% ripple ratio
        .prefer("efficiency")      # Automotive efficiency critical
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Inductance:    {params['inductance_uH']:.1f} uH")
    print(f"  Peak current:  {params['i_peak']:.1f} A")
    print(f"  Ripple (pp):   {params['i_ripple_pp']:.1f} A")
    print(f"  Duty cycle:    {params['duty_cycle']:.2%}")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": psu_spec.total_output_power,
        "frequency_hz": topology.fsw_hz,
        "topology": topology.name,
    }
    generate_example_report(
        results,
        "48v_to_12v_1kw",
        "Automotive 48V to 12V DC-DC - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_48v_to_12v_1kw()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
