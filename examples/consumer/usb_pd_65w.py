"""
USB PD 65W Laptop Charger - Flyback Transformer Design

Application: USB-C laptop charger with GaN technology
Real-world equivalents: MacBook Air charger, Dell XPS charger, Anker 65W GaN

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 20V @ 3.25A (65W)
- Switching frequency: 130 kHz (GaN compatible)
- Target efficiency: >90%
"""

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
    results = design.solve(max_results=3)

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
    best = design_usb_pd_65w()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
