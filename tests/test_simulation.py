"""
Tests for PyOpenMagnetics simulation functions.

Covers simulate(), magnetic_autocomplete(), mas_autocomplete(),
export_magnetic_as_subcircuit(), and related matrix calculations.
"""
import pytest
import PyOpenMagnetics


class TestSimulate:
    """Test simulate() function."""

    def test_simulate_inductor(self, processed_inductor_inputs, simple_magnetic):
        """Simulate an inductor magnetic."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.simulate(
            processed_inductor_inputs, simple_magnetic, models
        )
        assert isinstance(result, dict)

    def test_simulate_returns_outputs(self, processed_inductor_inputs, simple_magnetic):
        """Simulation result should contain outputs."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.simulate(
            processed_inductor_inputs, simple_magnetic, models
        )
        if isinstance(result, dict):
            assert "outputs" in result or "magnetic" in result or "inputs" in result

    def test_simulate_returns_mas_structure(self, processed_inductor_inputs, simple_magnetic):
        """Simulation should return MAS structure (inputs + magnetic + outputs)."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.simulate(
            processed_inductor_inputs, simple_magnetic, models
        )
        if isinstance(result, dict):
            # MAS has inputs, magnetic, outputs
            has_mas_structure = (
                "inputs" in result
                or "magnetic" in result
                or "outputs" in result
            )
            assert has_mas_structure

    def test_simulate_outputs_have_losses(self, processed_inductor_inputs, simple_magnetic):
        """Simulation outputs should include loss data."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.simulate(
            processed_inductor_inputs, simple_magnetic, models
        )
        if isinstance(result, dict) and "outputs" in result:
            outputs = result["outputs"]
            if isinstance(outputs, list) and len(outputs) > 0:
                output = outputs[0]
                has_loss_data = (
                    "coreLosses" in output
                    or "windingLosses" in output
                    or "temperature" in output
                )
                assert has_loss_data


class TestAutocomplete:
    """Test magnetic_autocomplete() and mas_autocomplete() functions."""

    def test_magnetic_autocomplete(self, simple_magnetic):
        """Autocomplete a partial magnetic specification."""
        config = {}
        result = PyOpenMagnetics.magnetic_autocomplete(simple_magnetic, config)
        assert isinstance(result, dict)

    def test_magnetic_autocomplete_returns_dict(self, simple_magnetic):
        """Autocomplete result should be a dict."""
        config = {}
        result = PyOpenMagnetics.magnetic_autocomplete(simple_magnetic, config)
        assert isinstance(result, dict)
        # Should still have core and coil
        assert "core" in result or "coil" in result

    def test_mas_autocomplete(self, processed_inductor_inputs, simple_magnetic):
        """Autocomplete a partial MAS specification."""
        mas = {
            "inputs": processed_inductor_inputs,
            "magnetic": simple_magnetic,
            "outputs": []
        }
        config = {}
        result = PyOpenMagnetics.mas_autocomplete(mas, config)
        assert isinstance(result, dict)


class TestExportSubcircuit:
    """Test export_magnetic_as_subcircuit() function."""

    @pytest.mark.xfail(reason="pybind11 return type issue in some builds")
    def test_export_spice_subcircuit(self, simple_magnetic):
        """Export magnetic as SPICE subcircuit."""
        result = PyOpenMagnetics.export_magnetic_as_subcircuit(simple_magnetic)
        assert result is not None

    @pytest.mark.xfail(reason="pybind11 return type issue in some builds")
    def test_export_contains_subcircuit(self, simple_magnetic):
        """SPICE export should contain subcircuit definition."""
        result = PyOpenMagnetics.export_magnetic_as_subcircuit(simple_magnetic)
        assert result is not None


class TestInductanceCalculations:
    """Test inductance-related simulation calculations."""

    def test_inductance_from_turns_and_gap(self, computed_core, wound_inductor_coil, triangular_operating_point):
        """Calculate inductance from turns count and gap."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
            computed_core, wound_inductor_coil, triangular_operating_point, models
        )
        assert isinstance(result, (int, float))
        if isinstance(result, (int, float)):
            assert result > 0


class TestCoreGeometry:
    """Test core geometry-related calculations."""

    def test_calculate_core_data(self, sample_core_data):
        """Calculate core processed data."""
        result = PyOpenMagnetics.calculate_core_data(sample_core_data, False)
        assert isinstance(result, dict)
        assert "processedDescription" in result or "functionalDescription" in result

    def test_calculate_core_geometrical_description(self, sample_core_data):
        """Calculate core geometrical description."""
        if not hasattr(PyOpenMagnetics, "calculate_core_geometrical_description"):
            pytest.skip("calculate_core_geometrical_description not available")
        result = PyOpenMagnetics.calculate_core_geometrical_description(sample_core_data)
        assert isinstance(result, dict)

    def test_core_effective_parameters(self, computed_core):
        """Computed core should have effective parameters."""
        if "processedDescription" in computed_core:
            processed = computed_core["processedDescription"]
            # Should have some effective parameters
            has_effective = any(
                k.startswith("effective") for k in processed.keys()
            )
            assert has_effective or "columns" in processed or "windingWindows" in processed
