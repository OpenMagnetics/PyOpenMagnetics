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
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_48v_to_12v_1kw():
    print("=" * 60)
    print("AUTOMOTIVE 48V TO 12V DC-DC - BUCK INDUCTOR")
    print("Input: 36-52V | Output: 12V @ 83A (1kW)")
    print("=" * 60)

    design = (
        Design.buck()
        .vin(36, 52)               # 48V system with variation
        .vout(12)                  # 12V auxiliary bus
        .iout(83)                  # 83A for 1kW
        .fsw(100e3)                # 100 kHz
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
    results = design.solve(max_results=DEFAULT_MAX_RESULTS)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": 1000,
        "frequency_hz": 100e3,
        "topology": "buck",
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
