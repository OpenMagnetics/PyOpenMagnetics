"""
Tests for PyOpenMagnetics bobbin functions (extended coverage).

Covers create_basic_bobbin(), bobbin data access, and bobbin fitting checks.
"""
import pytest
import PyOpenMagnetics


class TestCreateBobbin:
    """Test create_basic_bobbin() function."""

    def test_create_bobbin_from_etd_core(self, computed_core):
        """Create a basic bobbin from ETD 49 core."""
        bobbin = PyOpenMagnetics.create_basic_bobbin(computed_core, 0.001)
        assert isinstance(bobbin, dict)

    def test_create_bobbin_returns_dict(self, computed_core):
        """create_basic_bobbin should return a dict."""
        bobbin = PyOpenMagnetics.create_basic_bobbin(computed_core, 0.001)
        assert isinstance(bobbin, dict)
        assert len(bobbin) > 0

    def test_create_bobbin_from_e_core(self):
        """Create bobbin from E-shaped core."""
        core_data = {
            "functionalDescription": {
                "type": "two-piece set",
                "material": "3C95",
                "shape": "E 42/21/15",
                "gapping": [],
                "numberStacks": 1
            }
        }
        core = PyOpenMagnetics.calculate_core_data(core_data, False)
        bobbin = PyOpenMagnetics.create_basic_bobbin(core, 0.001)
        assert isinstance(bobbin, dict)

    def test_create_bobbin_different_margins(self, computed_core):
        """Create bobbins with different margin sizes."""
        bobbin_small = PyOpenMagnetics.create_basic_bobbin(computed_core, 0.0005)
        bobbin_large = PyOpenMagnetics.create_basic_bobbin(computed_core, 0.002)
        assert isinstance(bobbin_small, dict)
        assert isinstance(bobbin_large, dict)

    def test_bobbin_has_processed_description(self, basic_bobbin):
        """Created bobbin should have processed description."""
        has_description = (
            "processedDescription" in basic_bobbin
            or "functionalDescription" in basic_bobbin
        )
        assert has_description


class TestBobbinDatabase:
    """Test bobbin database access."""

    def test_get_bobbins(self):
        """Get all bobbins from database."""
        bobbins = PyOpenMagnetics.get_bobbins()
        assert isinstance(bobbins, list)

    def test_get_bobbin_names(self):
        """Get bobbin names from database."""
        names = PyOpenMagnetics.get_bobbin_names()
        assert isinstance(names, list)

    def test_find_bobbin_by_name(self):
        """Find bobbin by name from database."""
        names = PyOpenMagnetics.get_bobbin_names()
        if len(names) > 0:
            bobbin = PyOpenMagnetics.find_bobbin_by_name(names[0])
            assert isinstance(bobbin, dict)


class TestBobbinFitting:
    """Test coil fitting in bobbin."""

    def test_sections_and_layers_fitting_true(self, wound_inductor_coil):
        """A properly wound coil should fit."""
        result = PyOpenMagnetics.are_sections_and_layers_fitting(wound_inductor_coil)
        assert isinstance(result, bool)
        # A 20-turn coil on ETD 49 should fit
        assert result is True

    def test_sections_and_layers_fitting_check(self, wound_transformer_coil):
        """Check fitting for transformer coil."""
        result = PyOpenMagnetics.are_sections_and_layers_fitting(wound_transformer_coil)
        assert isinstance(result, bool)
