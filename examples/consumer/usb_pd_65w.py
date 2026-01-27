"""
USB PD 65W Laptop Charger - Flyback Transformer Design

Application: USB-C laptop charger with GaN technology
Real-world equivalents: MacBook Air charger, Dell XPS charger, Anker 65W GaN

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 20V @ 3.25A (65W)
- Switching frequency: 130 kHz (GaN compatible)
- Target efficiency: >90%

Generated Reports:
- design_report.png: Main dashboard with Pareto front, radar chart, loss breakdown
- pareto_detailed.png: Detailed Pareto analysis
- parallel_coordinates.png: Multi-objective comparison
- heatmap.png: Design characteristics heatmap
- report_summary.json: JSON summary with statistics
"""

import os
from api.design import Design


def design_usb_pd_65w():
    print("=" * 60)
    print("USB PD 65W LAPTOP CHARGER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 20V @ 3.25A (65W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(85, 265)           # Universal AC input
        .output(20, 3.25)          # 20V @ 3.25A = 65W
        .fsw(130e3)                # 130 kHz for GaN
        .efficiency(0.90)          # Target 90% efficiency
        .max_height(18)            # Compact GaN form factor
        .max_width(25)
        .prefer("efficiency")      # Efficiency is key for laptops
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    print("\nFinding optimal designs...")
    output_dir = "examples/_output/usb_pd_65w"
    results = design.solve(max_results=5, verbose=True, output_dir=output_dir)

    if not results:
        print("No suitable designs found.")
        return None

    print(f"\nFound {len(results)} designs:\n")
    for i, r in enumerate(results, 1):
        print(f"Design #{i}: {r.core} / {r.material}")
        print(f"  Primary:    {r.primary_turns}T, {r.primary_wire}")
        print(f"  Air gap:    {r.air_gap_mm:.2f} mm")
        print(f"  Total loss: {r.total_loss_w:.3f} W")
        print()

    # Generate comprehensive visual report with matplotlib
    try:
        from api.report import generate_design_report

        specs = {
            "power_w": 65,
            "frequency_hz": 130e3,
            "efficiency": 0.90,
            "topology": "flyback",
        }

        print("Generating visual reports...")
        report_path = generate_design_report(
            results,
            output_dir,
            title="USB PD 65W Charger - Design Report",
            specs=specs,
            verbose=True
        )

        print(f"\nReports saved to: {output_dir}/")
        print("  - design_report.png (main dashboard)")
        print("  - pareto_detailed.png (Pareto analysis)")
        print("  - parallel_coordinates.png (multi-objective)")
        print("  - heatmap.png (characteristics)")
        print("  - report_summary.json (statistics)")

    except ImportError as e:
        print(f"\n[Visual reports skipped - matplotlib not installed: {e}]")

    return results[0] if results else None


if __name__ == "__main__":
    best = design_usb_pd_65w()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
