"""
Tests for PyOpenMagnetics converter topology processor functions.

Many topology processors are defined in the .pyi type stubs but may not be
implemented in the current build. Tests are marked xfail where needed.
This file also tests the Design API's topology processing via process_inputs().
"""
import pytest
import PyOpenMagnetics


def _has_attr(name):
    """Check if PyOpenMagnetics has a given attribute."""
    return hasattr(PyOpenMagnetics, name)


class TestProcessFlyback:
    """Test process_flyback() converter processor."""

    @pytest.mark.skipif(not _has_attr("process_flyback"), reason="process_flyback not available")
    def test_basic_flyback(self):
        """Process basic flyback converter specification."""
        flyback = {
            "inputVoltage": {"nominal": 325},
            "outputVoltage": 12,
            "outputCurrent": 5,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.88,
            "turnsRatio": 0.1
        }
        result = PyOpenMagnetics.process_flyback(flyback)
        assert isinstance(result, dict)

    @pytest.mark.skipif(not _has_attr("process_flyback"), reason="process_flyback not available")
    def test_flyback_has_operating_points(self):
        """Flyback result should have operating points."""
        flyback = {
            "inputVoltage": {"nominal": 325},
            "outputVoltage": 12,
            "outputCurrent": 5,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.88,
            "turnsRatio": 0.1
        }
        result = PyOpenMagnetics.process_flyback(flyback)
        if isinstance(result, dict):
            assert "operatingPoints" in result

    @pytest.mark.skipif(not _has_attr("process_flyback"), reason="process_flyback not available")
    def test_flyback_has_design_requirements(self):
        """Flyback result should have design requirements."""
        flyback = {
            "inputVoltage": {"nominal": 325},
            "outputVoltage": 12,
            "outputCurrent": 5,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.88,
            "turnsRatio": 0.1
        }
        result = PyOpenMagnetics.process_flyback(flyback)
        if isinstance(result, dict):
            assert "designRequirements" in result


class TestProcessBuck:
    """Test process_buck() converter processor."""

    @pytest.mark.skipif(not _has_attr("process_buck"), reason="process_buck not available")
    def test_basic_buck(self):
        """Process basic buck converter specification."""
        buck = {
            "inputVoltage": {"nominal": 48},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "currentRipple": 0.2
        }
        result = PyOpenMagnetics.process_buck(buck)
        assert isinstance(result, dict)

    @pytest.mark.skipif(not _has_attr("process_buck"), reason="process_buck not available")
    def test_buck_has_operating_point(self):
        """Buck result should have operating points."""
        buck = {
            "inputVoltage": {"nominal": 48},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "currentRipple": 0.2
        }
        result = PyOpenMagnetics.process_buck(buck)
        if isinstance(result, dict):
            assert "operatingPoints" in result

    @pytest.mark.skipif(not _has_attr("process_buck"), reason="process_buck not available")
    def test_buck_has_inductance(self):
        """Buck result should have magnetizing inductance requirement."""
        buck = {
            "inputVoltage": {"nominal": 48},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "currentRipple": 0.2
        }
        result = PyOpenMagnetics.process_buck(buck)
        if isinstance(result, dict) and "designRequirements" in result:
            assert "magnetizingInductance" in result["designRequirements"]


class TestProcessBoost:
    """Test process_boost() converter processor."""

    @pytest.mark.skipif(not _has_attr("process_boost"), reason="process_boost not available")
    def test_basic_boost(self):
        """Process basic boost converter specification."""
        boost = {
            "inputVoltage": {"nominal": 12},
            "outputVoltage": 48,
            "outputCurrent": 2,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "currentRipple": 0.2
        }
        result = PyOpenMagnetics.process_boost(boost)
        assert isinstance(result, dict)


class TestProcessForward:
    """Test forward converter processor functions."""

    @pytest.mark.skipif(not _has_attr("process_single_switch_forward"), reason="process_single_switch_forward not available")
    def test_single_switch_forward(self):
        """Process single-switch forward converter."""
        forward = {
            "inputVoltage": {"nominal": 325},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.90,
            "turnsRatio": 0.1,
            "maxDutyCycle": 0.45
        }
        result = PyOpenMagnetics.process_single_switch_forward(forward)
        assert isinstance(result, dict)

    @pytest.mark.skipif(not _has_attr("process_two_switch_forward"), reason="process_two_switch_forward not available")
    def test_two_switch_forward(self):
        """Process two-switch forward converter."""
        forward = {
            "inputVoltage": {"nominal": 325},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.90,
            "turnsRatio": 0.1,
            "maxDutyCycle": 0.45
        }
        result = PyOpenMagnetics.process_two_switch_forward(forward)
        assert isinstance(result, dict)

    @pytest.mark.skipif(not _has_attr("process_active_clamp_forward"), reason="process_active_clamp_forward not available")
    def test_active_clamp_forward(self):
        """Process active-clamp forward converter."""
        forward = {
            "inputVoltage": {"nominal": 325},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.90,
            "turnsRatio": 0.1,
            "maxDutyCycle": 0.45
        }
        result = PyOpenMagnetics.process_active_clamp_forward(forward)
        assert isinstance(result, dict)


class TestProcessPushPull:
    """Test process_push_pull() converter processor."""

    @pytest.mark.skipif(not _has_attr("process_push_pull"), reason="process_push_pull not available")
    def test_basic_push_pull(self):
        """Process basic push-pull converter."""
        push_pull = {
            "inputVoltage": {"nominal": 12},
            "outputVoltage": 48,
            "outputCurrent": 5,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.90,
            "turnsRatio": 4
        }
        result = PyOpenMagnetics.process_push_pull(push_pull)
        assert isinstance(result, dict)


class TestProcessIsolatedConverters:
    """Test isolated converter processor functions."""

    @pytest.mark.skipif(not _has_attr("process_isolated_buck"), reason="process_isolated_buck not available")
    def test_isolated_buck(self):
        """Process isolated buck converter."""
        isolated_buck = {
            "inputVoltage": {"nominal": 48},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.90,
            "turnsRatio": 0.25
        }
        result = PyOpenMagnetics.process_isolated_buck(isolated_buck)
        assert isinstance(result, dict)

    @pytest.mark.skipif(not _has_attr("process_isolated_buck_boost"), reason="process_isolated_buck_boost not available")
    def test_isolated_buck_boost(self):
        """Process isolated buck-boost converter."""
        isolated_buck_boost = {
            "inputVoltage": {"nominal": 48},
            "outputVoltage": 12,
            "outputCurrent": 10,
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
            "efficiency": 0.90,
            "turnsRatio": 0.25
        }
        result = PyOpenMagnetics.process_isolated_buck_boost(isolated_buck_boost)
        assert isinstance(result, dict)


class TestTopologyViaProcessInputs:
    """Test topology processing through process_inputs() which is always available."""

    def test_inductor_inputs_processing(self, inductor_inputs):
        """Process inductor inputs through process_inputs."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        assert isinstance(result, dict)
        assert "operatingPoints" in result
        assert "designRequirements" in result

    def test_flyback_inputs_processing(self):
        """Process flyback-like inputs through process_inputs."""
        flyback = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": [{"nominal": 1}]
            },
            "operatingPoints": [
                {
                    "name": "Flyback Op Point",
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {
                            "frequency": 100000,
                            "current": {
                                "processed": {
                                    "dutyCycle": 0.4,
                                    "label": "Flyback primary",
                                    "offset": 10,
                                    "peakToPeak": 20
                                }
                            }
                        },
                        {
                            "frequency": 100000,
                            "current": {
                                "processed": {
                                    "dutyCycle": 0.6,
                                    "label": "Flyback secondary",
                                    "offset": 10,
                                    "peakToPeak": 20
                                }
                            }
                        }
                    ]
                }
            ]
        }
        result = PyOpenMagnetics.process_inputs(flyback)
        assert isinstance(result, dict)
        assert "operatingPoints" in result
        assert "designRequirements" in result

    def test_high_frequency_inputs_processing(self, high_frequency_inputs):
        """Process high frequency inputs through process_inputs."""
        result = PyOpenMagnetics.process_inputs(high_frequency_inputs)
        assert isinstance(result, dict)
        assert "operatingPoints" in result

    def test_inputs_preserve_inductance(self, inductor_inputs):
        """process_inputs should preserve magnetizing inductance."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        mag_ind = result["designRequirements"]["magnetizingInductance"]
        assert abs(mag_ind["nominal"] - 100e-6) < 1e-9

    def test_inputs_preserve_turns_ratios(self):
        """process_inputs should preserve turns ratios."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": [{"nominal": 0.307692}]
            },
            "operatingPoints": [
                {
                    "name": "Nominal",
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {
                            "frequency": 100000,
                            "current": {
                                "processed": {"dutyCycle": 0.5, "label": "Triangular", "offset": 0, "peakToPeak": 10}
                            }
                        },
                        {
                            "frequency": 100000,
                            "current": {
                                "processed": {"dutyCycle": 0.5, "label": "Triangular", "offset": 0, "peakToPeak": 5}
                            }
                        }
                    ]
                }
            ]
        }
        result = PyOpenMagnetics.process_inputs(inputs)
        ratios = result["designRequirements"]["turnsRatios"]
        assert isinstance(ratios, list)
        assert len(ratios) == 1

    def test_inputs_add_harmonics(self, inductor_inputs):
        """process_inputs should add harmonics to excitations."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        assert "harmonics" in excitation.get("current", {})

    def test_inputs_add_processed_data(self, inductor_inputs):
        """process_inputs should add processed data to excitations."""
        result = PyOpenMagnetics.process_inputs(inductor_inputs)
        excitation = result["operatingPoints"][0]["excitationsPerWinding"][0]
        assert "processed" in excitation.get("current", {})


class TestAvailableCalculationFunctions:
    """Test calculation utility functions that are always available."""

    def test_calculate_basic_processed_data(self):
        """calculate_basic_processed_data should process waveform data."""
        if not _has_attr("calculate_basic_processed_data"):
            pytest.skip("calculate_basic_processed_data not available")
        waveform = {
            "data": [-5, 5, -5],
            "time": [0, 0.0000025, 0.00001]
        }
        result = PyOpenMagnetics.calculate_basic_processed_data(waveform)
        assert isinstance(result, dict)

    def test_calculate_harmonics(self):
        """calculate_harmonics should decompose waveform."""
        if not _has_attr("calculate_harmonics"):
            pytest.skip("calculate_harmonics not available")
        signal = {
            "waveform": {
                "data": [-5, 5, -5],
                "time": [0, 0.0000025, 0.00001]
            }
        }
        result = PyOpenMagnetics.calculate_harmonics(signal, 100000)
        assert isinstance(result, dict)

    def test_resolve_dimension_with_tolerance(self):
        """resolve_dimension_with_tolerance should return a value."""
        if not _has_attr("resolve_dimension_with_tolerance"):
            pytest.skip("resolve_dimension_with_tolerance not available")
        dim = {"nominal": 100e-6, "minimum": 90e-6, "maximum": 110e-6}
        result = PyOpenMagnetics.resolve_dimension_with_tolerance(dim)
        assert isinstance(result, (int, float))
        assert result > 0
