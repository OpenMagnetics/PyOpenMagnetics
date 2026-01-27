# PyOpenMagnetics Skills Development Guide

## Vision

Make magnetic component design accessible to **hardware engineers** who think in terms of:
- "I need a flyback for 65W USB-C charger"
- "What core fits in 15mm height?"
- "Will this saturate at -40°C?"

NOT software constructs like JSON schemas, API calls, or class hierarchies.

---

## Implemented Skills (v0.1)

### Skill 1: Fluent Design API
**Status**: ✅ Implemented | **Location**: `api/design.py`

```python
from api.design import Design

# Hardware engineer writes this:
result = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3).solve()
```

**Gap**: Still requires Python knowledge. Need natural language interface.

---

### Skill 2: MCP Server
**Status**: ✅ Implemented | **Location**: `api/mcp/`

Two tools for AI assistants:
- `design_magnetic` - Design from specs or template
- `query_database` - Browse cores/materials/wires

8 offline templates: `usb_pd_20w`, `buck_5v_3a`, `boost_5v_1a`, etc.

**Gap**: Templates are generic. Need domain-specific templates by application.

---

### Skill 3: Streamlit GUI
**Status**: ✅ Implemented | **Location**: `api/gui/`

Run: `streamlit run api/gui/app.py`

Pages: Design, Database, Analysis, Compare

**Gap**: Forms are parameter-focused, not application-focused. HW engineer thinks "PoE injector" not "Vin=36-57V, Vout=12V".

---

### Skill 4: Application Examples
**Status**: ✅ Implemented | **Location**: `examples/`

Categories: consumer, automotive, industrial, telecom

**Gap**: Only 10 examples. Need 100+ covering real applications.

---

### Skill 5: FEMMT Bridge
**Status**: ✅ Implemented | **Location**: `api/bridges/femmt.py`

Export designs to FEMMT for FEM simulation.

---

### Skill 6: SW Architect Tools
**Status**: ✅ Implemented | **Location**: `api/architect/`

Code analysis, pattern documentation, API docs generation.

---

## Priority Skills To Implement

### Skill 7: Magnetic Expert (HIGH PRIORITY)
**Status**: 🔴 Not Started | **Target**: `api/expert/`

The core skill that makes PyOpenMagnetics accessible to HW engineers.

#### Purpose
An AI-powered expert system that:
1. Understands application context (not just electrical specs)
2. Asks the RIGHT questions a magnetics engineer would ask
3. Generates complete, manufacturable designs
4. Explains trade-offs in hardware terms

#### Expert Knowledge Base

```python
# api/expert/knowledge.py

APPLICATIONS = {
    # Consumer Electronics
    "usb_charger": {
        "variants": ["5W", "10W", "18W", "20W", "30W", "45W", "65W", "100W", "140W", "240W"],
        "standards": ["USB-BC 1.2", "QC 2.0", "QC 3.0", "PD 2.0", "PD 3.0", "PD 3.1 EPR"],
        "typical_topology": "flyback",
        "key_constraints": ["size", "efficiency", "EMI", "standby_power"],
        "safety": ["IEC 62368-1", "UL"],
        "questions": [
            "Single output or multi-output (5V/9V/12V/20V)?",
            "GaN or Si MOSFETs?",
            "Target form factor (cube, flat, travel)?",
            "Brand tier (budget, mainstream, premium)?"
        ]
    },

    "laptop_adapter": {
        "variants": ["45W", "65W", "90W", "100W", "140W", "180W", "230W"],
        "typical_topology": "flyback (<100W) | LLC (>100W)",
        "key_constraints": ["efficiency", "weight", "thermal"],
        "questions": [
            "Barrel connector or USB-C?",
            "Slim form factor required?",
            "Gaming laptop (high peak power)?"
        ]
    },

    "led_driver": {
        "variants": ["constant_current", "constant_voltage", "dimmable"],
        "typical_topology": "flyback | buck",
        "key_constraints": ["flicker", "PF", "THD", "dimming_range"],
        "standards": ["ENERGY STAR", "DLC", "Title 24"],
        "questions": [
            "Indoor or outdoor?",
            "Dimming method (0-10V, DALI, PWM, phase-cut)?",
            "LED string voltage and current?",
            "IP rating required?"
        ]
    },

    # Automotive
    "automotive_dcdc": {
        "variants": ["12V_aux", "48V_mild_hybrid", "HV_to_LV", "OBC"],
        "typical_topology": "buck | phase_shifted_full_bridge",
        "key_constraints": ["efficiency", "EMC", "temperature_range", "isolation"],
        "standards": ["AEC-Q200", "ISO 16750", "CISPR 25"],
        "questions": [
            "Voltage class (LV/48V/HV)?",
            "Ambient temperature range?",
            "Continuous vs peak power ratio?",
            "Functional safety level (ASIL)?"
        ]
    },

    "ev_obc": {
        "power_levels": ["3.3kW", "6.6kW", "11kW", "22kW"],
        "typical_topology": "LLC + PFC",
        "key_constraints": ["efficiency", "power_density", "bidirectional"],
        "questions": [
            "Single-phase or three-phase input?",
            "Bidirectional (V2G) required?",
            "Integrated or standalone?",
            "Liquid or air cooled?"
        ]
    },

    # Industrial
    "din_rail_psu": {
        "voltages": ["5V", "12V", "24V", "48V"],
        "powers": ["15W", "30W", "60W", "120W", "240W", "480W"],
        "typical_topology": "flyback (<150W) | LLC (>150W)",
        "standards": ["IEC 62368-1", "EN 61000-3-2"],
        "questions": [
            "DIN rail width constraint?",
            "Hazardous location (ATEX)?",
            "Redundancy/parallel operation?",
            "Communication (IO-Link, Modbus)?"
        ]
    },

    "medical_psu": {
        "classifications": ["BF", "CF", "2xMOPP", "2xMOOP"],
        "typical_topology": "flyback",
        "standards": ["IEC 60601-1", "IEC 60601-1-2"],
        "key_constraints": ["leakage_current", "isolation", "EMC"],
        "questions": [
            "Patient contact type (BF/CF)?",
            "Applied part or not?",
            "Home healthcare or clinical?",
            "Defibrillator-proof required?"
        ]
    },

    # Telecom/Datacenter
    "server_psu": {
        "form_factors": ["ATX", "1U", "CRPS", "OCP"],
        "powers": ["500W", "800W", "1200W", "1600W", "2000W", "3000W"],
        "typical_topology": "LLC + interleaved PFC",
        "standards": ["80 PLUS", "OCP", "CRPS"],
        "questions": [
            "Efficiency certification level?",
            "Hot-swap required?",
            "Redundancy (N+1, 2N)?",
            "48V direct or 12V?"
        ]
    },

    "poe": {
        "standards": ["802.3af (15W)", "802.3at (30W)", "802.3bt Type 3 (60W)", "802.3bt Type 4 (90W)"],
        "typical_topology": "flyback",
        "questions": [
            "PSE or PD side?",
            "PoE standard?",
            "Midspan or endspan?"
        ]
    },

    # Magnetics-specific
    "choke": {
        "types": ["EMI_filter", "PFC", "output_filter", "common_mode", "differential_mode"],
        "questions": [
            "Filter type (CM/DM/both)?",
            "Attenuation requirement?",
            "DC bias current?",
            "Frequency range?"
        ]
    },

    "current_transformer": {
        "applications": ["metering", "protection", "feedback"],
        "questions": [
            "Accuracy class?",
            "Burden impedance?",
            "Primary current range?",
            "Ratio and phase requirements?"
        ]
    },

    "gate_drive_transformer": {
        "applications": ["half_bridge", "full_bridge", "SiC", "GaN", "IGBT"],
        "questions": [
            "Drive voltage (+Vg/-Vg)?",
            "Isolation voltage?",
            "Switching frequency?",
            "dV/dt immunity?"
        ]
    }
}

# Common engineering trade-offs the expert explains
TRADEOFFS = {
    "core_size_vs_loss": """
        Smaller cores = higher flux density = more core loss = hotter
        Larger cores = lower flux density = lower loss = cooler but bigger
        Sweet spot depends on cooling and efficiency requirements
    """,

    "frequency_vs_size": """
        Higher frequency = smaller magnetics BUT:
        - More switching loss in semiconductors
        - More AC winding loss (skin/proximity)
        - More EMI
        - Needs better core material (lower loss at high f)
    """,

    "gap_vs_saturation": """
        More gap = higher saturation current BUT:
        - More turns needed for same inductance
        - More fringing flux = more EMI, eddy losses
        - Reduced AL value
    """,

    "litz_vs_solid": """
        Litz wire reduces AC resistance BUT:
        - Lower fill factor (more copper area needed)
        - More expensive
        - Harder to terminate
        Only beneficial when skin depth < wire radius
    """
}
```

#### Expert Conversation Flow

```python
# api/expert/conversation.py

class MagneticExpert:
    """
    Guides hardware engineers through magnetic design.
    Speaks their language, not code.
    """

    def start_design(self, application: str = None):
        """Start a new design conversation."""
        if application:
            return self._application_flow(application)
        return self._discovery_flow()

    def _discovery_flow(self):
        """Help user identify what they need."""
        return {
            "message": "What are you building?",
            "options": [
                "Power supply / charger",
                "DC-DC converter",
                "Motor drive",
                "Filter / EMI suppression",
                "Sensing / measurement",
                "Something else"
            ],
            "examples": [
                "USB-C charger for phone",
                "12V to 5V for Raspberry Pi",
                "PFC choke for server PSU",
                "Current sense transformer"
            ]
        }

    def _application_flow(self, app: str):
        """Guide through application-specific questions."""
        # ... ask relevant questions based on APPLICATIONS knowledge

    def explain_result(self, design_result):
        """Explain design in hardware terms."""
        return f"""
        ## Your Design: {design_result.core} with {design_result.material}

        ### Will it work?
        - Flux density: {design_result.bpk_tesla*1000:.0f} mT
          ({"OK - well below saturation" if design_result.bpk_tesla < 0.25 else "WARNING - close to saturation"})
        - Temperature rise: ~{design_result.temp_rise_c:.0f}°C
          ({"Acceptable" if design_result.temp_rise_c < 40 else "May need better cooling"})

        ### What to order
        - Core: {design_result.core} ({design_result.material})
        - Wire: {design_result.primary_wire}, {design_result.primary_turns} turns
        - Gap: {design_result.air_gap_mm:.2f}mm ({"spacer" if design_result.air_gap_mm > 0.5 else "ground core"})

        ### Watch out for
        {self._generate_warnings(design_result)}
        """
```

#### Example Generation Engine

```python
# api/expert/examples.py

class ExampleGenerator:
    """
    Generate hundreds of real-world design examples.
    Each example includes context, specs, and solution.
    """

    def generate_usb_pd_family(self):
        """Generate complete USB PD charger family."""
        examples = []

        for power in [20, 30, 45, 65, 100, 140]:
            for market in ["budget", "mainstream", "premium"]:
                for region in ["universal", "us_only", "eu_only"]:
                    example = self._create_usb_pd_example(power, market, region)
                    examples.append(example)

        return examples

    def generate_automotive_family(self):
        """Generate automotive DC-DC converter family."""
        examples = []

        # 48V mild hybrid variants
        for power in [500, 1000, 2000, 3000]:
            for cooling in ["air", "liquid"]:
                for temp_grade in ["commercial", "industrial", "automotive"]:
                    example = self._create_48v_dcdc_example(power, cooling, temp_grade)
                    examples.append(example)

        return examples

    def _create_usb_pd_example(self, power, market, region):
        """Create detailed USB PD example."""

        # Derive specs from power level and market
        if power <= 20:
            topology = "flyback"
            frequency = 100e3
            vout = 12  # Single output
        elif power <= 65:
            topology = "flyback"
            frequency = 130e3 if market == "premium" else 100e3
            vout = 20
        else:
            topology = "flyback"  # or LLC for premium
            frequency = 100e3
            vout = 28 if power >= 140 else 20

        vin_range = (85, 265) if region == "universal" else (100, 130) if region == "us_only" else (200, 240)

        # Size constraints by market
        if market == "budget":
            max_height = 25
            efficiency_target = 0.87
        elif market == "mainstream":
            max_height = 20
            efficiency_target = 0.90
        else:  # premium/GaN
            max_height = 15
            efficiency_target = 0.93

        return {
            "name": f"USB PD {power}W {market.title()} Charger",
            "description": f"""
                {power}W USB Power Delivery charger for {region.replace('_', ' ')} market.
                {market.title()} tier with {'GaN' if market == 'premium' else 'Si'} MOSFETs.
            """,
            "application": "usb_charger",
            "specs": {
                "topology": topology,
                "vin_ac": vin_range,
                "vout": vout,
                "iout": power / vout,
                "frequency_hz": frequency,
                "efficiency_target": efficiency_target,
                "max_height_mm": max_height,
            },
            "design_notes": [
                f"Target {'DoE Level VI' if region != 'eu_only' else 'CoC Tier 2'} efficiency",
                f"{'GaN enables smaller transformer' if market == 'premium' else 'Standard Si design'}",
                f"EMI filter sized for {'FCC Class B' if region != 'eu_only' else 'EN 55032 Class B'}",
            ],
            "bom_considerations": [
                "Core: EFD or EE for flat profile" if max_height < 18 else "Core: ETD or E for standard",
                f"Material: {'PC95' if frequency > 100e3 else '3C95'} for low loss at {frequency/1e3:.0f}kHz",
            ]
        }
```

---

### Skill 8: Natural Language Interface
**Status**: 🔴 Not Started | **Target**: `api/nlp/`

Allow engineers to describe needs in plain English:

```
Input: "I need a transformer for a 65W laptop charger,
        should fit in a slim adapter case, universal input"

Output: Expert asks clarifying questions, then generates design
```

#### Components Needed

```python
# api/nlp/parser.py

class SpecParser:
    """Parse natural language into design specs."""

    POWER_PATTERNS = [
        r"(\d+)\s*[wW](?:att)?",
        r"(\d+)\s*[vV](?:olt)?\s*[@x]\s*(\d+\.?\d*)\s*[aA]",
    ]

    VOLTAGE_PATTERNS = [
        r"(\d+)\s*[vV](?:olt)?\s*(?:input|in)",
        r"(\d+)\s*-\s*(\d+)\s*[vV](?:AC)?",
        r"universal\s*(?:input|AC)",  # -> (85, 265)
    ]

    APPLICATION_KEYWORDS = {
        "charger": "usb_charger",
        "adapter": "laptop_adapter",
        "laptop": "laptop_adapter",
        "phone": "usb_charger",
        "LED": "led_driver",
        "automotive": "automotive_dcdc",
        "car": "automotive_dcdc",
        "medical": "medical_psu",
        "server": "server_psu",
        "PoE": "poe",
        "telecom": "telecom_rectifier",
    }

    def parse(self, text: str) -> dict:
        """Extract design parameters from natural language."""
        specs = {}

        # Extract power
        # Extract voltages
        # Identify application
        # Extract constraints (size, efficiency, etc.)

        return specs
```

---

### Skill 9: Design Validation & DFM
**Status**: 🔴 Not Started | **Target**: `api/validation/`

Check designs against manufacturing and reliability constraints:

```python
# api/validation/dfm.py

class DFMChecker:
    """Design for Manufacturing validation."""

    def check_winding(self, design):
        """Check winding manufacturability."""
        issues = []

        # Check wire gauge availability
        if design.primary_wire not in STANDARD_WIRE_GAUGES:
            issues.append(f"Non-standard wire gauge: {design.primary_wire}")

        # Check turn count (too many = hard to wind)
        if design.primary_turns > 100:
            issues.append(f"High turn count ({design.primary_turns}) - consider larger core")

        # Check fill factor
        if design.fill_factor > 0.4:
            issues.append("Fill factor >40% - may be difficult to wind")

        # Check layer count
        if design.layer_count > 6:
            issues.append(f"{design.layer_count} layers - complex winding")

        return issues

    def check_thermal(self, design, ambient_max=40):
        """Check thermal margins."""
        issues = []

        max_temp = ambient_max + design.temp_rise_c

        if max_temp > 120:
            issues.append(f"Core may exceed Curie temperature at {ambient_max}°C ambient")

        if max_temp > 105:
            issues.append(f"Wire insulation class may be exceeded ({max_temp}°C)")

        return issues

    def check_safety(self, design, standard="IEC 62368-1"):
        """Check safety compliance."""
        issues = []

        # Creepage/clearance
        # Insulation coordination
        # Temperature class

        return issues
```

---

### Skill 10: Component Sourcing
**Status**: 🔴 Not Started | **Target**: `api/sourcing/`

Help find and order actual components:

```python
# api/sourcing/finder.py

class ComponentFinder:
    """Find real components for designs."""

    DISTRIBUTORS = {
        "cores": ["Digi-Key", "Mouser", "Farnell", "LCSC"],
        "wire": ["MWS Wire", "Elektrisola", "Furukawa"],
    }

    def find_core(self, shape: str, material: str) -> list[dict]:
        """Find purchasable cores matching spec."""
        results = []

        # Search distributor APIs
        # Match by shape name variants
        # Include pricing and availability

        return results

    def suggest_alternatives(self, design) -> list[dict]:
        """Suggest alternative components."""
        # Same size, different material
        # Same material, different size
        # Different manufacturer equivalents

        return alternatives
```

---

## Development Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] Fluent Design API
- [x] MCP Server with templates
- [x] Streamlit GUI
- [x] Basic examples
- [x] FEMMT bridge
- [x] SW Architect tools

### Phase 2: Expert System (Next Priority)
- [ ] Application knowledge base
- [ ] Expert conversation flow
- [ ] Example generation engine (100+ examples)
- [ ] Trade-off explanations

### Phase 3: Natural Language
- [ ] Spec parser from English
- [ ] Clarifying question generation
- [ ] Context understanding

### Phase 4: Validation & DFM
- [ ] Manufacturing checks
- [ ] Thermal validation
- [ ] Safety compliance
- [ ] Reliability estimation

### Phase 5: Sourcing & BOM
- [ ] Distributor integration
- [ ] Alternative suggestions
- [ ] Cost estimation
- [ ] Lead time tracking

---

## Hardware Engineer Personas

### Persona 1: Application Engineer
**Background**: EE degree, designs power supplies, limited magnetics expertise
**Needs**:
- "Just give me something that works"
- Wants proven designs for common applications
- Needs to explain design to management

**How we help**:
- Application templates with full context
- Design reports with plain English explanations
- Comparison with reference designs

### Persona 2: Power Electronics Specialist
**Background**: Deep PE knowledge, some magnetics experience
**Needs**:
- Optimize for specific constraints
- Understand trade-offs
- Push the boundaries

**How we help**:
- Detailed parameter control
- Trade-off visualizations
- What-if analysis

### Persona 3: System Architect
**Background**: High-level design, cost/schedule focused
**Needs**:
- Quick feasibility check
- Size/cost/efficiency trade-offs
- Multiple design options

**How we help**:
- Application-based entry point
- Design space exploration
- Multi-design comparison

---

## Contributing

### Adding New Applications

1. Add to `APPLICATIONS` dict in `api/expert/knowledge.py`
2. Include:
   - Variants (power levels, form factors)
   - Typical topologies
   - Key constraints
   - Relevant standards
   - Clarifying questions

### Adding Examples

1. Create in `examples/{category}/`
2. Follow template:
```python
"""
{Application Name} - {Topology} Design

Application: {Real-world description}
Real-world equivalents: {Actual products}

Specifications:
- Input: {range}
- Output: {voltage} @ {current} ({power})
- Frequency: {value}
- Key constraints: {list}
"""

from api.design import Design

def design_{name}():
    # Design implementation
    ...
```

3. Add test in `tests/test_examples_validation.py`

### Improving Expert Knowledge

The expert is only as good as its knowledge base. Contribute:
- Application-specific gotchas
- Common design mistakes
- Industry best practices
- Real-world failure modes

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time from "I need X" to valid design | ~10 min (with code) | <2 min (conversation) |
| Application templates | 8 | 50+ |
| Worked examples | 10 | 100+ |
| Design explanations | Code comments | Plain English reports |
| HW engineer adoption | Low (needs Python) | High (GUI + NLP) |
