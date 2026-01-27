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
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_din_rail_24v():
    print("=" * 60)
    print("DIN RAIL 24V INDUSTRIAL PSU - FLYBACK TRANSFORMER")
    print("Input: 85-264 VAC | Output: 24V @ 5A (120W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(85, 264)           # Universal AC input
        .output(24, 5)             # 24V @ 5A = 120W
        .fsw(100e3)                # 100 kHz
        .efficiency(0.89)          # Target 89% efficiency
        .prefer("efficiency")      # Industrial values efficiency
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": 120,
        "frequency_hz": 100e3,
        "efficiency": 0.89,
        "topology": "flyback",
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
