"""
PyOpenMagnetics Examples - Buck Inductor Design

This example demonstrates designing a buck converter output inductor:
1. Define operating conditions using the fluent API
2. Calculate inductance requirements
3. Get 50 Pareto-optimal designs
4. Generate visual reports
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.design import Design
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_buck_inductor():
    """
    Design a buck converter inductor for 12V to 3.3V @ 10A.

    Specifications:
    - Input: 12V (10-14V range)
    - Output: 3.3V @ 10A
    - Switching frequency: 500 kHz
    - Current ripple: 30% of Iout (3A p-p)
    - Required inductance: ~4.7 uH
    """
    print("=" * 60)
    print("BUCK INDUCTOR DESIGN")
    print("12V -> 3.3V @ 10A, 500 kHz")
    print("=" * 60)

    # Calculate expected values
    Vin = 12
    Vout = 3.3
    Iout = 10
    fsw = 500000
    ripple_ratio = 0.3

    D = Vout / Vin  # Duty cycle ~ 0.275
    delta_I = Iout * ripple_ratio  # 3A ripple
    L = (Vin - Vout) * D / (fsw * delta_I)  # ~4.7 uH

    print(f"\nCalculated parameters:")
    print(f"  Duty cycle: {D*100:.1f}%")
    print(f"  Current ripple: {delta_I:.1f} A p-p")
    print(f"  Required inductance: {L*1e6:.2f} uH")

    # Peak and RMS currents
    I_peak = Iout + delta_I/2  # 11.5A
    I_valley = Iout - delta_I/2  # 8.5A

    print(f"  Peak current: {I_peak:.1f} A")
    print(f"  Valley current: {I_valley:.1f} A")

    # Design using the fluent API
    design = (
        Design.buck()
        .vin(10, 14)               # 12V +/- tolerance
        .vout(Vout)                # 3.3V output
        .iout(Iout)                # 10A output current
        .fsw(fsw)                  # 500 kHz
        .ripple(ripple_ratio)      # 30% current ripple
        .prefer("efficiency")      # Optimize for lowest losses
        .ambient_temperature(50)   # 50C ambient
    )

    # Get design recommendations
    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found.")
        return None

    # Display results summary
    print_results_summary(results)

    # Generate visual reports
    specs = {
        "power_w": Vout * Iout,
        "frequency_hz": fsw,
        "topology": "buck",
        "inductance_uH": L * 1e6,
    }
    generate_example_report(
        results,
        "buck_inductor",
        "Buck Inductor 33W - Design Report",
        specs=specs
    )

    return results


def compare_wire_options():
    """Compare different wire options for high-current applications."""
    import PyOpenMagnetics

    print("\n" + "=" * 60)
    print("WIRE COMPARISON FOR 10A APPLICATION")
    print("=" * 60)

    # For 10A, we need substantial copper area
    # Target: ~4 A/mm2 current density -> ~2.5 mm2 area -> ~1.8mm diameter

    options = [
        ("Round 1.6mm", 0.0016, "round"),
        ("Round 1.8mm", 0.0018, "round"),
        ("Rectangular", 0.002, "rectangular"),
    ]

    print(f"\nComparing wires for 10A RMS at 100C:")
    print("-" * 50)

    current = {
        "processed": {
            "rms": 10,
            "peakToPeak": 3
        }
    }

    for name, dim, wire_type in options:
        try:
            wire = PyOpenMagnetics.find_wire_by_dimension(dim, wire_type, "IEC 60317")

            R_dc = PyOpenMagnetics.calculate_dc_resistance_per_meter(wire, 100)
            P_dc = PyOpenMagnetics.calculate_dc_losses_per_meter(wire, current, 100)

            print(f"\n{name}:")
            print(f"  R_dc: {R_dc*1000:.2f} mOhm/m")
            print(f"  P_dc (10A): {P_dc:.2f} W/m")

            # For rectangular, show dimensions
            if wire_type == "rectangular" and "conductingWidth" in wire:
                w = wire["conductingWidth"]["nominal"] * 1000
                h = wire["conductingHeight"]["nominal"] * 1000
                print(f"  Dimensions: {w:.2f} x {h:.2f} mm")

        except Exception:
            print(f"\n{name}: Not available")


if __name__ == "__main__":
    # Design the buck inductor
    results = design_buck_inductor()

    if results:
        best = results[0]
        print(f"\nRecommended: {best.core} with {best.material}")

    # Compare wire options
    compare_wire_options()

    print("\n[OK] Buck inductor design complete!")
