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
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_laptop_19v_90w():
    print("=" * 60)
    print("LAPTOP 19V 90W ADAPTER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 19V @ 4.74A (90W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(85, 265)           # Universal AC input
        .output(19, 4.74)          # 19V @ 4.74A = 90W
        .fsw(65e3)                 # 65 kHz (traditional)
        .efficiency(0.88)          # Target 88% efficiency
        .prefer("cost")            # Cost-optimized design
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
        "power_w": 90,
        "frequency_hz": 65e3,
        "efficiency": 0.88,
        "topology": "flyback",
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
