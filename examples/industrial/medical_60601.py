"""
Medical Grade Power Supply - Flyback Transformer Design (IEC 60601-1)

Application: Medical equipment isolated power supply
Real-world equivalents: Artesyn LPT series, XP Power CCM series

Specifications:
- Input: 85-264 VAC (universal input)
- Output: 12V @ 4.17A (50W)
- Switching frequency: 100 kHz
- Isolation: 2xMOPP (Means of Patient Protection)
- Leakage current: <100uA
- Target efficiency: >87%
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from api.models import (
    VoltageSpec, CurrentSpec, FlybackTopology, PowerSupplySpec, PortSpec
)
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)

# Define specifications using datamodels
psu_spec = PowerSupplySpec(
    name="Medical 60601-1 PSU",
    inputs=[PortSpec(
        name="AC Input",
        voltage=VoltageSpec.ac(230, v_min_rms=85, v_max_rms=264),
        current=CurrentSpec.dc(0.4)
    )],
    outputs=[PortSpec(
        name="Isolated Output",
        voltage=VoltageSpec.dc(12, tolerance_pct=5),
        current=CurrentSpec.dc(4.17)
    )],
    efficiency=0.87,
    isolation_v=4000  # 2xMOPP
)

topology = FlybackTopology(fsw_hz=100e3, max_duty=0.45)


def design_medical_60601():
    print("=" * 60)
    print("MEDICAL 60601-1 PSU - FLYBACK TRANSFORMER")
    print("Input: 85-264 VAC | Output: 12V @ 4.17A (50W)")
    print("Isolation: 2xMOPP (4kV)")
    print("=" * 60)

    design = (
        Design.flyback()
        .vin_ac(psu_spec.inputs[0].voltage.min, psu_spec.inputs[0].voltage.max)
        .output(psu_spec.outputs[0].voltage.nominal, psu_spec.outputs[0].current.nominal)
        .fsw(topology.fsw_hz)
        .efficiency(psu_spec.efficiency)
        .isolation("reinforced", "IEC 60601-1")  # Medical isolation
        .prefer("efficiency")
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Turns ratio (n):     {params['turns_ratio']:.2f}")
    print(f"  Mag inductance (Lm): {params['magnetizing_inductance_uH']:.1f} uH")
    print(f"  Duty cycle (D):      {params['duty_cycle_low_line']:.2%}")

    print("\nNote: Medical requires 2xMOPP isolation (4kVrms)")
    print("      Triple-insulated wire or margin tape required")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "power_w": psu_spec.total_output_power,
        "frequency_hz": topology.fsw_hz,
        "efficiency": psu_spec.efficiency,
        "topology": topology.name,
        "isolation": "2xMOPP",
    }
    generate_example_report(
        results,
        "medical_60601",
        "Medical 60601-1 PSU - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_medical_60601()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
