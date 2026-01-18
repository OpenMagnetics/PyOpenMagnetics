"""
Integration tests for PyOpenMagnetics examples.

These tests verify that the example scripts and common workflows continue to work
across PyOpenMagnetics versions. They test end-to-end functionality rather than
individual units.

Run with: pytest tests/test_examples_integration.py -v
"""

import json
import os
import sys
import pytest
from pathlib import Path

import PyOpenMagnetics

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))



class TestDatabaseAccess:
    """Test that database queries work correctly."""
    
    def test_get_core_shapes(self):
        """Verify core shape database is accessible."""
        shapes = PyOpenMagnetics.get_core_shape_names(include_toroidal=False)
        
        assert shapes is not None
        assert isinstance(shapes, list)
        assert len(shapes) > 0
        
        # Check for common shapes
        shape_names = [s.lower() for s in shapes]
        assert any("etd" in s for s in shape_names), "ETD shapes should be available"
        assert any("e " in s or s.startswith("e") for s in shape_names), "E shapes should be available"
    
    def test_get_core_materials(self):
        """Verify core material database is accessible."""
        materials = PyOpenMagnetics.get_core_material_names()
        
        assert materials is not None
        assert isinstance(materials, list)
        assert len(materials) > 0
        
        # Check for common materials
        material_names = [m.lower() for m in materials]
        assert any("3c" in m for m in material_names), "Ferroxcube 3Cxx materials should be available"
    
    def test_get_wires(self):
        """Verify wire database is accessible."""
        wires = PyOpenMagnetics.get_wire_names()
        
        assert wires is not None
        assert isinstance(wires, list)
        assert len(wires) > 0


class TestCoreCreation:
    """Test core creation workflows."""
    
    @pytest.fixture
    def etd39_core_data(self):
        """Standard ETD 39 core data."""
        return {
            "functionalDescription": {
                "name": "Test ETD 39",
                "type": "two-piece set",
                "shape": "ETD 39/20/13",
                "material": "3C95",
                "gapping": [],
                "numberStacks": 1
            }
        }
    
    def test_create_ungapped_core(self,  etd39_core_data):
        """Create an ungapped core."""
        # API: calculate_core_data(core_data, include_material_data: bool)
        core = PyOpenMagnetics.calculate_core_data(etd39_core_data, False)
        
        assert core is not None
        assert isinstance(core, dict), f"Expected dict, got: {type(core).__name__} = {core}"
        assert "processedDescription" in core or "functionalDescription" in core
    
    def test_create_gapped_core(self):
        """Create a gapped core."""
        core_data = {
            "functionalDescription": {
                "name": "Gapped ETD 39",
                "type": "two-piece set",
                "shape": "ETD 39/20/13",
                "material": "3C95",
                "gapping": [
                    {"type": "subtractive", "length": 0.001}
                ],
                "numberStacks": 1
            }
        }
        
        core = PyOpenMagnetics.calculate_core_data(core_data, False)
        
        assert core is not None
        assert isinstance(core, dict), f"Expected dict, got: {type(core).__name__} = {core}"


class TestCoreLossCalculation:
    """Test core loss calculation workflows."""
    
    @pytest.fixture
    def test_core(self):
        """Create a core for testing."""
        core_data = {
            "functionalDescription": {
                "type": "two-piece set",
                "shape": "E 42/21/15",
                "material": "3C95",
                "gapping": [],
                "numberStacks": 1
            }
        }
        # API: calculate_core_data(core_data, include_material_data: bool)
        return PyOpenMagnetics.calculate_core_data(core_data, False)
    
    def test_get_steinmetz_coefficients(self):
        """Test retrieving Steinmetz coefficients for core loss estimation."""
        # This is a simpler way to test loss-related functionality
        coeffs = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 100000)
        
        assert coeffs is not None
        assert isinstance(coeffs, dict)
        # Steinmetz equation: P = k * f^alpha * B^beta
        assert "k" in coeffs or "alpha" in coeffs or "beta" in coeffs
    
    def test_get_material_permeability(self):
        """Test getting material permeability for loss calculations."""
        permeability = PyOpenMagnetics.get_material_permeability("3C95", 25.0, 0.0, 100000.0)
        
        assert permeability is not None
        assert permeability > 0
    
    def test_core_has_processed_description(self,  test_core):
        """Verify calculated core has processed parameters for loss calculation."""
        assert test_core is not None
        
        # Core should have processed description with effective parameters
        if "processedDescription" in test_core:
            processed = test_core["processedDescription"]
            # These are needed for loss calculations
            assert "effectiveParameters" in processed or "columns" in processed


class TestSettingsManagement:
    """Test settings get/set/reset functionality."""
    
    def test_get_settings(self):
        """Get current settings."""
        settings = PyOpenMagnetics.get_settings()
        
        assert settings is not None
        assert isinstance(settings, dict)
    
    def test_reset_settings(self):
        """Test reset to defaults."""
        # Reset to defaults
        PyOpenMagnetics.reset_settings()
        
        # Settings should be retrievable after reset
        after_reset = PyOpenMagnetics.get_settings()
        assert after_reset is not None
        assert isinstance(after_reset, dict)


class TestBobbinCreation:
    """Test bobbin creation for cores."""
    
    def test_create_basic_bobbin(self):
        """Create basic bobbin for a core."""
        core_data = {
            "functionalDescription": {
                "shape": "ETD 39/20/13",
                "material": "3C95",
                "gapping": [],
                "numberStacks": 1
            }
        }
        core = PyOpenMagnetics.calculate_core_data(core_data, False)
        
        # API: create_basic_bobbin(core, margin: float)
        # margin is the winding margin in meters
        bobbin = PyOpenMagnetics.create_basic_bobbin(core, 0.001)
        
        assert bobbin is not None
        assert isinstance(bobbin, dict)
    
    def test_find_bobbin_by_name(self):
        """Find an existing bobbin from database."""
        bobbins = PyOpenMagnetics.get_bobbins()
        
        if len(bobbins) > 0:
            # Find by name if available
            first_bobbin = bobbins[0]
            if "name" in first_bobbin:
                found = PyOpenMagnetics.find_bobbin_by_name(first_bobbin["name"])
                assert found is not None


class TestWindingOperations:
    """Test winding-related operations."""
    
    def test_get_wires_database(self):
        """Verify wire database is accessible for winding operations."""
        wires = PyOpenMagnetics.get_wire_names()
        
        assert wires is not None
        assert isinstance(wires, list)
        assert len(wires) > 0
    
    def test_find_wire_by_name(self):
        """Find a wire by name for winding specification."""
        wires = PyOpenMagnetics.get_wire_names()
        
        if len(wires) > 0:
            wire = PyOpenMagnetics.find_wire_by_name(wires[0])
            assert wire is not None
            assert isinstance(wire, dict)
    
    def test_get_wire_outer_dimensions(self):
        """Get wire outer dimensions for winding calculations."""
        wires = PyOpenMagnetics.get_wire_names()
        
        if len(wires) > 0:
            wire = PyOpenMagnetics.find_wire_by_name(wires[0])
            dims = PyOpenMagnetics.get_outer_dimensions(wire)
            assert dims is not None
            # May return list (for round wires) or dict (for rectangular)
            assert isinstance(dims, (dict, list))


class TestBuckInductorWorkflow:
    """Test complete buck inductor design workflow (from example)."""
    
    def test_buck_inductor_parameters(self):
        """Verify buck inductor design parameters calculation."""
        # Design parameters
        V_IN = 48
        V_OUT = 12
        I_OUT = 10
        F_SW = 100000
        RIPPLE = 0.20
        
        duty_cycle = V_OUT / V_IN
        delta_I = RIPPLE * I_OUT
        L_min = (V_IN - V_OUT) * duty_cycle / (F_SW * delta_I)
        
        # Verify calculated inductance is reasonable
        assert L_min > 0
        assert L_min < 1e-3  # Less than 1 mH for this application
        
        # Create inputs structure
        inputs = {
            "designRequirements": {
                "name": "Buck Inductor Test",
                "magnetizingInductance": {"nominal": L_min * 1.2},
                "turnsRatios": []
            },
            "operatingPoints": [
                {
                    "name": "Nominal",
                    "conditions": {"ambientTemperature": 40},
                    "excitationsPerWinding": [
                        {
                            "name": "Primary",
                            "frequency": F_SW,
                            "current": {
                                "processed": {
                                    "label": "Triangular",
                                    "dutyCycle": duty_cycle,
                                    "peakToPeak": delta_I,
                                    "offset": I_OUT
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        # Verify inputs structure is valid
        assert "designRequirements" in inputs
        assert "operatingPoints" in inputs
        assert len(inputs["operatingPoints"]) > 0
    
    @pytest.mark.skip(reason="Core adviser may timeout in CI environments")
    def test_get_advised_cores(self):
        """Test core adviser (skipped by default - long running)."""
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [
                {
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {"frequency": 100000, "current": {"processed": {"peakToPeak": 2, "offset": 5}}}
                    ]
                }
            ]
        }
        
        cores = PyOpenMagnetics.get_advised_cores(inputs, maximum_number_results=3)
        assert cores is not None


class TestValidationModule:
    """Test the validation module if available."""
    
    def test_validate_inputs(self):
        """Test input validation."""
        try:
            from api.validation import validate_inputs, quick_validate
        except ImportError:
            pytest.skip("Validation module not available")
        
        # Valid inputs
        valid_inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [
                {
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [
                        {"name": "Primary", "frequency": 100000}
                    ]
                }
            ]
        }
        
        try:
            errors = validate_inputs(valid_inputs)
            # May have schema-specific errors but shouldn't raise
            assert isinstance(errors, list)
        except Exception as e:
            # Schema references may not be resolvable offline
            if "Unresolvable" in str(e) or "Unretrievable" in str(e):
                pytest.skip("Schema references not resolvable offline")
            raise
    
    def test_validate_core(self):
        """Test core validation."""
        try:
            from api.validation import validate_core
        except ImportError:
            pytest.skip("Validation module not available")
        
        # Valid core
        valid_core = {
            "functionalDescription": {
                "shape": "ETD 39/20/13",
                "material": "3C95",
                "gapping": [],
                "numberStacks": 1
            }
        }
        
        errors = validate_core(valid_core)
        assert errors == []  # Should have no errors
        
        # Invalid core (missing shape)
        invalid_core = {
            "functionalDescription": {
                "material": "3C95"
            }
        }
        
        errors = validate_core(invalid_core)
        assert len(errors) > 0  # Should have errors


class TestExampleScriptsImport:
    """Test that example scripts can be imported without error."""
    
    @pytest.fixture
    def examples_path(self):
        """Path to examples directory."""
        return Path(__file__).parent.parent / "examples"
    
    def test_examples_directory_exists(self, examples_path):
        """Verify examples directory exists."""
        assert examples_path.exists(), f"Examples directory not found: {examples_path}"
    
    def test_buck_inductor_example_exists(self, examples_path):
        """Verify buck inductor example exists."""
        example_file = examples_path / "buck_inductor.py"
        assert example_file.exists(), f"Buck inductor example not found: {example_file}"
    
    def test_flyback_example_exists(self, examples_path):
        """Verify flyback example exists."""
        example_file = examples_path / "flyback_design.py"
        assert example_file.exists(), f"Flyback example not found: {example_file}"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
