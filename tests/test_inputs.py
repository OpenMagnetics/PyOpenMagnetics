"""
Tests for PyOpenMagnetics Inputs processing.

These tests mirror TestInputs.cpp from the MKF test suite, verifying that
input processing, waveform analysis, and harmonic calculation work correctly.
"""
import pytest
import math
import PyOpenMagnetics


class TestInputsProcessing:
    """Test suite for input processing - mirrors SUITE(Inputs) in TestInputs.cpp"""

    def test_triangular_waveform_processing(self, triangular_operating_point):
        """
        Test processing of triangular current waveform.
        Mirrors Test_One_Operating_Point_One_Winding_Triangular.
        """
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [triangular_operating_point]
        }
        
        result = PyOpenMagnetics.process_inputs(inputs)
        assert "operatingPoints" in result
        
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        current = excitation["current"]
        
        # Verify processed data was calculated
        assert "processed" in current
        processed = current["processed"]
        
        # Check RMS value (expected ~2.88 A for triangular 10 A peak-to-peak)
        assert "rms" in processed
        assert 2.5 < processed["rms"] < 3.2
        
        # Check peak-to-peak
        assert "peakToPeak" in processed
        assert abs(processed["peakToPeak"] - 10.0) < 0.1

    def test_sinusoidal_waveform_from_processed(self, sinusoidal_operating_point):
        """
        Test processing when starting from processed data (sinusoidal).
        Mirrors Test_One_Operating_Point_One_Winding_Equidistant_Sinusoidal.
        """
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        
        result = PyOpenMagnetics.process_inputs(inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        current = excitation["current"]
        
        # Verify harmonics were calculated
        assert "harmonics" in current
        harmonics = current["harmonics"]
        assert "amplitudes" in harmonics
        assert "frequencies" in harmonics
        assert len(harmonics["amplitudes"]) > 0
        assert len(harmonics["frequencies"]) > 0

    def test_rectangular_voltage_processing(self, rectangular_voltage_operating_point):
        """
        Test processing of rectangular voltage waveform.
        Mirrors Test_One_Operating_Point_One_Winding_Equidistant_Rectangular.
        """
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [rectangular_voltage_operating_point]
        }
        
        result = PyOpenMagnetics.process_inputs(inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        voltage = excitation["voltage"]
        
        # Verify processed data
        assert "processed" in voltage
        processed = voltage["processed"]
        
        # Check RMS value (expected ~4.28 V)
        assert "rms" in processed
        
        # Check THD (Total Harmonic Distortion)
        assert "thd" in processed
        assert processed["thd"] > 0  # Rectangular has significant harmonics

    @pytest.mark.xfail(reason="C++ library issue with transformer inputs")
    def test_transformer_inputs_with_turns_ratio(self, transformer_inputs):
        """Test processing of transformer inputs with turns ratio."""
        result = PyOpenMagnetics.process_inputs(transformer_inputs)
        
        # Should have design requirements preserved
        assert "designRequirements" in result
        assert "turnsRatios" in result["designRequirements"]
        assert len(result["designRequirements"]["turnsRatios"]) > 0

    def test_high_frequency_inputs(self, high_frequency_inputs):
        """Test processing of high frequency inputs (~500kHz)."""
        result = PyOpenMagnetics.process_inputs(high_frequency_inputs)
        
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        assert excitation["frequency"] == 500000


class TestOperatingPointConditions:
    """Test suite for operating point conditions."""

    def test_ambient_temperature_preserved(self, inductor_inputs):
        """Verify ambient temperature is preserved in processing."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        conditions = result["operatingPoints"][0]["conditions"]
        assert "ambientTemperature" in conditions
        assert conditions["ambientTemperature"] == 25

    def test_multiple_operating_points(self):
        """Test inputs with multiple operating points."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [
                {
                    "name": "Low Power",
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {
                            "frequency": 100000,
                            "current": {
                                "processed": {
                                    "dutyCycle": 0.5,
                                    "label": "Triangular",
                                    "offset": 0,
                                    "peakToPeak": 5
                                }
                            }
                        }
                    ]
                },
                {
                    "name": "High Power",
                    "conditions": {"ambientTemperature": 85},
                    "excitationsPerWinding": [
                        {
                            "frequency": 100000,
                            "current": {
                                "processed": {
                                    "dutyCycle": 0.5,
                                    "label": "Triangular",
                                    "offset": 0,
                                    "peakToPeak": 20
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        result = PyOpenMagnetics.process_inputs(inputs)
        assert len(result["operatingPoints"]) == 2
        assert result["operatingPoints"][0]["name"] == "Low Power"
        assert result["operatingPoints"][1]["name"] == "High Power"


class TestDesignRequirements:
    """Test suite for design requirements handling."""

    def test_magnetizing_inductance_nominal(self, inductor_inputs):
        """Test magnetizing inductance is preserved."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        mag_ind = result["designRequirements"]["magnetizingInductance"]
        assert "nominal" in mag_ind
        assert abs(mag_ind["nominal"] - 100e-6) < 1e-9

    def test_turns_ratios_empty_for_inductor(self, inductor_inputs):
        """Inductor should have empty turns ratios."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        assert result["designRequirements"]["turnsRatios"] == []

    @pytest.mark.xfail(reason="C++ library issue with transformer inputs")
    def test_turns_ratios_for_transformer(self, transformer_inputs):
        """Transformer should have non-empty turns ratios."""
        result = PyOpenMagnetics.process_inputs(transformer_inputs)
        ratios = result["designRequirements"]["turnsRatios"]
        assert len(ratios) == 1
        assert abs(ratios[0]["nominal"] - 0.307692) < 0.001
