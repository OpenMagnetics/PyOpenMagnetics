"""
PoE Injector - Flyback Transformer Design

Application: Power over Ethernet injector for access points/cameras
Real-world equivalents: Ubiquiti PoE adapters, Cisco PoE injectors

Specifications:
- Input: 36-57VDC (PoE input range)
- Output: 12V @ 2.5A (30W) isolated
- Switching frequency: 200 kHz
- Isolation: Functional (IEEE 802.3af/at)
"""

from api.design import Design


def design_poe_injector():
    print("=" * 60)
    print("POE INJECTOR - FLYBACK TRANSFORMER")
    print("Input: 36-57VDC | Output: 12V @ 2.5A (30W)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_dc(36, 57)            # PoE input range
        .output(12, 2.5)           # 12V @ 2.5A = 30W
        .fsw(200e3)                # 200 kHz
        .efficiency(0.88)          # Target 88% efficiency
        .max_height(12)            # Compact PoE module
        .max_width(15)
        .prefer("size")
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
    best = design_poe_injector()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
