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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.design import Design
from api.models import (
    VoltageSpec, CurrentSpec, BuckTopology, PowerSupplySpec, PortSpec
)
from examples.common import (
    DEFAULT_MAX_RESULTS, generate_example_report, print_results_summary
)

# Define specifications using datamodels
psu_spec = PowerSupplySpec(
    name="VFD DC Link Choke",
    inputs=[PortSpec(
        name="DC Bus",
        voltage=VoltageSpec.dc(540, tolerance_pct=10),
        current=CurrentSpec.dc(20, ripple_pp=5)
    )],
    outputs=[PortSpec(
        name="Filtered DC",
        voltage=VoltageSpec.dc(540, tolerance_pct=5),
        current=CurrentSpec.dc(20)
    )],
    efficiency=0.99,
    isolation_v=None  # Non-isolated
)

topology = BuckTopology(fsw_hz=8e3)


def design_vfd_dc_link_choke():
    print("=" * 60)
    print("VFD DC LINK CHOKE - FILTER INDUCTOR")
    print("DC Bus: 540V | Current: 20A DC + 5A ripple")
    print("Inductance: 1mH @ 8kHz")
    print("=" * 60)

    design = (
        Design.inductor()
        .inductance(1e-3)          # 1mH
        .idc(psu_spec.inputs[0].current.nominal)
        .iac_pp(psu_spec.inputs[0].current.peak_to_peak)
        .fsw(topology.fsw_hz)
        .prefer("efficiency")      # Low losses for continuous operation
    )

    params = design.get_calculated_parameters()
    print("\nCalculated Parameters:")
    print(f"  Inductance:    {params['inductance_uH']:.0f} uH")
    print(f"  DC current:    {params['i_dc']:.1f} A")
    print(f"  Ripple (pp):   {params['i_ripple_pp']:.1f} A")
    print(f"  Peak current:  {params['i_peak']:.1f} A")

    print(f"\nFinding optimal designs (max {DEFAULT_MAX_RESULTS})...")
    results = design.solve(max_results=DEFAULT_MAX_RESULTS, verbose=True)

    if not results:
        print("No suitable designs found.")
        return None

    print_results_summary(results)

    specs = {
        "inductance_mH": 1.0,
        "current_dc_A": psu_spec.inputs[0].current.nominal,
        "frequency_hz": topology.fsw_hz,
        "topology": "inductor",
    }
    generate_example_report(
        results,
        "vfd_dc_link_choke",
        "VFD DC Link Choke - Design Report",
        specs=specs
    )

    return results[0] if results else None


if __name__ == "__main__":
    best = design_vfd_dc_link_choke()
    if best:
        print(f"\nRecommended: {best.core} with {best.material}")
