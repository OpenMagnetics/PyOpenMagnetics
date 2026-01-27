"""
Telecom Rectifier 48V 3kW - LLC Resonant Converter Design

Application: Telecom base station power supply module
Real-world equivalents: Eltek Flatpack2, Delta DPR series

Specifications:
- Input: 380-420VDC (from PFC stage)
- Output: 48V @ 62.5A (3kW)
- Resonant frequency: 100 kHz
- Target efficiency: >96% (LLC resonant)
"""

from api.design import Design

MAX_RESULTS = 50

def design_rectifier_48v_3kw():
    print("=" * 60)
    print("TELECOM RECTIFIER 48V 3KW - LLC TRANSFORMER")
    print("Input: 380-420VDC | Output: 48V @ 62.5A (3kW)")
    print("=" * 60)

    design = (
        Design.llc()
        .vin_dc(380, 420)          # DC bus from PFC
        .output(48, 62.5)          # 48V @ 62.5A = 3kW
        .resonant_frequency(100e3) # 100 kHz resonant
        .quality_factor(0.3)       # Q factor
        .prefer("efficiency")
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")

    print("\nFinding optimal designs...")
    results = design.solve(max_results=MAX_RESULTS, 
                           verbose=True, auto_relax=True,
                           output_dir="examples/_output/rectifier_48v_3kw")

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
    best = design_rectifier_48v_3kw()
    if best:
        print(f"Recommended: {best.core} with {best.material}")
