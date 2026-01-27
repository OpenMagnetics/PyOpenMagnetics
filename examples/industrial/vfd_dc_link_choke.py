"""
VFD DC Link Choke - Inductor Design

Application: Variable Frequency Drive (VFD) DC bus filter inductor
Real-world equivalents: Siemens SINAMICS filters, ABB drive filters

Specifications:
- DC bus: 540VDC nominal (from 400VAC rectified)
- Current: 20A DC with 5A ripple
- Inductance: 1mH
- Frequency: 8 kHz PWM harmonics
"""

from api.design import Design


def design_vfd_dc_link_choke():
    print("=" * 60)
    print("VFD DC LINK CHOKE - FILTER INDUCTOR")
    print("DC Bus: 540V | Current: 20A DC + 5A ripple")
    print("Inductance: 1mH @ 8kHz")
    print("=" * 60)

    design = (
        Design.inductor()
        .inductance(1e-3)          # 1mH
        .idc(20)                   # 20A DC
        .iac_pp(5)                 # 5A peak-to-peak ripple
        .fsw(8e3)                  # 8 kHz PWM harmonic
        .prefer("efficiency")      # Low losses for continuous operation
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Inductance:    {params['inductance_uH']:.0f} uH")
    print(f"  DC current:    {params['i_dc']:.1f} A")
    print(f"  Ripple (pp):   {params['i_ripple_pp']:.1f} A")
    print(f"  Peak current:  {params['i_peak']:.1f} A")

    print("\nFinding optimal designs...")
    results = design.solve(max_results=3)

    if not results:
        print("No suitable designs found.")
        return None

    print(f"\nFound {len(results)} designs:\n")
    for i, r in enumerate(results, 1):
        print(f"Design #{i}: {r.core} / {r.material}")
        print(f"  Turns:      {r.primary_turns}T, {r.primary_wire}")
        print(f"  Air gap:    {r.air_gap_mm:.2f} mm")
        print(f"  Core loss:  {r.core_loss_w:.3f} W")
        print(f"  Cu loss:    {r.copper_loss_w:.3f} W")
        print(f"  Total:      {r.total_loss_w:.3f} W")
        print()

    return results[0] if results else None


if __name__ == "__main__":
    best = design_vfd_dc_link_choke()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
