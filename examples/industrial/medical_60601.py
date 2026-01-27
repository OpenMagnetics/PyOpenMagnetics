"""
Medical Grade Power Supply - Flyback Transformer Design (IEC 60601-1)

Application: Medical equipment isolated power supply
Real-world equivalents: Artesyn LPT series, XP Power CCM series

Specifications:
- Input: 85-264 VAC (universal input)
- Output: 12V @ 4.17A (50W)
- Switching frequency: 100 kHz
- Isolation: 2xMOPP (Means of Patient Protection)
- Leakage current: <100uA
- Target efficiency: >87%
"""

from api.design import Design


def design_medical_60601():
    print("=" * 60)
    print("MEDICAL 60601-1 PSU - FLYBACK TRANSFORMER")
    print("Input: 85-264 VAC | Output: 12V @ 4.17A (50W)")
    print("Isolation: 2xMOPP (4kV)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(85, 264)           # Universal AC input
        .output(12, 4.17)          # 12V @ 4.17A = 50W
        .fsw(100e3)                # 100 kHz
        .efficiency(0.87)          # Target 87% efficiency
        .isolation("reinforced", "IEC 60601-1")  # Medical isolation
        .prefer("efficiency")
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    print("\nNote: Medical requires 2xMOPP isolation (4kVrms)")
    print("      Triple-insulated wire or margin tape required")

    print("\nFinding optimal designs...")
    results = design.solve(max_results=MAX_RESULTS)

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

    return results[0] if results else None


if __name__ == "__main__":
    best = design_medical_60601()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
