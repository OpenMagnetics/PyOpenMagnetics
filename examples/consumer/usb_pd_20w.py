"""
USB PD 20W Charger - Flyback Transformer Design

Application: Compact USB Power Delivery charger supporting 5V/9V/12V profiles
Real-world equivalents: Apple 20W USB-C charger, Samsung 25W charger

Specifications:
- Input: 85-265 VAC (universal input)
- Output: 12V @ 1.67A (20W, PD profile)
- Switching frequency: 100 kHz
- Target efficiency: >87%
"""

from api.design import Design


def design_usb_pd_20w():
    print("=" * 60)
    print("USB PD 20W CHARGER - FLYBACK TRANSFORMER")
    print("Input: 85-265 VAC | Output: 12V @ 1.67A (20W)")
    print("=" * 60)

    # Design using fluent API
    design = (
        Design.flyback()
        .vin_ac(85, 265)           # Universal AC input
        .output(12, 1.67)          # 12V @ 1.67A = 20W
        .fsw(100e3)                # 100 kHz switching
        .efficiency(0.87)          # Target 87% efficiency
        .max_height(15)            # Compact form factor (mm)
        .max_width(20)
        .prefer("size")            # Optimize for small size
    )

    # Show calculated parameters
    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    # Get design recommendations
    print("\nFinding optimal designs...")
    results = design.solve(max_results=3)

    if not results:
        print("No suitable designs found. Try relaxing constraints.")
        return None

    print(f"\nFound {len(results)} designs:\n")
    for i, r in enumerate(results, 1):
        print(f"Design #{i}: {r.core} / {r.material}")
        print(f"  Primary:    {r.primary_turns}T, {r.primary_wire}")
        print(f"  Air gap:    {r.air_gap_mm:.2f} mm")
        print(f"  Core loss:  {r.core_loss_w:.3f} W")
        print(f"  Cu loss:    {r.copper_loss_w:.3f} W")
        print(f"  Total:      {r.total_loss_w:.3f} W")
        print()

    return results[0] if results else None


if __name__ == "__main__":
    best = design_usb_pd_20w()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
