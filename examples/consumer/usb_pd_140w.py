"""
USB PD 140W High-Power Charger - Flyback Transformer Design

Application: High-power USB-C charger for gaming laptops and fast charging
Real-world equivalents: MacBook Pro 140W charger, Lenovo Legion charger

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 28V @ 5A (140W PD 3.1)
- Switching frequency: 100 kHz
- Target efficiency: >92%
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_usb_pd_140w():
    print("=" * 60)
    print("USB PD 140W HIGH-POWER CHARGER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 28V @ 5A (140W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(85, 265)           # Universal AC input
        .output(28, 5)             # 28V @ 5A = 140W (PD 3.1 EPR)
        .fsw(100e3)                # 100 kHz
        .efficiency(0.92)          # Target 92% efficiency
        .max_height(22)            # Larger form factor acceptable
        .max_width(35)
        .prefer("efficiency")
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
        "power_w": 140,
        "frequency_hz": 100e3,
        "efficiency": 0.92,
        "topology": "flyback",
    }
    generate_example_report(
        results,
        "usb_pd_140w",
        "USB PD 140W Charger - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_usb_pd_140w()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
