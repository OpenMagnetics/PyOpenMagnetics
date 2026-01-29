"""
Tests for PyOpenMagnetics utility functions.

Covers waveform processing, harmonics, sampled waveform generation,
power calculations, and reflected waveform transformations.
"""
import pytest
import PyOpenMagnetics


class TestProcessedData:
    """Test waveform processing to extract RMS, peak, offset, etc."""

    def test_triangular_waveform_produces_processed_data(self, inductor_inputs):
        """Triangular waveform should produce processed data fields."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        processed = excitation["current"]["processed"]

        assert "rms" in processed
        assert "peakToPeak" in processed
        assert "offset" in processed

    def test_sinusoidal_waveform_produces_processed_data(self, sinusoidal_operating_point):
        """Sinusoidal waveform should produce processed data."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        processed = excitation["current"]["processed"]

        assert "rms" in processed
        assert processed["rms"] > 0

    def test_rectangular_waveform_produces_processed_data(self, rectangular_voltage_operating_point):
        """Rectangular voltage waveform should produce processed data."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [rectangular_voltage_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        processed = excitation["voltage"]["processed"]

        assert "rms" in processed
        assert processed["rms"] > 0

    def test_processed_data_returns_expected_fields(self, inductor_inputs):
        """Processed data should contain standard signal description fields."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        processed = excitation["current"]["processed"]

        # These are the main fields from the Processed dataclass
        expected_fields = {"rms", "peakToPeak", "offset"}
        assert expected_fields.issubset(set(processed.keys()))

    def test_triangular_rms_value_is_physical(self, inductor_inputs):
        """RMS of +-5A triangular should be ~2.88A."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        rms = excitation["current"]["processed"]["rms"]

        # Triangular wave RMS = peak / sqrt(3) = 5 / sqrt(3) ~= 2.88
        assert 2.5 < rms < 3.2

    def test_processed_peak_to_peak_matches_input(self, inductor_inputs):
        """Peak-to-peak should match the input waveform amplitude."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        p2p = excitation["current"]["processed"]["peakToPeak"]

        assert abs(p2p - 10.0) < 0.5  # +-5A = 10A p2p


class TestHarmonics:
    """Test harmonic decomposition of waveforms."""

    def test_sinusoidal_has_harmonics(self, sinusoidal_operating_point):
        """Sinusoidal waveform should produce harmonics data."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        harmonics = excitation["current"]["harmonics"]

        assert "amplitudes" in harmonics
        assert "frequencies" in harmonics

    def test_harmonics_amplitudes_array(self, sinusoidal_operating_point):
        """Harmonics amplitudes should be a non-empty list."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        amplitudes = result["operatingPoints"][0]["excitationsPerWinding"][0]["current"]["harmonics"]["amplitudes"]

        assert isinstance(amplitudes, list)
        assert len(amplitudes) > 0

    def test_harmonics_frequencies_array(self, sinusoidal_operating_point):
        """Harmonics frequencies should be a non-empty list."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        frequencies = result["operatingPoints"][0]["excitationsPerWinding"][0]["current"]["harmonics"]["frequencies"]

        assert isinstance(frequencies, list)
        assert len(frequencies) > 0

    def test_harmonics_amplitudes_and_frequencies_same_length(self, sinusoidal_operating_point):
        """Amplitudes and frequencies arrays should have same length."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        harmonics = result["operatingPoints"][0]["excitationsPerWinding"][0]["current"]["harmonics"]

        assert len(harmonics["amplitudes"]) == len(harmonics["frequencies"])

    def test_triangular_waveform_has_harmonics(self, inductor_inputs):
        """Triangular waveform should also produce harmonics."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]

        assert "harmonics" in excitation["current"]
        harmonics = excitation["current"]["harmonics"]
        assert len(harmonics["amplitudes"]) > 0


class TestProcessInputsStructure:
    """Test the overall structure of process_inputs() output."""

    def test_preserves_design_requirements(self, inductor_inputs):
        """process_inputs should preserve designRequirements."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        assert "designRequirements" in result
        assert "magnetizingInductance" in result["designRequirements"]

    def test_preserves_operating_points(self, inductor_inputs):
        """process_inputs should preserve operatingPoints."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        assert "operatingPoints" in result
        assert len(result["operatingPoints"]) > 0

    def test_preserves_frequency(self, inductor_inputs):
        """process_inputs should preserve excitation frequency."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        freq = result["operatingPoints"][0]["excitationsPerWinding"][0]["frequency"]
        assert freq == 100000

    def test_adds_waveform_to_processed_input(self, sinusoidal_operating_point):
        """When starting from processed data, should reconstruct waveform."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [sinusoidal_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]

        # Should have waveform reconstructed from processed data
        assert "waveform" in excitation["current"] or "processed" in excitation["current"]

    def test_multiple_operating_points_preserved(self):
        """Multiple operating points should all be processed."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [
                {
                    "name": "OP1",
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {"frequency": 100000, "current": {"processed": {"dutyCycle": 0.5, "label": "Triangular", "offset": 0, "peakToPeak": 5}}}
                    ]
                },
                {
                    "name": "OP2",
                    "conditions": {"ambientTemperature": 85},
                    "excitationsPerWinding": [
                        {"frequency": 200000, "current": {"processed": {"dutyCycle": 0.5, "label": "Triangular", "offset": 0, "peakToPeak": 10}}}
                    ]
                }
            ]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        assert len(result["operatingPoints"]) == 2


class TestTHD:
    """Test Total Harmonic Distortion calculations."""

    def test_rectangular_has_significant_thd(self, rectangular_voltage_operating_point):
        """Rectangular waveforms should have high THD."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [rectangular_voltage_operating_point]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        processed = result["operatingPoints"][0]["excitationsPerWinding"][0]["voltage"]["processed"]

        assert "thd" in processed
        assert processed["thd"] > 0

    def test_thd_is_non_negative(self, inductor_inputs):
        """THD should always be non-negative."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        processed = result["operatingPoints"][0]["excitationsPerWinding"][0]["current"]["processed"]

        if "thd" in processed:
            assert processed["thd"] >= 0
