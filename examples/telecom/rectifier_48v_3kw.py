"""
Telecom Rectifier 48V 3kW - LLC Resonant Converter Design

Application: Telecom base station power supply module
Real-world equivalents: Eltek Flatpack2, Delta DPR series

Specifications:
- Input: 380-420VDC (from PFC stage)
- Output: 48V @ 62.5A (3kW)
- Resonant frequency: 100 kHz
- Target efficiency: >96% (LLC resonant)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_rectifier_48v_3kw():
    print("=" * 60)
    print("TELECOM RECTIFIER 48V 3KW - LLC TRANSFORMER")
    print("Input: 380-420VDC | Output: 48V @ 62.5A (3kW)")
    print("=" * 60)

    design = (
        Design.llc()
        .vin_dc(380, 420)          # DC bus from PFC
        .output(48, 62.5)          # 48V @ 62.5A = 3kW
        .resonant_frequency(100e3) # 100 kHz resonant
        .quality_factor(0.3)       # Q factor
        .prefer("efficiency")
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
        "power_w": 3000,
        "frequency_hz": 100e3,
        "efficiency": 0.96,
        "topology": "LLC",
    }
    generate_example_report(
        results,
        "rectifier_48v_3kw",
        "Telecom Rectifier 48V 3kW - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_rectifier_48v_3kw()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
