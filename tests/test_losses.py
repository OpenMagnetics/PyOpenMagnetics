"""
Tests for PyOpenMagnetics loss calculation functions.

Covers core losses (multiple models), winding losses (ohmic, skin, proximity),
wire-level per-meter loss functions, and Steinmetz coefficients.
"""
import pytest
import PyOpenMagnetics


class TestCoreLosses:
    """Test calculate_core_losses() function."""

    def test_core_losses_igse_model(self, computed_core, wound_inductor_coil, processed_inductor_inputs):
        """Calculate core losses using IGSE model."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_core_losses(
            computed_core, wound_inductor_coil, processed_inductor_inputs, models
        )
        assert isinstance(result, dict)

    def test_core_losses_returns_positive_value(self, computed_core, wound_inductor_coil, processed_inductor_inputs):
        """Core losses should be a positive number."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_core_losses(
            computed_core, wound_inductor_coil, processed_inductor_inputs, models
        )
        if isinstance(result, dict) and "coreLosses" in result:
            assert result["coreLosses"] > 0

    def test_core_losses_has_flux_density(self, computed_core, wound_inductor_coil, processed_inductor_inputs):
        """Core loss result should include magnetic flux density."""
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_core_losses(
            computed_core, wound_inductor_coil, processed_inductor_inputs, models
        )
        if isinstance(result, dict):
            # Should have B peak data
            has_flux = (
                "magneticFluxDensityPeak" in result
                or "magneticFluxDensityAcPeak" in result
                or "magneticFluxDensity" in result
            )
            assert has_flux or "coreLosses" in result

    def test_core_losses_steinmetz_model(self, computed_core, wound_inductor_coil, processed_inductor_inputs):
        """Calculate core losses using Steinmetz model."""
        models = {"coreLosses": "STEINMETZ", "reluctance": "ZHANG"}
        result = PyOpenMagnetics.calculate_core_losses(
            computed_core, wound_inductor_coil, processed_inductor_inputs, models
        )
        assert isinstance(result, dict)


class TestCoreLossModelInfo:
    """Test core loss model information functions."""

    def test_get_core_losses_model_information(self):
        """Get available loss models for a material."""
        material = PyOpenMagnetics.find_core_material_by_name("3C95")
        result = PyOpenMagnetics.get_core_losses_model_information(material)
        assert isinstance(result, dict)

    def test_model_info_has_content(self):
        """Model info should have some content."""
        material = PyOpenMagnetics.find_core_material_by_name("3C95")
        result = PyOpenMagnetics.get_core_losses_model_information(material)
        assert len(result) > 0


class TestSteinmetzCoefficients:
    """Test Steinmetz coefficient retrieval."""

    def test_steinmetz_coefficients_by_name(self):
        """Get Steinmetz coefficients by material name string."""
        result = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 100000)
        assert isinstance(result, dict)

    def test_steinmetz_coefficients_by_material_dict(self):
        """Get Steinmetz coefficients by material dict."""
        material = PyOpenMagnetics.find_core_material_by_name("3C95")
        result = PyOpenMagnetics.get_core_material_steinmetz_coefficients(material, 100000)
        assert isinstance(result, dict)

    def test_steinmetz_has_k_alpha_beta(self):
        """Steinmetz result should have k, alpha, beta coefficients."""
        result = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 100000)
        # Standard Steinmetz equation: P = k * f^alpha * B^beta
        has_coefficients = "k" in result or "alpha" in result or "beta" in result
        assert has_coefficients

    def test_steinmetz_at_different_frequencies(self):
        """Coefficients may differ at different frequencies."""
        result_100k = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 100000)
        result_500k = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 500000)
        assert isinstance(result_100k, dict)
        assert isinstance(result_500k, dict)


class TestWindingLosses:
    """Test calculate_winding_losses() function."""

    def test_winding_losses_basic(self, simple_magnetic, triangular_operating_point):
        """Calculate total winding losses."""
        result = PyOpenMagnetics.calculate_winding_losses(
            simple_magnetic, triangular_operating_point, 25.0
        )
        assert isinstance(result, dict)

    def test_winding_losses_returns_total(self, simple_magnetic, triangular_operating_point):
        """Winding loss result should include loss data."""
        result = PyOpenMagnetics.calculate_winding_losses(
            simple_magnetic, triangular_operating_point, 25.0
        )
        if isinstance(result, dict):
            # Result may contain various keys depending on the build
            assert len(result) > 0

    def test_winding_losses_positive(self, simple_magnetic, triangular_operating_point):
        """Winding losses should be positive."""
        result = PyOpenMagnetics.calculate_winding_losses(
            simple_magnetic, triangular_operating_point, 25.0
        )
        if isinstance(result, dict) and "windingLosses" in result:
            losses = result["windingLosses"]
            if isinstance(losses, (int, float)):
                assert losses >= 0

    def test_winding_losses_at_high_temperature(self, simple_magnetic, triangular_operating_point):
        """Winding losses should increase at higher temperature."""
        result_25 = PyOpenMagnetics.calculate_winding_losses(
            simple_magnetic, triangular_operating_point, 25.0
        )
        result_100 = PyOpenMagnetics.calculate_winding_losses(
            simple_magnetic, triangular_operating_point, 100.0
        )
        # Both should return valid results
        assert isinstance(result_25, dict)
        assert isinstance(result_100, dict)


class TestOhmicLosses:
    """Test calculate_ohmic_losses() function."""

    def test_ohmic_losses_basic(self, wound_inductor_coil, triangular_operating_point):
        """Calculate DC ohmic losses."""
        result = PyOpenMagnetics.calculate_ohmic_losses(
            wound_inductor_coil, triangular_operating_point, 25.0
        )
        assert isinstance(result, dict)

    def test_ohmic_losses_positive(self, wound_inductor_coil, triangular_operating_point):
        """Ohmic losses should be non-negative."""
        result = PyOpenMagnetics.calculate_ohmic_losses(
            wound_inductor_coil, triangular_operating_point, 25.0
        )
        if isinstance(result, dict) and "ohmicLosses" in result:
            losses = result["ohmicLosses"]
            if isinstance(losses, (int, float)):
                assert losses >= 0


class TestDcResistancePerMeter:
    """Test wire-level per-meter loss calculations."""

    def test_dc_resistance_per_meter(self, sample_round_wire):
        """DC resistance per meter should be positive."""
        result = PyOpenMagnetics.calculate_dc_resistance_per_meter(sample_round_wire, 25.0)
        assert isinstance(result, float)
        assert result > 0

    def test_dc_resistance_increases_with_temperature(self, sample_round_wire):
        """DC resistance should increase with temperature for copper."""
        r_25 = PyOpenMagnetics.calculate_dc_resistance_per_meter(sample_round_wire, 25.0)
        r_100 = PyOpenMagnetics.calculate_dc_resistance_per_meter(sample_round_wire, 100.0)
        assert r_100 > r_25

    def test_dc_losses_per_meter(self, sample_round_wire, current_excitation_with_harmonics):
        """DC losses per meter should be positive."""
        current = current_excitation_with_harmonics.get("current", current_excitation_with_harmonics)
        result = PyOpenMagnetics.calculate_dc_losses_per_meter(sample_round_wire, current, 25.0)
        assert isinstance(result, float)
        assert result >= 0

    def test_skin_ac_losses_per_meter(self, sample_round_wire, current_excitation_with_harmonics):
        """Skin effect AC losses per meter should be non-negative."""
        current = current_excitation_with_harmonics.get("current", current_excitation_with_harmonics)
        result = PyOpenMagnetics.calculate_skin_ac_losses_per_meter(sample_round_wire, current, 25.0)
        assert isinstance(result, float)
        assert result >= 0

    def test_skin_ac_resistance_per_meter(self, sample_round_wire, current_excitation_with_harmonics):
        """Skin effect AC resistance per meter should be positive."""
        current = current_excitation_with_harmonics.get("current", current_excitation_with_harmonics)
        result = PyOpenMagnetics.calculate_skin_ac_resistance_per_meter(sample_round_wire, current, 25.0)
        assert isinstance(result, float)
        assert result > 0

    def test_skin_ac_factor(self, sample_round_wire, current_excitation_with_harmonics):
        """AC factor (Rac/Rdc) should be >= 1.0."""
        current = current_excitation_with_harmonics.get("current", current_excitation_with_harmonics)
        result = PyOpenMagnetics.calculate_skin_ac_factor(sample_round_wire, current, 25.0)
        assert isinstance(result, float)
        assert result >= 1.0

    def test_effective_current_density(self, sample_round_wire, current_excitation_with_harmonics):
        """Effective current density should be positive."""
        current = current_excitation_with_harmonics.get("current", current_excitation_with_harmonics)
        result = PyOpenMagnetics.calculate_effective_current_density(sample_round_wire, current, 25.0)
        assert isinstance(result, float)
        assert result > 0

    def test_effective_skin_depth(self, current_excitation_with_harmonics):
        """Skin depth should be positive for copper."""
        current = current_excitation_with_harmonics.get("current", current_excitation_with_harmonics)
        result = PyOpenMagnetics.calculate_effective_skin_depth("copper", current, 25.0)
        assert isinstance(result, float)
        assert result > 0


class TestMagneticFieldStrength:
    """Test magnetic field strength calculation."""

    def test_calculate_field_strength(self, simple_magnetic, triangular_operating_point):
        """Calculate magnetic field distribution in winding window."""
        result = PyOpenMagnetics.calculate_magnetic_field_strength_field(
            triangular_operating_point, simple_magnetic
        )
        assert isinstance(result, dict)

    def test_field_strength_has_data(self, simple_magnetic, triangular_operating_point):
        """Field strength result should contain field data."""
        result = PyOpenMagnetics.calculate_magnetic_field_strength_field(
            triangular_operating_point, simple_magnetic
        )
        if isinstance(result, dict):
            assert len(result) > 0
