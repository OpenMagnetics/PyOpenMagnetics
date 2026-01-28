"""
PyOpenMagnetics Examples - Flyback Transformer Design

This example demonstrates a complete flyback transformer design workflow:
1. Define converter specifications using the fluent API
2. Get design recommendations (50 Pareto-optimal solutions)
3. Analyze losses and performance
4. Generate visual reports

For more examples, see llms.txt in the PyOpenMagnetics directory.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.design import Design
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)


def design_flyback_transformer():
    """
    Design a flyback transformer for a 24V/3A output from universal AC input.

    Specifications:
    - Input: 85-265 VAC (rectified to ~120-375 VDC)
    - Output: 24V @ 3A (72W)
    - Switching frequency: 100 kHz
    - Efficiency target: 85%
    """
    print("=" * 60)
    print("FLYBACK TRANSFORMER DESIGN")
    print("Input: 85-265 VAC | Output: 24V @ 3A (72W)")
    print("=" * 60)

    # Step 1: Define the converter using fluent API
    design = (
        Design.flyback()
        .vin_ac(85, 265)           # Universal AC input
        .output(24, 3)             # 24V @ 3A = 72W
        .fsw(100e3)                # 100 kHz switching
        .efficiency(0.85)          # Target 85% efficiency
        .prefer("efficiency")      # Optimize for efficiency
    )

    # Step 2: Get calculated parameters
    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    # Step 3: Get design recommendations (50 Pareto-optimal solutions)
    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found.")
        return None

    # Step 4: Display results summary
    print_results_summary(results)

    # Step 5: Generate visual reports (Pareto front, etc.)
    specs = {
        "power_w": 72,
        "frequency_hz": 100e3,
        "efficiency": 0.85,
        "topology": "flyback",
    }
    generate_example_report(
        results,
        "flyback_design",
        "Flyback Transformer 72W - Design Report",
        specs=specs
    )

    return results


def explore_core_database():
    """Demonstrate database access functions."""
    import PyOpenMagnetics

    print("\n" + "=" * 60)
    print("CORE DATABASE EXPLORATION")
    print("=" * 60)

    # Get available shape families
    families = PyOpenMagnetics.get_core_shape_families()
    print(f"\nShape families: {', '.join(families[:10])}...")

    # Get materials by manufacturer
    ferroxcube = PyOpenMagnetics.get_core_material_names_by_manufacturer("Ferroxcube")
    print(f"Ferroxcube materials: {', '.join(ferroxcube[:5])}...")

    tdk = PyOpenMagnetics.get_core_material_names_by_manufacturer("TDK")
    print(f"TDK materials: {', '.join(tdk[:5])}...")

    # Get material properties
    print("\n3C95 Properties at 25C:")
    mu = PyOpenMagnetics.get_material_permeability("3C95", 25, 0, 100000)
    print(f"  Permeability (100 kHz): {mu:.0f}")

    rho = PyOpenMagnetics.get_material_resistivity("3C95", 25)
    print(f"  Resistivity: {rho:.2f} Ohm*m")

    material = PyOpenMagnetics.find_core_material_by_name("3C95")
    steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients(material, 100000)
    print(f"  Steinmetz k={steinmetz['k']:.2e}, a={steinmetz['alpha']:.2f}, b={steinmetz['beta']:.2f}")


def wire_selection_example():
    """Demonstrate wire selection and loss calculation."""
    import PyOpenMagnetics

    print("\n" + "=" * 60)
    print("WIRE SELECTION")
    print("=" * 60)

    # Find available wire types
    wire_types = PyOpenMagnetics.get_available_wire_types()
    print(f"\nAvailable wire types: {wire_types}")

    # Find wire by dimension
    round_wire = PyOpenMagnetics.find_wire_by_dimension(0.0005, "round", "IEC 60317")
    print(f"\n0.5mm round wire: {round_wire.get('name', 'N/A')}")

    # Calculate DC resistance
    R_dc = PyOpenMagnetics.calculate_dc_resistance_per_meter(round_wire, 25)
    print(f"  DC resistance: {R_dc*1000:.2f} mOhm/m at 25C")

    R_dc_hot = PyOpenMagnetics.calculate_dc_resistance_per_meter(round_wire, 100)
    print(f"  DC resistance: {R_dc_hot*1000:.2f} mOhm/m at 100C")

    # Litz wire for high frequency
    print("\nFor high-frequency applications, consider litz wire:")
    litz_wires = [w for w in PyOpenMagnetics.get_wire_names() if "litz" in w.lower()]
    print(f"  Available litz options: {len(litz_wires)} types")


if __name__ == "__main__":
    # Run the flyback design example
    results = design_flyback_transformer()

    if results:
        best = results[0]
        print(f"\nRecommended: {best.core} with {best.material}")

    # Explore the database
    explore_core_database()

    # Wire selection
    wire_selection_example()

    print("\n[OK] All examples completed successfully!")
