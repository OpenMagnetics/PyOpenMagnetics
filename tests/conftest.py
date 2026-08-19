"""
Pytest configuration and shared fixtures for PyOpenMagnetics tests.

These fixtures mirror the patterns used in MKF C++ tests, providing
common test data structures for inputs, operating points, and cores.
"""
import pytest
import json
import PyOpenMagnetics


# ============================================================================
# Sample Operating Points (from MKF tests)
# ============================================================================

@pytest.fixture
def triangular_operating_point():
    """
    Operating point with triangular current waveform.
    Similar to Test_One_Operating_Point_One_Winding_Triangular in TestInputs.cpp
    """
    return {
        "name": "Nominal",
        "conditions": {
            "ambientTemperature": 25
        },
        "excitationsPerWinding": [
            {
                "frequency": 100000,
                "current": {
                    "waveform": {
                        "data": [-5, 5, -5],
                        "time": [0, 0.0000025, 0.00001]
                    }
                }
            }
        ]
    }


@pytest.fixture
def sinusoidal_operating_point():
    """Operating point with sinusoidal waveform using processed data."""
    return {
        "name": "Sinusoidal",
        "conditions": {
            "ambientTemperature": 25
        },
        "excitationsPerWinding": [
            {
                "frequency": 100000,
                "current": {
                    "processed": {
                        "dutyCycle": 0.5,
                        "label": "Sinusoidal",
                        "offset": 0,
                        "peakToPeak": 10
                    }
                }
            }
        ]
    }


@pytest.fixture
def rectangular_voltage_operating_point():
    """Operating point with rectangular voltage waveform."""
    return {
        "name": "Rectangular",
        "conditions": {
            "ambientTemperature": 42
        },
        "excitationsPerWinding": [
            {
                "frequency": 100000,
                "voltage": {
                    "waveform": {
                        "data": [-2.5, 7.5, 7.5, -2.5, -2.5],
                        "time": [0, 0, 0.0000025, 0.0000025, 0.00001]
                    }
                }
            }
        ]
    }


# ============================================================================
# Sample Inputs (from MKF tests)
# ============================================================================

@pytest.fixture
def inductor_inputs(triangular_operating_point):
    """
    Basic inductor inputs similar to those in TestMagneticAdviser.cpp.
    Magnetizing inductance: 100µH, frequency: 100kHz
    """
    return {
        "designRequirements": {
            "magnetizingInductance": {"nominal": 100e-6},
            "turnsRatios": []
        },
        "operatingPoints": [triangular_operating_point]
    }


@pytest.fixture
def transformer_inputs():
    """
    Basic transformer inputs with turns ratio.
    Similar to examples in TestCoreAdviser.cpp

    Two windings, because that is what one turns ratio means. This fixture used to
    declare turnsRatios and then supply a single winding excitation carrying a current
    and no voltage; the engine tried to reflect the missing winding off the primary
    voltage, found an empty optional and dereferenced it, and four tests across three
    files were marked xfail("C++ library issue with transformer inputs") to live with
    it (ABT #825 — the engine should name the operating point, the winding and the
    field instead of answering "bad optional access", but the input was wrong too).

    Both windings carry a voltage as well as a current. The core adviser sizes a core
    from the flux the voltage produces, and without one it dereferenced an empty
    optional too (also ABT #825) — a current-only excitation does not describe an
    operating point anything can be sized for.

    Everything follows from the ratio Np/Ns = 0.307692 (24:78, a step-up):
    Ip*Np = Is*Ns gives 10 A pk-pk primary -> 3.07692 A pk-pk secondary, and
    Vs/Vp = Ns/Np gives 100 V pk-pk primary -> 325 V pk-pk secondary.
    """
    turns_ratio = 0.307692  # Np/Ns, i.e. 24:78
    primary_current_peak_to_peak = 10
    primary_voltage_peak_to_peak = 100

    def winding(current_peak_to_peak, voltage_peak_to_peak):
        return {
            "frequency": 100000,
            "current": {
                "processed": {
                    "dutyCycle": 0.5,
                    "label": "Triangular",
                    "offset": 0,
                    "peakToPeak": current_peak_to_peak
                }
            },
            "voltage": {
                "processed": {
                    "dutyCycle": 0.5,
                    "label": "Rectangular",
                    "offset": 0,
                    "peakToPeak": voltage_peak_to_peak
                }
            }
        }

    return {
        "designRequirements": {
            "magnetizingInductance": {"nominal": 100e-6},
            "turnsRatios": [{"nominal": turns_ratio}]
        },
        "operatingPoints": [
            {
                "name": "Nominal",
                "conditions": {"ambientTemperature": 25},
                "excitationsPerWinding": [
                    winding(primary_current_peak_to_peak,
                            primary_voltage_peak_to_peak),
                    winding(primary_current_peak_to_peak * turns_ratio,
                            primary_voltage_peak_to_peak / turns_ratio)
                ]
            }
        ]
    }


@pytest.fixture
def high_frequency_inputs():
    """High frequency inputs for filter applications (~500kHz)."""
    return {
        "designRequirements": {
            "magnetizingInductance": {"nominal": 10e-6},
            "turnsRatios": []
        },
        "operatingPoints": [
            {
                "name": "High Frequency",
                "conditions": {"ambientTemperature": 25},
                "excitationsPerWinding": [
                    {
                        "frequency": 500000,
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
            }
        ]
    }


@pytest.fixture
def flyback_inputs():
    """
    Flyback transformer inputs based on simple_flyback.json test data.
    Two windings with 1:1 turns ratio.
    """
    return {
        "designRequirements": {
            "magnetizingInductance": {"nominal": 100e-6},
            "turnsRatios": [{"nominal": 1}]
        },
        "operatingPoints": [
            {
                "name": "Flyback Op Point",
                "conditions": {"ambientTemperature": 100},
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
                    }
                ]
            }
        ]
    }


# ============================================================================
# Sample Core Data
# ============================================================================

@pytest.fixture
def sample_core_data():
    """
    Sample core configuration for an ETD 49 with 3C95 material.
    Based on patterns from TestCore.cpp and TestCoreAdviser.cpp.
    """
    return {
        "functionalDescription": {
            "type": "two-piece set",
            "material": "3C95",
            "shape": "ETD 49/25/16",
            "gapping": [
                {"type": "subtractive", "length": 0.0001},
                {"type": "residual", "length": 0.000005},
                {"type": "residual", "length": 0.000005}
            ],
            "numberStacks": 1
        }
    }


@pytest.fixture
def sample_toroidal_core():
    """Toroidal core configuration for filter applications."""
    return {
        "functionalDescription": {
            "type": "toroidal",
            "material": "3C90",
            "shape": "R 25.3/14.8/10",
            "gapping": [],
            "numberStacks": 1
        }
    }


# ============================================================================
# Sample Winding Data
# ============================================================================

@pytest.fixture
def simple_winding():
    """Simple single winding configuration."""
    return [
        {
            "name": "Primary",
            "numberTurns": 31,
            "numberParallels": 1,
            "isolationSide": "primary",
            "wire": "Round 0.5 - Grade 1"
        }
    ]


@pytest.fixture
def transformer_windings():
    """Transformer with primary and secondary windings."""
    return [
        {
            "name": "Primary",
            "numberTurns": 24,
            "numberParallels": 1,
            "isolationSide": "primary",
            "wire": "Round 0.5 - Grade 1"
        },
        {
            "name": "Secondary",
            "numberTurns": 78,
            "numberParallels": 1,
            "isolationSide": "secondary",
            "wire": "Round 0.3 - Grade 1"
        }
    ]


# ============================================================================
# Core Adviser Weights
# ============================================================================

@pytest.fixture
def balanced_weights():
    """Balanced weights for core adviser."""
    return {
        "COST": 1,
        "EFFICIENCY": 1,
        "DIMENSIONS": 1
    }


@pytest.fixture
def efficiency_weights():
    """Efficiency-focused weights for core adviser."""
    return {
        "COST": 0,
        "EFFICIENCY": 1,
        "DIMENSIONS": 0
    }


# ============================================================================
# Utility Functions
# ============================================================================

@pytest.fixture
def reset_settings():
    """Reset PyOpenMagnetics settings before and after test."""
    PyOpenMagnetics.reset_settings()
    yield
    PyOpenMagnetics.reset_settings()
