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
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_poe_injector():
    print("=" * 60)
    print("POE INJECTOR - FLYBACK TRANSFORMER")
    print("Input: 36-57VDC | Output: 12V @ 2.5A (30W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_dc(36, 57)            # PoE input range
        .output(12, 2.5)           # 12V @ 2.5A = 30W
        .fsw(200e3)                # 200 kHz
        .efficiency(0.88)          # Target 88% efficiency
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
    results = design.solve(max_results=DEFAULT_MAX_RESULTS)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": 30,
        "frequency_hz": 200e3,
        "efficiency": 0.88,
        "topology": "flyback",
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
