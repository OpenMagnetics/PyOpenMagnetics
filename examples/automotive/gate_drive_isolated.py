"""
Isolated Gate Drive Transformer - Flyback Design

Application: Isolated gate driver for SiC/GaN power modules in EV inverters
Real-world equivalents: Infineon EiceDRIVER, Texas Instruments UCC21750

Specifications:
- Input: 12V DC (from auxiliary supply)
- Output: +15V (positive gate drive) and 8V (for -8V negative bias)
- Switching frequency: 500 kHz
- Isolation: Reinforced, 5kV

Note: The -8V output is achieved by reversing the winding polarity during assembly.
      Both outputs are specified as positive values; the transformer design is the same.
"""

from api.design import Design


def design_gate_drive_isolated():
    print("=" * 60)
    print("ISOLATED GATE DRIVE TRANSFORMER")
    print("Input: 12V DC | Output: +15V / -8V isolated")
    print("=" * 60)
    print("\nNote: Two independent secondary windings:")
    print("  - Secondary 1: 15V @ 0.5A (positive gate drive)")
    print("  - Secondary 2: 8V @ 0.2A (negative bias, reverse polarity)")

    # For gate drivers, design with two independent secondary windings
    # The -8V output is achieved by reversing winding polarity during winding
    design = (
        Design.flyback()
        .vin_dc(10, 14)            # 12V +/- tolerance
        .output(15, 0.5)           # Secondary 1: +15V gate drive
        .output(8, 0.2)            # Secondary 2: 8V (connect reversed for -8V)
        .fsw(500e3)                # 500 kHz (good balance of size/losses)
        .efficiency(0.80)          # Lower efficiency acceptable at low power
        .max_height(12)            # Compact
        .max_width(15)
        .prefer("size")
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")

    print("\nFinding optimal designs...")
    # auto_relax=True will try relaxing constraints if no solution found
    results = design.solve(max_results=MAX_RESULTS, verbose=True, auto_relax=True,
                          output_dir="examples/_output/gate_drive_isolated")

    if not results:
        print("No suitable designs found even after relaxation.")
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
        print("\nWinding Instructions:")
        print("  1. Wind primary as specified")
        print("  2. Secondary 1 (+15V): Wind in same direction as primary")
        print("  3. Secondary 2 (-8V): Wind in OPPOSITE direction for negative output")
        print("  4. Use margin tape for isolation between primary and secondaries")
