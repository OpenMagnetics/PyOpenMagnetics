"""
Boost Inductor Design for DC-DC Converter

Application: 400V->800V boost stage for EV charger / solar inverter
Real-world equivalents: EV on-board charger boost stage, solar MPPT converter

This example demonstrates designing a high-power boost inductor for automotive
and industrial DC-DC applications using the PyOpenMagnetics fluent API.

Specifications:
- Input voltage: 200-450V DC (battery or PV array)
- Output voltage: 800V DC bus
- Output power: 10kW
- Switching frequency: 100kHz
- Target efficiency: >98%

Core material considerations:
- Powder cores (Sendust, High Flux, Mega Flux) recommended for:
  - High DC bias capability
  - Distributed gap reduces fringing EMI
  - Good thermal performance
- Ferrite with gap possible but has higher fringing losses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)

def design_boost_inductor():
    """Design a boost inductor for EV charger application."""
    print("=" * 70)
    print("BOOST INDUCTOR DESIGN - EV CHARGER / SOLAR INVERTER")
    print("Input: 200-450V DC | Output: 800V DC | Power: 10kW @ 100kHz")
    print("=" * 70)

    # Design using the fluent API
    design = (
        Design.boost()
        .vin(200, 450)             # 200-450V DC input range
        .vout(800)                 # 800V DC output
        .pout(10000)               # 10kW output power
        .fsw(100e3)                # 100kHz switching frequency
        .efficiency(0.98)          # Target 98% efficiency
        .prefer("efficiency")      # Optimize for lowest losses
        .ambient_temperature(70)   # 70C ambient (automotive)
        .max_temperature_rise(50)  # Max 50K rise
    )

    # Get calculated parameters
    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Input voltage range:  {params['vin_min']:.0f} - {params['vin_max']:.0f} V")
    print(f"  Output voltage:       {params['vout']:.0f} V")
    print(f"  Output power:         {params['pout']:.0f} W")
    print(f"  Inductance:           {params['inductance_uH']:.1f} uH")
    print(f"  Frequency:            {params['frequency_kHz']:.0f} kHz")

    # Calculate DC current at worst case (low line, full load)
    i_dc = params['pout'] / 0.98 / params['vin_min']  # Pin / Vin
    print(f"\n  DC current (low line): {i_dc:.1f} A")

    # Material recommendations for boost inductors
    print("\n" + "-" * 70)
    print("MATERIAL RECOMMENDATIONS")
    print("-" * 70)
    print("\nFor high DC bias boost inductors:")
    print("  Balanced:   Sendust/Kool Mu 60u - good all-around")
    print("  Low loss:   MPP 60u - lowest core loss")
    print("  High bias:  High Flux 60u or Mega Flux 60u - best saturation")

    # Run the design solver
    print("\n" + "-" * 70)
    print("DESIGN RESULTS")
    print("-" * 70)
    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")

    results = design.solve(max_results=DEFAULT_MAX_RESULTS)

    if not results:
        print("No suitable designs found.")
        print("\nPossible reasons:")
        print("  - Core database may not have suitable powder cores")
        print("  - Try relaxing constraints (temperature, dimensions)")
        return None

    print_results_summary(results)

    specs = {
        "power_w": 10000,
        "frequency_hz": 100e3,
        "efficiency": 0.98,
        "topology": "boost",
    }
    generate_example_report(
        results,
        "boost_inductor_design",
        "Boost Inductor 10kW - Design Report",
        specs=specs
    )

    return results[0] if results else None


def compare_operating_points():
    """Show inductor behavior across multiple operating points."""
    print("\n" + "=" * 70)
    print("MULTI-OPERATING POINT ANALYSIS")
    print("=" * 70)

    # Define operating points for efficiency optimization
    operating_points = [
        {"name": "Low line, full load", "vin": 200, "vout": 800, "pout": 10000},
        {"name": "Mid line, full load", "vin": 325, "vout": 800, "pout": 10000},
        {"name": "High line, full load", "vin": 450, "vout": 800, "pout": 10000},
        {"name": "Low line, half load", "vin": 200, "vout": 800, "pout": 5000},
        {"name": "High line, light load", "vin": 450, "vout": 800, "pout": 2000},
    ]

    print("\nOperating Point Analysis:")
    print("-" * 70)

    for op in operating_points:
        # Calculate duty cycle and current for each point
        duty = 1 - op["vin"] / op["vout"]
        i_dc = op["pout"] / 0.98 / op["vin"]

        print(f"\n{op['name']}:")
        print(f"  Vin={op['vin']}V, Vout={op['vout']}V, Pout={op['pout']}W")
        print(f"  Duty cycle: {duty*100:.1f}%")
        print(f"  DC current: {i_dc:.1f} A")


def main():
    """Run the boost inductor design example."""
    best = design_boost_inductor()
    compare_operating_points()

    if best:
        print("\n" + "=" * 70)
        print("RECOMMENDED DESIGN")
        print("=" * 70)
        print(f"\nCore:      {best.core}")
        print(f"Material:  {best.material}")
        print(f"Turns:     {best.primary_turns}")
        print(f"Wire:      {best.primary_wire}")
        print(f"Air gap:   {best.air_gap_mm:.2f} mm")
        print(f"Losses:    {best.total_loss_w:.2f} W")

        # Bill of materials
        if best.bom:
            print("\nBill of Materials:")
            for item in best.bom:
                print(f"  - {item}")


if __name__ == "__main__":
    main()
