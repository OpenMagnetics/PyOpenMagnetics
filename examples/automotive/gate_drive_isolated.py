"""
Isolated Gate Drive Transformer - Flyback Design

Application: Isolated gate driver for SiC/GaN power modules in EV inverters
Real-world equivalents: Infineon EiceDRIVER, Texas Instruments UCC21750

Specifications:
- Input: 12V DC (from auxiliary supply)
- Output: +15V (positive gate drive) and 8V (for -8V negative bias)
- Switching frequency: 500 kHz
- Isolation: Reinforced, 5kV

Note: The -8V output is achieved by reversing the winding polarity during assembly.
      Both outputs are specified as positive values; the transformer design is the same.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_gate_drive_isolated():
    print("=" * 60)
    print("ISOLATED GATE DRIVE TRANSFORMER")
    print("Input: 12V DC | Output: +15V / -8V isolated")
    print("=" * 60)
    print("\nNote: Two independent secondary windings:")
    print("  - Secondary 1: 15V @ 0.5A (positive gate drive)")
    print("  - Secondary 2: 8V @ 0.2A (negative bias, reverse polarity)")

    design = (
        Design.flyback()
        .vin_dc(10, 14)            # 12V +/- tolerance
        .output(15, 0.5)           # Secondary 1: +15V gate drive
        .output(8, 0.2)            # Secondary 2: 8V (connect reversed for -8V)
        .fsw(500e3)                # 500 kHz (good balance of size/losses)
        .efficiency(0.80)          # Lower efficiency acceptable at low power
        .max_height(12)            # Compact
        .max_width(15)
        .prefer("size")
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True, auto_relax=True)

    if not results:
        print("No suitable designs found even after relaxation.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": 9.1,  # 15V*0.5A + 8V*0.2A
        "frequency_hz": 500e3,
        "efficiency": 0.80,
        "topology": "flyback",
    }
    generate_example_report(
        results,
        "gate_drive_isolated",
        "Isolated Gate Drive Transformer - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_gate_drive_isolated()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
        print("\nWinding Instructions:")
        print("  1. Wind primary as specified")
        print("  2. Secondary 1 (+15V): Wind in same direction as primary")
        print("  3. Secondary 2 (-8V): Wind in OPPOSITE direction for negative output")
        print("  4. Use margin tape for isolation between primary and secondaries")
