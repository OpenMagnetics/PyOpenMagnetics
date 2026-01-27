"""
Magnetic Expert Conversation System.

Natural language interface for hardware engineers.
Asks the right questions, explains trade-offs, generates designs.
"""

from typing import Optional
from dataclasses import dataclass, field
from .knowledge import APPLICATIONS, TOPOLOGIES, TRADEOFFS, suggest_topology
from .examples import ExampleGenerator, DesignExample


@dataclass
class ConversationState:
    """Tracks the state of a design conversation."""
    application: Optional[str] = None
    power_level: Optional[float] = None
    input_voltage: Optional[tuple] = None
    input_is_ac: bool = True
    outputs: list[dict] = field(default_factory=list)
    constraints: dict = field(default_factory=dict)
    questions_asked: list[str] = field(default_factory=list)
    answers: dict = field(default_factory=dict)


class MagneticExpert:
    """
    AI-powered magnetic design expert.

    Guides hardware engineers through design process using
    domain knowledge and natural conversation.
    """

    def __init__(self):
        self.state = ConversationState()
        self.example_generator = ExampleGenerator()

    def start(self, initial_input: str = None) -> dict:
        """
        Start a new design conversation.

        Args:
            initial_input: Optional initial description from user

        Returns:
            dict with message and options/questions
        """
        self.state = ConversationState()

        if initial_input:
            return self._parse_initial_input(initial_input)

        return {
            "message": "What are you designing today?",
            "options": [
                {"label": "USB charger / Power adapter", "value": "usb_charger"},
                {"label": "Laptop adapter", "value": "laptop_adapter"},
                {"label": "LED driver", "value": "led_driver"},
                {"label": "Automotive DC-DC", "value": "automotive_dcdc"},
                {"label": "Industrial power supply", "value": "din_rail_psu"},
                {"label": "Medical equipment PSU", "value": "medical_psu"},
                {"label": "PoE device", "value": "poe"},
                {"label": "Inductor / Choke", "value": "inductor"},
                {"label": "Something else", "value": "custom"},
            ],
            "examples": [
                "65W USB-C charger for laptops",
                "12V 3A buck converter",
                "PFC inductor for 1kW power supply",
                "Gate driver transformer for SiC",
            ],
        }

    def _parse_initial_input(self, text: str) -> dict:
        """Parse natural language input to extract specs."""
        text_lower = text.lower()

        # Detect application
        app_keywords = {
            "usb": "usb_charger",
            "charger": "usb_charger",
            "phone": "usb_charger",
            "laptop": "laptop_adapter",
            "notebook": "laptop_adapter",
            "led": "led_driver",
            "light": "led_driver",
            "automotive": "automotive_dcdc",
            "car": "automotive_dcdc",
            "48v": "automotive_dcdc",
            "medical": "medical_psu",
            "hospital": "medical_psu",
            "din": "din_rail_psu",
            "industrial": "din_rail_psu",
            "poe": "poe",
            "ethernet": "poe",
            "server": "server_psu",
            "inductor": "inductor",
            "choke": "inductor",
            "pfc": "inductor",
        }

        for keyword, app in app_keywords.items():
            if keyword in text_lower:
                self.state.application = app
                break

        # Detect power level
        import re
        power_match = re.search(r'(\d+)\s*[wW]', text)
        if power_match:
            self.state.power_level = float(power_match.group(1))

        # Detect voltage
        voltage_match = re.search(r'(\d+)\s*[vV]', text)
        if voltage_match:
            v = float(voltage_match.group(1))
            if v < 50:  # Likely output voltage
                self.state.outputs = [{"voltage": v, "current": 0}]
            else:  # Likely input voltage
                self.state.input_voltage = (v * 0.9, v * 1.1)

        # Continue conversation based on what we know
        return self._next_question()

    def answer(self, question_id: str, answer) -> dict:
        """
        Process user's answer to a question.

        Args:
            question_id: ID of the question being answered
            answer: User's answer (string or selection)

        Returns:
            dict with next question or design result
        """
        self.state.answers[question_id] = answer
        self.state.questions_asked.append(question_id)

        # Update state based on answer
        if question_id == "application":
            self.state.application = answer
        elif question_id == "power":
            self.state.power_level = float(answer)
        elif question_id == "input_voltage":
            if answer == "universal":
                self.state.input_voltage = (85, 265)
                self.state.input_is_ac = True
            elif answer == "12v_dc":
                self.state.input_voltage = (10, 14)
                self.state.input_is_ac = False
            elif answer == "48v_dc":
                self.state.input_voltage = (36, 57)
                self.state.input_is_ac = False
            # ... handle other cases
        elif question_id == "output_voltage":
            v = float(answer)
            if self.state.outputs:
                self.state.outputs[0]["voltage"] = v
            else:
                self.state.outputs = [{"voltage": v, "current": 0}]
        elif question_id == "output_current":
            if self.state.outputs:
                self.state.outputs[0]["current"] = float(answer)

        return self._next_question()

    def _next_question(self) -> dict:
        """Determine and return the next question to ask."""

        # Check what info we still need
        if not self.state.application:
            return self.start()

        app_info = APPLICATIONS.get(self.state.application, {})

        if not self.state.power_level and "power" not in self.state.questions_asked:
            return self._ask_power(app_info)

        if not self.state.input_voltage and "input_voltage" not in self.state.questions_asked:
            return self._ask_input_voltage(app_info)

        if not self.state.outputs and "output_voltage" not in self.state.questions_asked:
            return self._ask_output(app_info)

        # Check for application-specific questions
        questions = app_info.get("questions_to_ask", [])
        for q in questions:
            q_id = q.replace(" ", "_").replace("?", "")[:20].lower()
            if q_id not in self.state.questions_asked:
                return {
                    "question_id": q_id,
                    "message": q,
                    "type": "text",  # or provide options
                }

        # We have enough info - generate design
        return self._generate_design()

    def _ask_power(self, app_info: dict) -> dict:
        """Ask about power level."""
        variants = app_info.get("variants", {})

        if variants:
            options = []
            for name, spec in variants.items():
                if isinstance(spec, dict) and "power" in spec:
                    p = spec["power"]
                    if isinstance(p, tuple):
                        options.append({"label": f"{p[0]}-{p[1]}W", "value": str(p[1])})
                    else:
                        options.append({"label": f"{p}W", "value": str(p)})

            return {
                "question_id": "power",
                "message": "What power level do you need?",
                "options": options[:8],  # Limit options
                "allow_custom": True,
            }

        return {
            "question_id": "power",
            "message": "What is the required output power (in Watts)?",
            "type": "number",
            "hint": "Total output power, e.g., 65 for a 65W charger",
        }

    def _ask_input_voltage(self, app_info: dict) -> dict:
        """Ask about input voltage."""
        input_options = app_info.get("input_voltage", {})

        if input_options:
            options = [
                {"label": "Universal AC (85-265V)", "value": "universal"},
            ]
            if "us_only" in input_options:
                options.append({"label": "US only (100-130V)", "value": "us_only"})
            if "eu_only" in input_options:
                options.append({"label": "EU only (200-240V)", "value": "eu_only"})

            return {
                "question_id": "input_voltage",
                "message": "What is the input voltage?",
                "options": options,
            }

        return {
            "question_id": "input_voltage",
            "message": "What is the input voltage range?",
            "type": "text",
            "hint": "e.g., '85-265V AC' or '36-57V DC'",
        }

    def _ask_output(self, app_info: dict) -> dict:
        """Ask about output requirements."""
        return {
            "question_id": "output_voltage",
            "message": "What output voltage do you need?",
            "type": "number",
            "hint": "e.g., 12 for 12V output",
            "follow_up": {
                "question_id": "output_current",
                "message": "And what output current?",
                "type": "number",
                "hint": "In Amps, e.g., 5 for 5A",
            },
        }

    def _generate_design(self) -> dict:
        """Generate design based on collected information."""
        # Calculate derived parameters
        if not self.state.outputs[0].get("current") and self.state.power_level:
            v = self.state.outputs[0]["voltage"]
            self.state.outputs[0]["current"] = self.state.power_level / v

        # Suggest topology
        power = self.state.power_level or sum(
            o["voltage"] * o["current"] for o in self.state.outputs
        )
        topology = suggest_topology(power, isolated=True)

        # Find similar examples
        examples = self.example_generator.generate_all()
        similar = [e for e in examples if e.application == self.state.application]
        similar = [e for e in similar
                   if abs(sum(o["voltage"] * o["current"] for o in e.outputs) - power) < power * 0.3]

        return {
            "status": "ready_to_design",
            "message": f"""
Based on your requirements, I recommend a **{topology}** topology.

**Your Specs:**
- Input: {self.state.input_voltage[0]:.0f}-{self.state.input_voltage[1]:.0f}V {'AC' if self.state.input_is_ac else 'DC'}
- Output: {self.state.outputs[0]['voltage']:.1f}V @ {self.state.outputs[0]['current']:.2f}A ({power:.0f}W)

**Similar designs you can reference:**
{self._format_similar_examples(similar[:3])}

Ready to run the design solver?
            """,
            "design_params": {
                "topology": topology,
                "vin_min": self.state.input_voltage[0],
                "vin_max": self.state.input_voltage[1],
                "vin_is_ac": self.state.input_is_ac,
                "outputs": self.state.outputs,
                "frequency_hz": 100000,
            },
            "similar_examples": similar[:5],
            "actions": [
                {"label": "Run Design Solver", "action": "solve"},
                {"label": "Adjust Parameters", "action": "edit"},
                {"label": "See More Examples", "action": "examples"},
            ],
        }

    def _format_similar_examples(self, examples: list) -> str:
        """Format examples for display."""
        if not examples:
            return "- No similar examples found"

        lines = []
        for e in examples:
            power = sum(o["voltage"] * o["current"] for o in e.outputs)
            lines.append(f"- {e.name} ({power:.0f}W)")

        return "\n".join(lines)

    def explain_tradeoff(self, topic: str) -> str:
        """
        Explain a design trade-off in plain language.

        Args:
            topic: Trade-off topic (e.g., "core_size_vs_loss")

        Returns:
            Plain language explanation
        """
        tradeoff = TRADEOFFS.get(topic)
        if tradeoff:
            return f"**{tradeoff['description']}**\n\n{tradeoff['explanation']}"

        return f"I don't have specific guidance on '{topic}'. Could you rephrase?"

    def explain_result(self, design_result) -> str:
        """
        Explain a design result in hardware engineer terms.

        Args:
            design_result: DesignResult from PyOpenMagnetics

        Returns:
            Plain language explanation
        """
        # Assess the design
        flux_ok = design_result.bpk_tesla < 0.25
        temp_ok = design_result.temp_rise_c < 40
        margin_ok = design_result.saturation_margin > 0.2

        explanation = f"""
## Design Result: {design_result.core} with {design_result.material}

### Quick Assessment
- **Flux Density**: {design_result.bpk_tesla * 1000:.0f} mT {'✓ Good' if flux_ok else '⚠️ High - may saturate'}
- **Temperature Rise**: ~{design_result.temp_rise_c:.0f}°C {'✓ Acceptable' if temp_ok else '⚠️ Hot - needs cooling'}
- **Saturation Margin**: {design_result.saturation_margin * 100:.0f}% {'✓ Safe' if margin_ok else '⚠️ Tight'}

### What to Order
| Component | Specification |
|-----------|---------------|
| Core | {design_result.core} ({design_result.material}) |
| Primary Wire | {design_result.primary_wire}, {design_result.primary_turns} turns |
| Air Gap | {design_result.air_gap_mm:.2f} mm {'(spacer)' if design_result.air_gap_mm > 0.5 else '(ground core)'} |

### Expected Performance
- Core Loss: {design_result.core_loss_w:.2f} W
- Copper Loss: {design_result.copper_loss_w:.2f} W
- **Total Loss: {design_result.total_loss_w:.2f} W**

### Things to Check
"""
        warnings = []

        if not flux_ok:
            warnings.append("- Consider larger core to reduce flux density")

        if not temp_ok:
            warnings.append("- Add heatsinking or increase core size")

        if not margin_ok:
            warnings.append("- Increase air gap or reduce turns for saturation margin")

        if design_result.primary_turns > 80:
            warnings.append("- High turn count - consider larger core to reduce turns")

        if not warnings:
            warnings.append("- Design looks good! Verify with prototype.")

        explanation += "\n".join(warnings)

        return explanation

    def get_application_guide(self, application: str) -> str:
        """
        Get a complete guide for an application.

        Args:
            application: Application key

        Returns:
            Comprehensive guide text
        """
        app = APPLICATIONS.get(application)
        if not app:
            return f"Unknown application: {application}"

        guide = f"""
# {app['name']} Design Guide

{app.get('description', '')}

## Typical Specifications
- Power range: {app.get('power_range', 'Varies')} W
- Typical topology: **{app.get('typical_topology', 'Various')}**

## Variants
"""
        for name, spec in app.get('variants', {}).items():
            guide += f"- **{name}**: {spec}\n"

        guide += f"""
## Key Design Constraints
"""
        for c in app.get('key_constraints', []):
            guide += f"- {c}\n"

        guide += f"""
## Applicable Standards
"""
        for s in app.get('standards', []):
            guide += f"- {s}\n"

        guide += f"""
## Design Tips
"""
        for tip in app.get('design_tips', []):
            guide += f"- {tip}\n"

        guide += f"""
## Common Mistakes to Avoid
"""
        for mistake in app.get('common_mistakes', []):
            guide += f"- {mistake}\n"

        return guide
