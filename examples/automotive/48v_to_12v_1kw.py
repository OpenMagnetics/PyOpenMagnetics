"""
48V to 12V 1kW DC-DC Converter - Buck Inductor Design

Application: Automotive mild-hybrid 48V to 12V auxiliary power converter
Real-world equivalents: Mercedes 48V EQ Boost, Audi e-tron DC-DC

Specifications:
- Input: 36-52V (48V nominal with battery variation)
- Output: 12V @ 83A (1kW)
- Switching frequency: 100 kHz
- Bidirectional capable
"""

from api.design import Design


def design_48v_to_12v_1kw():
    print("=" * 60)
    print("AUTOMOTIVE 48V TO 12V DC-DC - BUCK INDUCTOR")
    print("Input: 36-52V | Output: 12V @ 83A (1kW)")
    print("=" * 60)

    design = (
        Design.buck()
        .vin(36, 52)               # 48V system with variation
        .vout(12)                  # 12V auxiliary bus
        .iout(83)                  # 83A for 1kW
        .fsw(100e3)                # 100 kHz
        .ripple_ratio(0.3)         # 30% ripple ratio
        .prefer("efficiency")      # Automotive efficiency critical
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Inductance:    {params['inductance_uH']:.1f} uH")
    print(f"  Peak current:  {params['i_peak']:.1f} A")
    print(f"  Ripple (pp):   {params['i_ripple_pp']:.1f} A")
    print(f"  Duty cycle:    {params['duty_cycle']:.2%}")

    print("\nFinding optimal designs...")
    results = design.solve(max_results=MAX_RESULTS)

    if not results:
        print("No suitable designs found.")
        return None

    print(f"\nFound {len(results)} designs:\n")
    for i, r in enumerate(results, 1):
        print(f"Design #{i}: {r.core} / {r.material}")
        print(f"  Turns:      {r.primary_turns}T, {r.primary_wire}")
        print(f"  Air gap:    {r.air_gap_mm:.2f} mm")
        print(f"  Total loss: {r.total_loss_w:.3f} W")
        print()

    return results[0] if results else None


if __name__ == "__main__":
    best = design_48v_to_12v_1kw()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
