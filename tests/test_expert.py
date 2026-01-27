"""Tests for Magnetic Expert module."""

import pytest


class TestKnowledge:
    """Test knowledge base."""

    def test_import_knowledge(self):
        from api.expert import APPLICATIONS, TOPOLOGIES, MATERIALS_GUIDE, TRADEOFFS
        assert APPLICATIONS is not None
        assert TOPOLOGIES is not None
        assert len(APPLICATIONS) > 10

    def test_application_structure(self):
        from api.expert.knowledge import APPLICATIONS
        usb = APPLICATIONS.get("usb_charger")
        assert usb is not None
        assert "name" in usb
        assert "variants" in usb
        assert "typical_topology" in usb
        assert "design_tips" in usb

    def test_topology_structure(self):
        from api.expert.knowledge import TOPOLOGIES
        flyback = TOPOLOGIES.get("flyback")
        assert flyback is not None
        assert "advantages" in flyback
        assert "disadvantages" in flyback
        assert "power_range" in flyback

    def test_suggest_topology(self):
        from api.expert.knowledge import suggest_topology

        # Low power should suggest flyback
        assert suggest_topology(20, isolated=True) == "flyback"

        # High power should suggest LLC or PSFB
        assert suggest_topology(500, isolated=True) in ["LLC", "phase_shifted_full_bridge"]

        # Non-isolated should suggest buck
        assert suggest_topology(50, isolated=False) == "buck"

    def test_suggest_core_material(self):
        from api.expert.knowledge import suggest_core_material

        # Low frequency
        mats = suggest_core_material(65000, "flyback")
        assert "3C90" in mats or "3C95" in mats

        # High frequency
        mats = suggest_core_material(500000, "LLC")
        assert "3F4" in mats or "N49" in mats


class TestExamples:
    """Test example generator."""

    def test_import_examples(self):
        from api.expert import ExampleGenerator, generate_application_examples
        assert ExampleGenerator is not None
        assert callable(generate_application_examples)

    def test_generate_all_examples(self):
        from api.expert.examples import ExampleGenerator

        gen = ExampleGenerator()
        examples = gen.generate_all()

        # Should generate many examples
        assert len(examples) > 50

    def test_example_structure(self):
        from api.expert.examples import ExampleGenerator

        gen = ExampleGenerator()
        examples = gen.generate_all()

        # Check first example structure
        ex = examples[0]
        assert ex.name
        assert ex.category
        assert ex.topology
        assert ex.vin_min > 0
        assert ex.outputs

    def test_examples_by_category(self):
        from api.expert.examples import ExampleGenerator

        gen = ExampleGenerator()
        gen.generate_all()

        consumer = gen.get_examples_by_category("consumer")
        assert len(consumer) > 10

        automotive = gen.get_examples_by_category("automotive")
        assert len(automotive) > 5

    def test_examples_by_application(self):
        from api.expert.examples import ExampleGenerator

        gen = ExampleGenerator()
        gen.generate_all()

        usb = gen.get_examples_by_application("usb_charger")
        assert len(usb) > 5

    def test_examples_by_power(self):
        from api.expert.examples import ExampleGenerator

        gen = ExampleGenerator()
        gen.generate_all()

        # Get examples in 50-100W range
        medium = gen.get_examples_by_power_range(50, 100)
        assert len(medium) > 3

    def test_example_to_design_params(self):
        from api.expert.examples import ExampleGenerator

        gen = ExampleGenerator()
        examples = gen.generate_all()

        ex = examples[0]
        params = ex.to_design_params()

        assert "topology" in params
        assert "vin_min" in params
        assert "outputs" in params

    def test_get_example_count(self):
        from api.expert.examples import get_example_count

        counts = get_example_count()
        assert counts["total"] > 50
        assert "consumer" in counts["by_category"]


class TestConversation:
    """Test conversation interface."""

    def test_import_conversation(self):
        from api.expert import MagneticExpert
        assert MagneticExpert is not None

    def test_start_conversation(self):
        from api.expert.conversation import MagneticExpert

        expert = MagneticExpert()
        response = expert.start()

        assert "message" in response
        assert "options" in response
        assert len(response["options"]) > 5

    def test_conversation_with_initial_input(self):
        from api.expert.conversation import MagneticExpert

        expert = MagneticExpert()
        response = expert.start("65W USB charger")

        # Should have parsed the input
        assert expert.state.application == "usb_charger"
        assert expert.state.power_level == 65

    def test_answer_flow(self):
        from api.expert.conversation import MagneticExpert

        expert = MagneticExpert()
        expert.start()

        # Answer application question
        response = expert.answer("application", "usb_charger")
        assert expert.state.application == "usb_charger"

    def test_explain_tradeoff(self):
        from api.expert.conversation import MagneticExpert

        expert = MagneticExpert()
        explanation = expert.explain_tradeoff("core_size_vs_loss")

        assert "flux density" in explanation.lower() or "loss" in explanation.lower()

    def test_get_application_guide(self):
        from api.expert.conversation import MagneticExpert

        expert = MagneticExpert()
        guide = expert.get_application_guide("usb_charger")

        assert "USB" in guide
        assert "flyback" in guide.lower()
        assert "Design Tips" in guide


class TestExpertIntegration:
    """Test expert integration with Design API."""

    def test_example_to_design(self):
        from api.expert.examples import ExampleGenerator
        from api.design import Design

        gen = ExampleGenerator()
        examples = gen.generate_all()

        # Find a simple example
        simple = [e for e in examples if e.topology == "flyback" and e.vin_is_ac]
        assert len(simple) > 0

        ex = simple[0]
        params = ex.to_design_params()

        # Should be able to create design from params
        builder = Design.flyback()
        if params["vin_is_ac"]:
            builder.vin_ac(params["vin_min"], params["vin_max"])
        else:
            builder.vin_dc(params["vin_min"], params["vin_max"])

        for out in params["outputs"]:
            builder.output(out["voltage"], out["current"])

        builder.fsw(params["frequency_hz"])

        # Should generate valid MAS
        mas = builder.to_mas()
        assert "designRequirements" in mas
        assert "operatingPoints" in mas
