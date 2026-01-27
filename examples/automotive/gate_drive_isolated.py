"""
Isolated Gate Drive Transformer - Flyback Design

Application: Isolated gate driver for SiC/GaN power modules in EV inverters
Real-world equivalents: Infineon EiceDRIVER, Texas Instruments UCC21750

Specifications:
- Input: 12V DC (from auxiliary supply)
- Output: +15V/-8V isolated (dual output)
- Switching frequency: 1 MHz (high speed gate drive)
- Isolation: Reinforced, 5kV
"""

from api.design import Design


def design_gate_drive_isolated():
    print("=" * 60)
    print("ISOLATED GATE DRIVE TRANSFORMER")
    print("Input: 12V DC | Output: +15V/-8V isolated")
    print("=" * 60)

    # For gate drivers, typically a flyback with low power
    design = (
        Design.flyback()
        .vin_dc(10, 14)            # 12V +/- tolerance
        .output(15, 0.5)           # +15V gate drive (main)
        .output(-8, 0.2)           # -8V negative bias
        .fsw(1e6)                  # 1 MHz for fast response
        .efficiency(0.80)          # Lower efficiency acceptable at low power
        .max_height(8)             # Very compact
        .max_width(10)
        .prefer("size")
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")

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
    best = design_gate_drive_isolated()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
