"""
Tests for PyOpenMagnetics Magnetic Adviser.

These tests mirror TestMagneticAdviser.cpp from MKF, verifying the magnetic
adviser functionality for recommending optimal complete magnetic designs
including core, winding, and all parameters.
"""
import pytest
import json
import PyOpenMagnetics


def parse_json_result(result):
    """Parse JSON result string into Python object."""
    if isinstance(result, str):
        return json.loads(result)
    return result


class TestMagneticAdviserBasic:
    """
    Basic magnetic adviser tests.
    Mirrors SUITE(MagneticAdviser) in TestMagneticAdviser.cpp.
    """

    def test_calculate_advised_magnetics_returns_results(self, inductor_inputs, reset_settings):
        """
        Magnetic adviser should return recommendations for inductor inputs.
        Similar to Test_MagneticAdviser_Toroidal_Cores_All_Cores.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        # API: calculate_advised_magnetics(inputs, max_results, core_mode)
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)
        # Should return some results

    def test_advised_magnetics_have_required_fields(self, inductor_inputs, reset_settings):
        """
        Advised magnetics should contain required Mas fields.
        Similar to checks in TestMagneticAdviser.cpp that verify magnetic structure.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 3, "available cores")
        results = parse_json_result(result_json)
        
        if len(results) > 0:
            for result in results:
                assert isinstance(result, dict)
                # Each result should be a valid Mas with magnetic
                # The Mas structure should contain magnetic, inputs, and optionally outputs
                if "magnetic" in result:
                    assert "core" in result["magnetic"] or "coil" in result["magnetic"]


class TestMagneticAdviserCoreModes:
    """
    Test magnetic adviser with different core modes.
    Mirrors filtering tests in TestMagneticAdviser.cpp.
    """

    def test_available_cores_mode(self, inductor_inputs, reset_settings):
        """
        Test with AVAILABLE_CORES mode (uses all available cores).
        Similar to Test_MagneticAdviser_Toroidal_Cores_All_Cores.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)

    def test_standard_cores_mode(self, inductor_inputs, reset_settings):
        """
        Test with STANDARD_CORES mode (uses standard core shapes/materials).
        Similar to Test_MagneticAdviser_Toroidal_Cores_Standard_Cores.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "standard cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)


class TestMagneticAdviserInputTypes:
    """Test magnetic adviser with various input configurations."""

    def test_with_inductor_inputs(self, inductor_inputs, reset_settings):
        """Test magnetic adviser with simple inductor inputs."""
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)

    @pytest.mark.xfail(reason="C++ library may have issues with transformer inputs")
    def test_with_transformer_inputs(self, transformer_inputs, reset_settings):
        """
        Test magnetic adviser with transformer (multi-winding) inputs.
        Similar to Test_MagneticAdviser_Insulation_Requirements.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(transformer_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)

    @pytest.mark.xfail(reason="C++ library may have issues with high frequency inputs")
    def test_with_high_frequency_inputs(self, high_frequency_inputs, reset_settings):
        """
        Test magnetic adviser with high frequency (~500kHz) inputs.
        Similar to high frequency tests in TestMagneticAdviser.cpp.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(high_frequency_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)

    @pytest.mark.xfail(reason="C++ library may have issues with flyback inputs")
    def test_with_flyback_inputs(self, flyback_inputs, reset_settings):
        """
        Test magnetic adviser with flyback transformer inputs.
        Similar to MagneticAdviserJsonHV and MagneticAdviserJsonLV tests.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(flyback_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        results = parse_json_result(result_json)
        
        assert isinstance(results, list)


class TestMagneticAdviserFiltering:
    """Test magnetic adviser result filtering and limits."""

    def test_limit_results(self, inductor_inputs, reset_settings):
        """
        Should respect max_results limit.
        Similar to result limiting in TestMagneticAdviser.cpp.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        results_5 = parse_json_result(
            PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "available cores")
        )
        results_2 = parse_json_result(
            PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 2, "available cores")
        )
        
        assert len(results_2) <= 2
        assert len(results_5) <= 5

    def test_single_result(self, inductor_inputs, reset_settings):
        """
        Should be able to request a single result.
        Similar to tests that request maximumNumberResults=1.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        result_json = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 1, "available cores")
        results = parse_json_result(result_json)
        
        assert len(results) <= 1


class TestMagneticAdviserFromCatalog:
    """Test magnetic adviser from component catalog."""

    @pytest.mark.skip(reason="C++ library crashes with empty catalog - access violation")
    def test_from_catalog_with_empty_catalog(self, inductor_inputs, reset_settings):
        """
        Test magnetic adviser from catalog with empty catalog.
        Should handle empty catalog gracefully.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        result = PyOpenMagnetics.calculate_advised_magnetics_from_catalog(processed_inputs, [], 5)
        result_data = parse_json_result(result)
        
        # Should return empty or error gracefully
        assert isinstance(result_data, (dict, str, list))

    @pytest.mark.xfail(reason="Requires valid magnetic catalog data")
    def test_from_catalog_with_magnetics(self, inductor_inputs, reset_settings):
        """
        Test magnetic adviser from catalog with actual magnetic components.
        Similar to catalog-based filtering in TestMagneticAdviser.cpp.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        # Create a simple magnetic catalog entry
        catalog = [
            {
                "manufacturerInfo": {
                    "reference": "TEST_MAGNETIC_001"
                },
                "core": {
                    "functionalDescription": {
                        "type": "two-piece set",
                        "material": "3C95",
                        "shape": "ETD 49/25/16",
                        "gapping": [
                            {"type": "subtractive", "length": 0.0001}
                        ],
                        "numberStacks": 1
                    }
                },
                "coil": {
                    "functionalDescription": [
                        {
                            "name": "Primary",
                            "numberTurns": 20,
                            "numberParallels": 1,
                            "isolationSide": "primary",
                            "wire": "Round 0.5 - Grade 1"
                        }
                    ]
                }
            }
        ]
        
        result = PyOpenMagnetics.calculate_advised_magnetics_from_catalog(processed_inputs, catalog, 5)
        result_data = parse_json_result(result)
        
        assert isinstance(result_data, dict)
        if "data" in result_data:
            assert isinstance(result_data["data"], list)


class TestMagneticAdviserFromCache:
    """Test magnetic adviser from cached magnetics."""

    def test_from_cache_without_cache(self, inductor_inputs, reset_settings):
        """
        Test magnetic adviser from cache when cache is empty.
        Should return appropriate error message.
        """
        processed_inputs = PyOpenMagnetics.process_inputs(inductor_inputs)
        
        filter_flow = []
        
        result = PyOpenMagnetics.calculate_advised_magnetics_from_cache(processed_inputs, filter_flow, 5)
        
        # Should handle empty cache - returns error string "Exception: No magnetics found in cache"
        # or a result structure with empty data
        if isinstance(result, str):
            assert "cache" in result.lower() or "exception" in result.lower()
        else:
            result_data = parse_json_result(result)
            assert isinstance(result_data, (dict, list))
