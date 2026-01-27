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

from api.design import Design


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
    best = design_usb_pd_140w()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
