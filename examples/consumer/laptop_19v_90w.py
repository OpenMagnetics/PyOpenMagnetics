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

from api.design import Design


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
    best = design_laptop_19v_90w()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
