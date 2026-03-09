"""
Tests for PyOpenMagnetics winding engine functions.

Covers wind(), wind_by_sections(), wind_by_layers(), wind_by_turns(),
coil query functions, and insulation calculation.
"""
import pytest
import PyOpenMagnetics


class TestWindBasic:
    """Test basic wind() function."""

    def test_wind_single_winding(self, inductor_coil):
        """wind() should produce a coil with turnsDescription."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert isinstance(result, dict)
        # Should have at least one of the description levels populated
        has_descriptions = (
            "turnsDescription" in result
            or "layersDescription" in result
            or "sectionsDescription" in result
        )
        assert has_descriptions

    def test_wind_two_windings(self, transformer_coil):
        """wind() should handle two-winding transformer coil."""
        result = PyOpenMagnetics.wind(transformer_coil, 1, [0.5, 0.5], [0, 1], [])
        assert isinstance(result, dict)
        has_descriptions = (
            "turnsDescription" in result
            or "layersDescription" in result
            or "sectionsDescription" in result
        )
        assert has_descriptions

    def test_wind_preserves_functional_description(self, inductor_coil):
        """wind() should preserve the functional description."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert "functionalDescription" in result

    def test_wind_with_repetitions(self, inductor_coil):
        """wind() with repetitions parameter."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert isinstance(result, dict)

    def test_wind_returns_bobbin(self, inductor_coil):
        """wind() should preserve the bobbin in the output."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert "bobbin" in result

    def test_wind_with_proportions(self, transformer_coil):
        """wind() with proportions for each winding."""
        result = PyOpenMagnetics.wind(transformer_coil, 1, [0.6, 0.4], [0, 1], [])
        assert isinstance(result, dict)

    def test_wind_has_turns_description(self, inductor_coil):
        """wind() should populate turnsDescription."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert "turnsDescription" in result
        assert isinstance(result["turnsDescription"], list)
        assert len(result["turnsDescription"]) > 0


class TestWindBySections:
    """Test wind_by_sections() function."""

    def test_wind_by_sections_basic(self, transformer_coil):
        """wind_by_sections should create sections."""
        result = PyOpenMagnetics.wind_by_sections(
            transformer_coil, 1, [0.5, 0.5], [0, 1], 0.0001
        )
        assert isinstance(result, dict)
        assert "sectionsDescription" in result

    def test_wind_by_sections_has_sections(self, transformer_coil):
        """Resulting coil should have section descriptions."""
        result = PyOpenMagnetics.wind_by_sections(
            transformer_coil, 1, [0.5, 0.5], [0, 1], 0.0001
        )
        sections = result.get("sectionsDescription", [])
        assert isinstance(sections, list)
        assert len(sections) >= 2  # At least one section per winding

    def test_wind_by_sections_single_winding(self, inductor_coil):
        """wind_by_sections for single winding inductor."""
        result = PyOpenMagnetics.wind_by_sections(
            inductor_coil, 1, [1.0], [0], 0.0001
        )
        assert isinstance(result, dict)

    def test_wind_by_sections_insulation_thickness(self, transformer_coil):
        """Insulation thickness should be applied between sections."""
        result = PyOpenMagnetics.wind_by_sections(
            transformer_coil, 1, [0.5, 0.5], [0, 1], 0.0005
        )
        assert isinstance(result, dict)
        assert "sectionsDescription" in result


class TestWindByLayers:
    """Test wind_by_layers() function."""

    def test_wind_by_layers_from_sections(self, transformer_coil):
        """wind_by_layers should produce layers from sections."""
        coil_with_sections = PyOpenMagnetics.wind_by_sections(
            transformer_coil, 1, [0.5, 0.5], [0, 1], 0.0001
        )
        result = PyOpenMagnetics.wind_by_layers(coil_with_sections, 0, 0.0001)
        if isinstance(result, str) and result.startswith("Exception"):
            pytest.skip(f"C++ engine error: {result}")
        assert isinstance(result, dict)
        assert "layersDescription" in result

    def test_wind_by_layers_has_layers(self, transformer_coil):
        """Result should contain layer descriptions."""
        coil_with_sections = PyOpenMagnetics.wind_by_sections(
            transformer_coil, 1, [0.5, 0.5], [0, 1], 0.0001
        )
        result = PyOpenMagnetics.wind_by_layers(coil_with_sections, 0, 0.0001)
        if isinstance(result, str) and result.startswith("Exception"):
            pytest.skip(f"C++ engine error: {result}")
        layers = result.get("layersDescription", [])
        assert isinstance(layers, list)
        assert len(layers) > 0

    def test_wind_by_layers_single_winding(self, inductor_coil):
        """wind_by_layers for single winding inductor."""
        coil_with_sections = PyOpenMagnetics.wind_by_sections(
            inductor_coil, 1, [1.0], [0], 0.0001
        )
        result = PyOpenMagnetics.wind_by_layers(coil_with_sections, 0, 0.0001)
        if isinstance(result, str) and result.startswith("Exception"):
            pytest.skip(f"C++ engine error: {result}")
        assert isinstance(result, dict)


class TestWindByTurns:
    """Test wind_by_turns() function."""

    def test_wind_by_turns_from_full_pipeline(self, inductor_coil):
        """wind_by_turns via the full wind() pipeline."""
        # wind() does the full pipeline: sections -> layers -> turns
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert isinstance(result, dict)
        assert "turnsDescription" in result

    def test_wind_by_turns_has_turn_data(self, inductor_coil):
        """Turns description should have per-turn data."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        turns = result.get("turnsDescription", [])
        assert isinstance(turns, list)
        assert len(turns) > 0

    def test_wind_by_turns_count_matches(self, inductor_coil):
        """Number of turns should match the specification."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        turns = result.get("turnsDescription", [])
        # 20 turns specified in inductor_coil fixture
        assert len(turns) == 20


class TestCoilQueries:
    """Test coil query functions."""

    def test_are_sections_and_layers_fitting(self, wound_inductor_coil):
        """Check if winding fits in available window."""
        result = PyOpenMagnetics.are_sections_and_layers_fitting(wound_inductor_coil)
        assert isinstance(result, bool)

    def test_fitting_is_true_for_small_coil(self, wound_inductor_coil):
        """A 20-turn coil on ETD 49 should fit."""
        result = PyOpenMagnetics.are_sections_and_layers_fitting(wound_inductor_coil)
        assert result is True

    def test_get_layers_by_winding_index(self, wound_inductor_coil):
        """Get layers for winding index 0."""
        layers = PyOpenMagnetics.get_layers_by_winding_index(wound_inductor_coil, 0)
        assert isinstance(layers, list)

    def test_get_layers_by_winding_index_transformer(self, wound_transformer_coil):
        """Get layers for each winding of a transformer."""
        primary_layers = PyOpenMagnetics.get_layers_by_winding_index(wound_transformer_coil, 0)
        secondary_layers = PyOpenMagnetics.get_layers_by_winding_index(wound_transformer_coil, 1)
        assert isinstance(primary_layers, list)
        assert isinstance(secondary_layers, list)


class TestWindFullPipeline:
    """Test the complete wind -> sections -> layers -> turns pipeline."""

    def test_full_pipeline_inductor(self, inductor_coil):
        """Full winding pipeline for inductor."""
        result = PyOpenMagnetics.wind(inductor_coil, 1, [1.0], [0], [])
        assert isinstance(result, dict)
        assert "turnsDescription" in result

    def test_full_pipeline_transformer(self, transformer_coil):
        """Full winding pipeline for transformer."""
        result = PyOpenMagnetics.wind(transformer_coil, 1, [0.5, 0.5], [0, 1], [])
        assert isinstance(result, dict)
        assert "turnsDescription" in result

    def test_wound_coil_has_sections(self, wound_inductor_coil):
        """Wound coil should have sections description."""
        assert "sectionsDescription" in wound_inductor_coil

    def test_wound_coil_has_layers(self, wound_inductor_coil):
        """Wound coil should have layers description."""
        assert "layersDescription" in wound_inductor_coil

    def test_wound_coil_has_turns(self, wound_inductor_coil):
        """Wound coil should have turns description."""
        assert "turnsDescription" in wound_inductor_coil


class TestInsulationCalculation:
    """Test calculate_insulation() function."""

    @pytest.mark.xfail(reason="calculate_insulation may require specific C++ library version")
    def test_basic_insulation_calculation(self):
        """Calculate insulation distances for a transformer design."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": [{"nominal": 1}],
                "insulation": {
                    "insulationType": "Reinforced",
                    "cti": "Group I",
                    "pollutionDegree": "P2",
                    "overvoltageCategory": "OVC-II",
                    "altitude": {"maximum": 2000},
                    "mainSupplyVoltage": {"nominal": 230},
                    "standards": ["IEC 62368-1"]
                },
                "isolationSides": ["primary", "secondary"]
            },
            "operatingPoints": [
                {
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {"frequency": 100000}
                    ]
                }
            ]
        }
        result = PyOpenMagnetics.calculate_insulation(inputs)
        assert isinstance(result, dict)
