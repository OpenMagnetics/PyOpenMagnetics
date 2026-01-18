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
    """
    return {
        "designRequirements": {
            "magnetizingInductance": {"nominal": 100e-6},
            "turnsRatios": [{"nominal": 0.307692}]  # 24:78 ratio
        },
        "operatingPoints": [
            {
                "name": "Nominal",
                "conditions": {"ambientTemperature": 25},
                "excitationsPerWinding": [
                    {
                        "frequency": 100000,
                        "current": {
                            "processed": {
                                "dutyCycle": 0.5,
                                "label": "Triangular",
                                "offset": 0,
                                "peakToPeak": 10
                            }
                        }
                    }
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
