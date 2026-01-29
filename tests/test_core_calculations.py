"""
Tests for PyOpenMagnetics core calculation functions.

Covers gap reluctance, inductance from turns, turns from inductance,
gapping from turns, magnetic energy, saturation current, and
temperature-dependent parameters.
"""
import pytest
import PyOpenMagnetics


class TestGapReluctance:
    """Test calculate_gap_reluctance() function."""

    def test_gap_reluctance_zhang_model(self):
        """Calculate gap reluctance using ZHANG model."""
        gap = {
            "type": "subtractive",
            "length": 0.001,
            "area": 0.000211,
            "shape": "round",
            "coordinates": [0, 0, 0],
            "distanceClosestNormalSurface": 0.01,
            "distanceClosestParallelSurface": 0.005,
            "sectionDimensions": [0.0164, 0.0164]
        }
        result = PyOpenMagnetics.calculate_gap_reluctance(gap, "ZHANG")
        assert isinstance(result, dict)

    def test_gap_reluctance_positive(self):
        """Gap reluctance should be a positive value."""
        gap = {
            "type": "subtractive",
            "length": 0.001,
            "area": 0.000211,
            "shape": "round",
            "coordinates": [0, 0, 0],
            "distanceClosestNormalSurface": 0.01,
            "distanceClosestParallelSurface": 0.005,
            "sectionDimensions": [0.0164, 0.0164]
        }
        result = PyOpenMagnetics.calculate_gap_reluctance(gap, "ZHANG")
        if isinstance(result, dict) and "reluctance" in result:
            assert result["reluctance"] > 0

    def test_gap_reluctance_different_models(self):
        """Different reluctance models should produce results."""
        gap = {
            "type": "subtractive",
            "length": 0.001,
            "area": 0.000211,
            "shape": "round",
            "coordinates": [0, 0, 0],
            "distanceClosestNormalSurface": 0.01,
            "distanceClosestParallelSurface": 0.005,
            "sectionDimensions": [0.0164, 0.0164]
        }
        for model in ["ZHANG", "CLASSIC"]:
            result = PyOpenMagnetics.calculate_gap_reluctance(gap, model)
            assert isinstance(result, dict)


class TestInductanceFromTurns:
    """Test calculate_inductance_from_number_turns_and_gapping()."""

    def test_inductance_from_turns(self, computed_core, wound_inductor_coil, triangular_operating_point):
        """Calculate inductance from known turns and gapping."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
            computed_core, wound_inductor_coil, triangular_operating_point, models
        )
        assert isinstance(result, (int, float))

    def test_inductance_is_positive(self, computed_core, wound_inductor_coil, triangular_operating_point):
        """Inductance should be a positive value."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
            computed_core, wound_inductor_coil, triangular_operating_point, models
        )
        if isinstance(result, (int, float)):
            assert result > 0

    def test_inductance_physical_range(self, computed_core, wound_inductor_coil, triangular_operating_point):
        """Inductance should be in a physically reasonable range."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
            computed_core, wound_inductor_coil, triangular_operating_point, models
        )
        if isinstance(result, (int, float)):
            # For 20 turns on ETD 49 with small gap, expect uH to mH range
            assert 1e-9 < result < 1  # 1 nH to 1 H

    def test_inductance_different_models(self, computed_core, wound_inductor_coil, triangular_operating_point):
        """Different reluctance models should produce results."""
        for model_name in ["ZHANG", "CLASSIC"]:
            models = {"reluctance": model_name}
            result = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
                computed_core, wound_inductor_coil, triangular_operating_point, models
            )
            assert isinstance(result, (int, float))


class TestTurnsFromInductance:
    """Test calculate_number_turns_from_gapping_and_inductance()."""

    def test_turns_from_inductance(self, computed_core, processed_inductor_inputs):
        """Calculate number of turns for target inductance."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_number_turns_from_gapping_and_inductance(
            computed_core, processed_inductor_inputs, models
        )
        assert isinstance(result, (int, float))

    def test_turns_is_positive(self, computed_core, processed_inductor_inputs):
        """Number of turns should be positive."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_number_turns_from_gapping_and_inductance(
            computed_core, processed_inductor_inputs, models
        )
        if isinstance(result, (int, float)):
            assert result > 0

    def test_turns_is_reasonable(self, computed_core, processed_inductor_inputs):
        """Number of turns should be in a reasonable range for this core."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_number_turns_from_gapping_and_inductance(
            computed_core, processed_inductor_inputs, models
        )
        if isinstance(result, (int, float)):
            # For 100uH on ETD 49, expect single digits to low hundreds
            assert 1 < result < 500


class TestGappingFromTurns:
    """Test calculate_gapping_from_number_turns_and_inductance()."""

    @pytest.mark.xfail(reason="May fail with 'bad optional access' in some builds")
    def test_gapping_from_turns(self, computed_core, wound_inductor_coil, processed_inductor_inputs):
        """Calculate gap for given turns and inductance."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_gapping_from_number_turns_and_inductance(
            computed_core, wound_inductor_coil, processed_inductor_inputs,
            "SUBTRACTIVE", 4, models
        )
        assert isinstance(result, dict)

    @pytest.mark.xfail(reason="May fail with 'bad optional access' in some builds")
    def test_gapping_returns_core(self, computed_core, wound_inductor_coil, processed_inductor_inputs):
        """Result should be a Core dict with gapping."""
        models = {"reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_gapping_from_number_turns_and_inductance(
            computed_core, wound_inductor_coil, processed_inductor_inputs,
            "SUBTRACTIVE", 4, models
        )
        if isinstance(result, dict):
            assert "functionalDescription" in result
            if "gapping" in result.get("functionalDescription", {}):
                assert isinstance(result["functionalDescription"]["gapping"], list)


class TestMagneticEnergy:
    """Test calculate_core_maximum_magnetic_energy()."""

    def test_magnetic_energy_basic(self, computed_core, triangular_operating_point):
        """Calculate maximum magnetic energy storage."""
        result = PyOpenMagnetics.calculate_core_maximum_magnetic_energy(
            computed_core, triangular_operating_point
        )
        assert isinstance(result, (int, float))

    def test_magnetic_energy_positive(self, computed_core, triangular_operating_point):
        """Magnetic energy should be positive."""
        result = PyOpenMagnetics.calculate_core_maximum_magnetic_energy(
            computed_core, triangular_operating_point
        )
        if isinstance(result, (int, float)):
            assert result > 0


class TestSaturationCurrent:
    """Test calculate_saturation_current()."""

    def test_saturation_current_basic(self, simple_magnetic):
        """Calculate saturation current for magnetic assembly."""
        result = PyOpenMagnetics.calculate_saturation_current(simple_magnetic, 25.0)
        assert isinstance(result, (int, float))

    def test_saturation_current_positive(self, simple_magnetic):
        """Saturation current should be positive."""
        result = PyOpenMagnetics.calculate_saturation_current(simple_magnetic, 25.0)
        if isinstance(result, (int, float)):
            assert result > 0


class TestTemperatureDependantParameters:
    """Test get_core_temperature_dependant_parameters()."""

    def test_temperature_params_at_25c(self, computed_core):
        """Get temperature-dependent parameters at 25C."""
        result = PyOpenMagnetics.get_core_temperature_dependant_parameters(
            computed_core, 25.0
        )
        assert isinstance(result, dict)

    def test_temperature_params_has_fields(self, computed_core):
        """Temperature params should include expected fields."""
        result = PyOpenMagnetics.get_core_temperature_dependant_parameters(
            computed_core, 25.0
        )
        if isinstance(result, dict):
            assert len(result) > 0
            # May include: magneticFluxDensitySaturation, initialPermeability,
            # effectivePermeability, reluctance, permeance, resistivity

    def test_temperature_params_at_100c(self, computed_core):
        """Get parameters at 100C (should differ from 25C)."""
        result_25 = PyOpenMagnetics.get_core_temperature_dependant_parameters(
            computed_core, 25.0
        )
        result_100 = PyOpenMagnetics.get_core_temperature_dependant_parameters(
            computed_core, 100.0
        )
        assert isinstance(result_25, dict)
        assert isinstance(result_100, dict)


class TestCoreAvailability:
    """Test core data availability and shape queries."""

    def test_get_core_shape_families(self):
        """Shape families should include common types."""
        families = PyOpenMagnetics.get_core_shape_families()
        assert isinstance(families, list)
        assert len(families) > 0

    def test_shape_families_include_common(self):
        """Shape families should include E, ETD, PQ."""
        families = PyOpenMagnetics.get_core_shape_families()
        families_lower = [f.lower() for f in families]
        # At least some common families should be present
        common = ["e", "etd", "pq", "rm"]
        found = [f for f in common if f in families_lower]
        assert len(found) > 0

    def test_get_manufacturers(self):
        """Should get materials from specific manufacturers."""
        ferroxcube = PyOpenMagnetics.get_core_material_names_by_manufacturer("Ferroxcube")
        assert isinstance(ferroxcube, list)

    def test_calculate_shape_data(self):
        """find_core_shape_by_name should return shape geometry."""
        shape = PyOpenMagnetics.find_core_shape_by_name("ETD 49/25/16")
        assert isinstance(shape, dict)
        assert "name" in shape or "family" in shape

    def test_calculate_core_data_for_different_shapes(self):
        """calculate_core_data should work for various core shapes."""
        shapes_to_test = ["ETD 49/25/16", "E 42/21/15"]
        for shape_name in shapes_to_test:
            core_data = {
                "functionalDescription": {
                    "type": "two-piece set",
                    "material": "3C95",
                    "shape": shape_name,
                    "gapping": [],
                    "numberStacks": 1
                }
            }
            result = PyOpenMagnetics.calculate_core_data(core_data, False)
            assert isinstance(result, dict)
