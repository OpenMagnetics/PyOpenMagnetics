"""Tests for converter topology endpoints."""
import json
import PyOpenMagnetics as PyMKF


def test_process_flyback():
    """Test Flyback converter processing."""
    flyback = {
        "inputVoltage": {"minimum": 150, "maximum": 150},
        "desiredInductance": 400e-6,
        "desiredTurnsRatios": [6.14],
        "desiredDutyCycle": [[0.45, 0.45]],
        "maximumDutyCycle": 0.5,
        "efficiency": 0.9,
        "diodeVoltageDrop": 0.7,
        "operatingPoints": [{
            "outputVoltages": [20.0],
            "outputCurrents": [1.5],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }
    
    # Test with ngspice (default)
    result = PyMKF.process_converter("flyback", flyback, use_ngspice=True)
    assert "error" not in result, f"Error: {result.get('error')}"
    assert "designRequirements" in result
    assert "operatingPoints" in result
    print("✓ Flyback converter processed successfully")


def test_process_buck():
    """Test Buck converter processing."""
    buck = {
        "inputVoltage": {"minimum": 12, "maximum": 12},
        "desiredInductance": 10e-6,
        "diodeVoltageDrop": 0.7,
        "operatingPoints": [{
            "outputVoltages": [5.0],
            "outputCurrents": [2.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    result = PyMKF.process_converter("buck", buck, use_ngspice=False)  # Use analytical for speed
    assert "error" not in result, f"Error: {result.get('error')}"
    assert "designRequirements" in result
    assert "operatingPoints" in result
    print("✓ Buck converter processed successfully")


def test_process_boost():
    """Test Boost converter processing."""
    boost = {
        "inputVoltage": {"minimum": 5, "maximum": 5},
        "desiredInductance": 10e-6,
        "diodeVoltageDrop": 0.7,
        "operatingPoints": [{
            "outputVoltages": [12.0],
            "outputCurrents": [1.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    result = PyMKF.process_converter("boost", boost, use_ngspice=False)
    assert "error" not in result, f"Error: {result.get('error')}"
    assert "designRequirements" in result
    assert "operatingPoints" in result
    print("✓ Boost converter processed successfully")


def test_design_magnetics_from_flyback():
    """Test full magnetic design from Flyback converter."""
    flyback = {
        "inputVoltage": {"minimum": 150, "maximum": 150},
        "desiredInductance": 400e-6,
        "desiredTurnsRatios": [6.14],
        "desiredDutyCycle": [[0.45, 0.45]],
        "maximumDutyCycle": 0.5,
        "efficiency": 0.9,
        "diodeVoltageDrop": 0.7,
        "operatingPoints": [{
            "outputVoltages": [20.0],
            "outputCurrents": [1.5],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }
    
    # Design with analytical waveforms (faster)
    # Note: This test is skipped in CI as magnetic adviser can take a long time
    print("✓ Magnetic design test skipped (too slow for unit test)")
    print("  Use design_magnetics_from_converter() for full magnetic design")


def test_per_topology_wrappers():
    """Test per-topology wrapper functions."""

    # Test process_flyback wrapper
    flyback = {
        "inputVoltage": {"minimum": 100, "maximum": 100},
        "desiredInductance": 1e-3,
        "desiredTurnsRatios": [10.0],
        "desiredDutyCycle": [[0.45]],
        "maximumDutyCycle": 0.5,
        "diodeVoltageDrop": 0.7,
        "efficiency": 0.9,
        "operatingPoints": [{
            "outputVoltages": [10.0],
            "outputCurrents": [1.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    result = PyMKF.process_flyback(flyback)
    assert "error" not in result
    print("✓ process_flyback wrapper works")

    # Test process_buck wrapper
    buck = {
        "inputVoltage": {"minimum": 12, "maximum": 12},
        "desiredInductance": 10e-6,
        "diodeVoltageDrop": 0.7,
        "currentRippleRatio": 0.3,
        "operatingPoints": [{
            "outputVoltages": [5.0],
            "outputCurrents": [2.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    result = PyMKF.process_buck(buck)
    assert "error" not in result, f"Error: {result.get('error')}"
    print("✓ process_buck wrapper works")


def test_invalid_topology():
    """An unknown topology is refused, and the error names the topology it refused.

    The spec has to describe a real converter for this to test anything. The engine
    validates the requirements before it dispatches on the topology (Kirchhoff's
    validate_requirements runs at the top of build_tas_for, ahead of the tas_builders
    lookup), so a degenerate payload never reaches the topology switch at all. This
    test used to pass {"some": "data"} and assert "unknown topology", a message the
    engine cannot produce for that input — it answers "spec: designRequirements
    missing" — so the test had been red on main and was pinning an unreachable branch
    (ABT #824). The assertion was right; the payload was the problem.
    """
    import pytest
    converter = {
        "inputVoltage": {"minimum": 12, "maximum": 12},
        "desiredInductance": 10e-6,
        "diodeVoltageDrop": 0.7,
        "currentRippleRatio": 0.3,
        "operatingPoints": [{
            "outputVoltages": [5.0],
            "outputCurrents": [2.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25,
        }],
    }

    with pytest.raises(PyMKF.EngineError, match="[Uu]nknown topology"):
        PyMKF.process_converter("invalid_topology", converter)

    # An error that does not say WHICH topology it rejected cannot be acted on.
    with pytest.raises(PyMKF.EngineError, match="invalid_topology"):
        PyMKF.process_converter("invalid_topology", converter)
    print("✓ Invalid topology raises EngineError naming the topology")


def test_spec_is_validated_before_the_topology():
    """A payload describing no converter is refused for the spec, not the topology.

    Pins the ordering test_invalid_topology depends on (ABT #824): requirements are
    validated first, so a caller with a broken spec hears about the spec even when the
    topology is wrong too. Without this pinned, the obvious way to "fix" a red
    test_invalid_topology is to widen its regex until it accepts either message — which
    would quietly stop testing the topology switch, the one thing that test is named for.
    """
    import pytest
    with pytest.raises(PyMKF.EngineError, match="designRequirements"):
        PyMKF.process_converter("buck", {"some": "data"})
    print("✓ A spec that describes no converter is refused for the spec")


def test_llc_converter():
    """Test LLC resonant converter."""
    llc = {
        "inputVoltage": {"minimum": 400, "maximum": 400},
        "desiredInductance": 100e-6,
        "desiredTurnsRatios": [1.0],
        "minSwitchingFrequency": 80000,
        "maxSwitchingFrequency": 120000,
        "operatingPoints": [{
            "outputVoltages": [48.0],
            "outputCurrents": [5.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    result = PyMKF.process_converter("llc", llc, use_ngspice=False)
    assert "error" not in result, f"Error: {result.get('error')}"
    assert "designRequirements" in result
    print("✓ LLC converter processed successfully")


def test_forward_converters():
    """Test Forward converter variants."""
    # Single switch forward: turns ratios must have one more position than outputs for demagnetization winding
    single_switch_forward = {
        "inputVoltage": {"minimum": 48, "maximum": 48},
        "desiredInductance": 1e-3,
        # [demagnetization, output]. The output ratio must keep duty below 0.5:
        # n < Vin/(2*(Vout+Vd)) = 48/(2*12.7) ~ 1.89 for a single-switch forward.
        "desiredTurnsRatios": [1.0, 1.5],
        "diodeVoltageDrop": 0.7,
        "currentRippleRatio": 0.2,
        "operatingPoints": [{
            "outputVoltages": [12.0],
            "outputCurrents": [5.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    # Single switch forward
    result = PyMKF.process_converter("single_switch_forward", single_switch_forward, use_ngspice=False)
    assert "error" not in result, f"Error: {result.get('error')}"
    print("✓ Single-switch forward processed successfully")

    # Two switch forward and Active clamp forward: turns ratios must have same positions as outputs
    other_forward = {
        "inputVoltage": {"minimum": 48, "maximum": 48},
        "desiredInductance": 1e-3,
        "desiredTurnsRatios": [1.5],  # Same as number of outputs; keeps duty < 0.5
        "diodeVoltageDrop": 0.7,
        "currentRippleRatio": 0.2,
        "operatingPoints": [{
            "outputVoltages": [12.0],
            "outputCurrents": [5.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }

    # Two switch forward
    result = PyMKF.process_converter("two_switch_forward", other_forward, use_ngspice=False)
    assert "error" not in result, f"Error: {result.get('error')}"
    print("✓ Two-switch forward processed successfully")

    # Active clamp forward
    result = PyMKF.process_converter("active_clamp_forward", other_forward, use_ngspice=False)
    assert "error" not in result, f"Error: {result.get('error')}"
    print("✓ Active clamp forward processed successfully")


if __name__ == "__main__":
    print("Running converter topology tests...\n")
    
    test_process_flyback()
    test_process_buck()
    test_process_boost()
    test_llc_converter()
    test_forward_converters()
    test_per_topology_wrappers()
    test_invalid_topology()
    
    print("\n--- Full Design Flow Test ---")
    test_design_magnetics_from_flyback()
    
    print("\n✓ All tests passed!")
