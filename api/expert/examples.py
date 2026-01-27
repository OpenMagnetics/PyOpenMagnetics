"""
Example Generator for PyOpenMagnetics.

Generates hundreds of real-world design examples to help hardware engineers
understand magnetic design through practical applications.
"""

from dataclasses import dataclass, field
from typing import Optional
from .knowledge import APPLICATIONS, TOPOLOGIES, suggest_topology


@dataclass
class DesignExample:
    """A complete design example with context."""
    name: str
    category: str
    application: str
    description: str

    # Electrical specs
    topology: str
    vin_min: float
    vin_max: float
    vin_is_ac: bool
    outputs: list[dict]  # [{voltage, current}, ...]
    frequency_hz: float

    # Constraints
    max_height_mm: Optional[float] = None
    max_width_mm: Optional[float] = None
    efficiency_target: Optional[float] = None
    ambient_temp_c: float = 25.0

    # Context
    real_world_products: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    design_notes: list[str] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)

    def to_design_params(self) -> dict:
        """Convert to parameters for Design API."""
        return {
            "topology": self.topology,
            "vin_min": self.vin_min,
            "vin_max": self.vin_max,
            "vin_is_ac": self.vin_is_ac,
            "outputs": self.outputs,
            "frequency_hz": self.frequency_hz,
            "max_height_mm": self.max_height_mm,
            "max_width_mm": self.max_width_mm,
            "efficiency_target": self.efficiency_target,
        }


class ExampleGenerator:
    """Generate design examples for various applications."""

    def __init__(self):
        self.examples: list[DesignExample] = []

    def generate_all(self) -> list[DesignExample]:
        """Generate all examples across all categories."""
        self.examples = []

        # Consumer
        self.examples.extend(self._generate_usb_chargers())
        self.examples.extend(self._generate_laptop_adapters())
        self.examples.extend(self._generate_led_drivers())

        # Automotive
        self.examples.extend(self._generate_automotive_dcdc())
        self.examples.extend(self._generate_gate_drivers())

        # Industrial
        self.examples.extend(self._generate_din_rail())
        self.examples.extend(self._generate_medical())

        # Telecom
        self.examples.extend(self._generate_poe())
        self.examples.extend(self._generate_server_psu())

        # Inductors
        self.examples.extend(self._generate_pfc_inductors())
        self.examples.extend(self._generate_filter_inductors())

        return self.examples

    def _generate_usb_chargers(self) -> list[DesignExample]:
        """Generate USB charger examples."""
        examples = []

        # USB PD power levels
        pd_levels = [
            (20, 12, 1.67, "phone", ["Apple 20W", "Samsung 25W"]),
            (30, 20, 1.5, "tablet", ["iPad charger", "Pixel 30W"]),
            (45, 20, 2.25, "ultrabook", ["MacBook Air", "Surface"]),
            (65, 20, 3.25, "laptop", ["MacBook Pro 13", "Dell XPS"]),
            (100, 20, 5.0, "workstation", ["MacBook Pro 14"]),
            (140, 28, 5.0, "pro_laptop", ["MacBook Pro 16"]),
        ]

        for power, vout, iout, use, products in pd_levels:
            # Universal input version
            examples.append(DesignExample(
                name=f"USB PD {power}W Universal Charger",
                category="consumer",
                application="usb_charger",
                description=f"{power}W USB-C charger for {use}, universal AC input",
                topology="flyback",
                vin_min=85, vin_max=265, vin_is_ac=True,
                outputs=[{"voltage": vout, "current": iout}],
                frequency_hz=100000 if power < 65 else 130000,
                max_height_mm=18 if power < 65 else 22,
                efficiency_target=0.87 if power < 45 else 0.90,
                real_world_products=products,
                standards=["IEC 62368-1", "DoE Level VI"],
                design_notes=[
                    f"{'GaN' if power >= 65 else 'Si'} MOSFETs recommended",
                    "EFD or EE core for compact size",
                    "Primary-side regulation for cost savings",
                ],
            ))

            # Compact GaN version for higher power
            if power >= 45:
                examples.append(DesignExample(
                    name=f"USB PD {power}W GaN Compact Charger",
                    category="consumer",
                    application="usb_charger",
                    description=f"Compact {power}W GaN charger, 30% smaller",
                    topology="active_clamp_flyback" if power < 100 else "flyback",
                    vin_min=85, vin_max=265, vin_is_ac=True,
                    outputs=[{"voltage": vout, "current": iout}],
                    frequency_hz=200000 if power < 100 else 150000,
                    max_height_mm=14 if power < 100 else 18,
                    efficiency_target=0.92,
                    real_world_products=["Anker Nano", "Baseus GaN"],
                    design_notes=[
                        "GaN enables 2x frequency for smaller magnetics",
                        "Active clamp recovers leakage energy",
                        "Planar or ELP core for slim profile",
                    ],
                ))

        # Multi-output chargers
        examples.append(DesignExample(
            name="USB PD 65W Dual Output Charger",
            category="consumer",
            application="usb_charger",
            description="65W total with 45W + 20W USB-C outputs",
            topology="flyback",
            vin_min=85, vin_max=265, vin_is_ac=True,
            outputs=[{"voltage": 20, "current": 2.25}, {"voltage": 12, "current": 1.67}],
            frequency_hz=100000,
            efficiency_target=0.88,
            design_notes=[
                "Cross-regulation critical for multi-output",
                "Mag amp or synchronous rectifier for regulation",
            ],
        ))

        return examples

    def _generate_laptop_adapters(self) -> list[DesignExample]:
        """Generate laptop adapter examples."""
        examples = []

        adapters = [
            (65, 19.5, 3.33, "standard laptop", ["Dell", "HP", "Lenovo"]),
            (90, 19.5, 4.62, "workstation laptop", ["ThinkPad", "Precision"]),
            (135, 20, 6.75, "gaming laptop", ["Razer", "Alienware"]),
            (180, 19.5, 9.23, "high-end gaming", ["MSI", "ASUS ROG"]),
            (230, 19.5, 11.8, "desktop replacement", ["Alienware Area-51m"]),
        ]

        for power, vout, iout, use_case, brands in adapters:
            topology = "flyback" if power < 150 else "LLC"

            examples.append(DesignExample(
                name=f"Laptop Adapter {power}W",
                category="consumer",
                application="laptop_adapter",
                description=f"{power}W adapter for {use_case}",
                topology=topology,
                vin_min=85, vin_max=265, vin_is_ac=True,
                outputs=[{"voltage": vout, "current": iout}],
                frequency_hz=100000 if topology == "flyback" else 100000,
                efficiency_target=0.88 if power < 150 else 0.92,
                real_world_products=brands,
                standards=["IEC 62368-1", "ENERGY STAR"],
                design_notes=[
                    f"{'LLC resonant' if topology == 'LLC' else 'Flyback'} for this power level",
                    "Active PFC required for power factor",
                    "Slim form factor requires careful thermal design",
                ],
            ))

        return examples

    def _generate_led_drivers(self) -> list[DesignExample]:
        """Generate LED driver examples."""
        examples = []

        # LED driver variants
        led_types = [
            (12, 1.0, "12V LED strip", 24, "constant_voltage"),
            (24, 2.5, "24V LED strip", 48, "constant_voltage"),
            (36, 1.0, "LED panel", 48, "constant_current"),
            (48, 1.5, "LED tube retrofit", 60, "constant_current"),
            (100, 2.1, "High bay light", 150, "constant_current"),
            (200, 1.4, "Street light", 320, "constant_current"),
        ]

        for vout, iout, application, vled, output_type in led_types:
            power = vout * iout

            examples.append(DesignExample(
                name=f"LED Driver {power:.0f}W {application}",
                category="consumer",
                application="led_driver",
                description=f"{power:.0f}W {output_type} LED driver for {application}",
                topology="flyback",
                vin_min=85, vin_max=265, vin_is_ac=True,
                outputs=[{"voltage": vout, "current": iout}],
                frequency_hz=65000,
                efficiency_target=0.87,
                design_notes=[
                    f"{'Constant current' if output_type == 'constant_current' else 'Constant voltage'} output",
                    "Consider electrolytic-free for long life",
                    "Valley fill for high power factor" if power < 25 else "Active PFC required",
                ],
                standards=["IEC 61347", "ENERGY STAR"],
            ))

        return examples

    def _generate_automotive_dcdc(self) -> list[DesignExample]:
        """Generate automotive DC-DC examples."""
        examples = []

        # 48V to 12V converters
        for power in [200, 500, 1000, 2000, 3000]:
            examples.append(DesignExample(
                name=f"48V to 12V {power}W Automotive DC-DC",
                category="automotive",
                application="automotive_dcdc",
                description=f"{power}W DC-DC for 48V mild hybrid to 12V auxiliary",
                topology="phase_shifted_full_bridge" if power > 1000 else "buck",
                vin_min=36, vin_max=52, vin_is_ac=False,
                outputs=[{"voltage": 12, "current": power / 12}],
                frequency_hz=100000,
                ambient_temp_c=85,
                efficiency_target=0.95,
                standards=["AEC-Q200", "ISO 16750", "CISPR 25"],
                design_notes=[
                    f"{'Interleaved phases' if power > 1000 else 'Single phase'} recommended",
                    "Powder core for high DC bias handling",
                    "-40°C to +105°C operation required",
                ],
            ))

        # HV to 12V (EV main DC-DC)
        for power in [2000, 2500, 3000, 3500]:
            examples.append(DesignExample(
                name=f"HV to 12V {power}W EV DC-DC (LDC)",
                category="automotive",
                application="automotive_dcdc",
                description=f"{power}W isolated DC-DC from HV battery to 12V",
                topology="phase_shifted_full_bridge",
                vin_min=250, vin_max=450, vin_is_ac=False,
                outputs=[{"voltage": 12, "current": power / 12}],
                frequency_hz=100000,
                efficiency_target=0.96,
                standards=["AEC-Q200", "ISO 16750"],
                design_notes=[
                    "Reinforced isolation required (HV class)",
                    "Planar transformer for power density",
                    "Liquid cooling typical at this power",
                ],
            ))

        return examples

    def _generate_gate_drivers(self) -> list[DesignExample]:
        """Generate isolated gate driver transformer examples."""
        examples = []

        # Gate driver variants
        variants = [
            ("Si IGBT", 15, -8, 3000, 100000),
            ("SiC MOSFET", 20, -5, 5000, 200000),
            ("GaN HEMT", 6, 0, 1500, 500000),
        ]

        for device, vg_pos, vg_neg, isolation, freq in variants:
            examples.append(DesignExample(
                name=f"Isolated Gate Driver for {device}",
                category="automotive",
                application="gate_driver",
                description=f"Gate drive transformer for {device}, +{vg_pos}V/{vg_neg}V",
                topology="flyback",
                vin_min=10, vin_max=14, vin_is_ac=False,
                outputs=[{"voltage": vg_pos, "current": 0.5}],
                frequency_hz=freq,
                max_height_mm=8,
                design_notes=[
                    f"{isolation}V isolation required",
                    "Low interwinding capacitance critical",
                    "EP or EFD core for compact size",
                    f"CMTI > 100 V/ns for {device}",
                ],
            ))

        return examples

    def _generate_din_rail(self) -> list[DesignExample]:
        """Generate DIN rail power supply examples."""
        examples = []

        variants = [
            (24, 2.5, 60, "1.5 SU"),
            (24, 5, 120, "3 SU"),
            (24, 10, 240, "6 SU"),
            (24, 20, 480, "9 SU"),
            (48, 5, 240, "6 SU"),
            (12, 5, 60, "3 SU"),
        ]

        for vout, iout, power, width in variants:
            topology = "flyback" if power <= 150 else "LLC"

            examples.append(DesignExample(
                name=f"DIN Rail {vout}V {power}W PSU",
                category="industrial",
                application="din_rail_psu",
                description=f"{power}W DIN rail power supply, {width} width",
                topology=topology,
                vin_min=85, vin_max=264, vin_is_ac=True,
                outputs=[{"voltage": vout, "current": iout}],
                frequency_hz=100000,
                efficiency_target=0.89,
                standards=["IEC 62368-1", "UL 508"],
                design_notes=[
                    f"{'Single-stage flyback' if topology == 'flyback' else 'PFC + LLC'} architecture",
                    "DIN rail width limits core height",
                    "Consider redundancy capability",
                ],
            ))

        return examples

    def _generate_medical(self) -> list[DesignExample]:
        """Generate medical power supply examples."""
        examples = []

        variants = [
            (12, 4.17, 50, "BF", "patient monitor"),
            (24, 2.5, 60, "BF", "infusion pump"),
            (48, 1.5, 72, "2xMOPP", "diagnostic equipment"),
            (12, 8.33, 100, "CF", "cardiac equipment"),
        ]

        for vout, iout, power, classification, application in variants:
            examples.append(DesignExample(
                name=f"Medical {power}W {classification} PSU",
                category="industrial",
                application="medical_psu",
                description=f"{power}W medical PSU for {application}, {classification} rated",
                topology="flyback",
                vin_min=85, vin_max=264, vin_is_ac=True,
                outputs=[{"voltage": vout, "current": iout}],
                frequency_hz=100000,
                efficiency_target=0.87,
                standards=["IEC 60601-1", "IEC 60601-1-2"],
                design_notes=[
                    f"{classification} classification requirements",
                    "8mm creepage/clearance for 2xMOPP",
                    "Patient leakage <100µA (BF) or <10µA (CF)",
                    "Triple-insulated wire mandatory",
                ],
            ))

        return examples

    def _generate_poe(self) -> list[DesignExample]:
        """Generate PoE examples."""
        examples = []

        standards = [
            ("802.3af", 15.4, 12, 1.0, "IP camera"),
            ("802.3at", 30, 12, 2.0, "Access point"),
            ("802.3bt Type 3", 60, 12, 4.0, "PTZ camera"),
            ("802.3bt Type 4", 90, 48, 1.5, "Digital signage"),
        ]

        for std, poe_power, vout, iout, application in standards:
            examples.append(DesignExample(
                name=f"PoE PD {std} for {application}",
                category="telecom",
                application="poe",
                description=f"PoE Powered Device converter ({std}) for {application}",
                topology="flyback",
                vin_min=36, vin_max=57, vin_is_ac=False,
                outputs=[{"voltage": vout, "current": iout}],
                frequency_hz=200000,
                max_height_mm=10,
                efficiency_target=0.88,
                standards=["IEEE " + std],
                design_notes=[
                    f"Input from PoE {std} ({poe_power}W max)",
                    "Compact design critical for integration",
                    "Consider 4-pair for high power",
                ],
            ))

        return examples

    def _generate_server_psu(self) -> list[DesignExample]:
        """Generate server PSU examples."""
        examples = []

        levels = [
            (800, "Gold", 0.87, "ATX"),
            (1200, "Platinum", 0.90, "CRPS"),
            (2000, "Titanium", 0.94, "CRPS"),
            (3000, "Titanium", 0.94, "OCP"),
        ]

        for power, tier, eff, form in levels:
            examples.append(DesignExample(
                name=f"Server PSU {power}W {tier}",
                category="telecom",
                application="server_psu",
                description=f"{power}W server power supply, 80 PLUS {tier}, {form} form factor",
                topology="LLC",
                vin_min=85, vin_max=264, vin_is_ac=True,
                outputs=[{"voltage": 12, "current": power / 12}],
                frequency_hz=100000,
                efficiency_target=eff,
                standards=["80 PLUS", "CRPS" if "CRPS" in form else "ATX"],
                design_notes=[
                    "Interleaved bridgeless totem-pole PFC",
                    "LLC with synchronous rectification",
                    f"{'GaN for Titanium' if tier == 'Titanium' else 'SiC or Si'} MOSFETs",
                    "Digital control for efficiency optimization",
                ],
            ))

        return examples

    def _generate_pfc_inductors(self) -> list[DesignExample]:
        """Generate PFC inductor examples."""
        examples = []

        levels = [
            (100, 250e-6, 1.0, "CCM"),
            (300, 400e-6, 2.0, "CCM"),
            (600, 500e-6, 3.5, "CCM"),
            (1000, 600e-6, 5.0, "CCM"),
            (2000, 400e-6, 8.0, "interleaved"),
            (3000, 300e-6, 12.0, "interleaved"),
        ]

        for power, inductance, idc, mode in levels:
            examples.append(DesignExample(
                name=f"PFC Inductor {power}W {mode}",
                category="inductor",
                application="pfc_inductor",
                description=f"Boost PFC inductor for {power}W, {mode} mode",
                topology="inductor",
                vin_min=85, vin_max=265, vin_is_ac=True,
                outputs=[{"voltage": 400, "current": power / 400}],
                frequency_hz=65000 if mode == "CCM" else 100000,
                design_notes=[
                    f"Inductance: {inductance*1e6:.0f}µH",
                    f"DC current: {idc}A, ripple ~30%",
                    "Powder core (Kool Mu) for DC bias" if power < 1000 else "Amorphous for high power",
                    f"{'Single winding' if mode == 'CCM' else 'Coupled inductors'} topology",
                ],
            ))

        return examples

    def _generate_filter_inductors(self) -> list[DesignExample]:
        """Generate EMI filter inductor examples."""
        examples = []

        # Common mode chokes
        for current in [1, 3, 5, 10, 20]:
            examples.append(DesignExample(
                name=f"Common Mode Choke {current}A",
                category="inductor",
                application="emi_filter",
                description=f"Common mode EMI choke, {current}A rated",
                topology="inductor",
                vin_min=85, vin_max=265, vin_is_ac=True,
                outputs=[{"voltage": 0, "current": current}],
                frequency_hz=100000,
                design_notes=[
                    f"Rated current: {current}A",
                    "Nanocrystalline or high-µ ferrite core",
                    "Bifilar winding for balance",
                    "High impedance 150kHz-30MHz",
                ],
            ))

        return examples

    def get_examples_by_category(self, category: str) -> list[DesignExample]:
        """Get all examples in a category."""
        if not self.examples:
            self.generate_all()
        return [e for e in self.examples if e.category == category]

    def get_examples_by_application(self, application: str) -> list[DesignExample]:
        """Get all examples for an application."""
        if not self.examples:
            self.generate_all()
        return [e for e in self.examples if e.application == application]

    def get_examples_by_power_range(self, min_power: float, max_power: float) -> list[DesignExample]:
        """Get examples within a power range."""
        if not self.examples:
            self.generate_all()
        results = []
        for e in self.examples:
            power = sum(o["voltage"] * o["current"] for o in e.outputs)
            if min_power <= power <= max_power:
                results.append(e)
        return results


def generate_application_examples(application: str) -> list[DesignExample]:
    """Generate examples for a specific application."""
    generator = ExampleGenerator()
    generator.generate_all()
    return generator.get_examples_by_application(application)


def get_example_count() -> dict:
    """Get count of examples by category."""
    generator = ExampleGenerator()
    examples = generator.generate_all()

    counts = {}
    for e in examples:
        counts[e.category] = counts.get(e.category, 0) + 1

    return {"total": len(examples), "by_category": counts}
