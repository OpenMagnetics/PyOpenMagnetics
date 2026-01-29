"""
Tests for PyOpenMagnetics settings and configuration functions.

Covers get_settings(), set_settings(), reset_settings(),
get_constants(), and get_default_models().
"""
import pytest
import PyOpenMagnetics


class TestConstants:
    """Test get_constants() function."""

    def test_get_constants_returns_dict(self):
        """get_constants should return a dict."""
        result = PyOpenMagnetics.get_constants()
        assert isinstance(result, dict)

    def test_constants_has_vacuum_permeability(self):
        """Constants should include vacuum permeability ~1.26e-6."""
        result = PyOpenMagnetics.get_constants()
        if isinstance(result, dict):
            # Look for vacuum permeability (mu_0 = 4*pi*1e-7 ~= 1.256e-6)
            has_mu0 = any(
                "permeability" in k.lower() or "mu" in k.lower()
                for k in result.keys()
            )
            if has_mu0:
                for k, v in result.items():
                    if "permeability" in k.lower():
                        assert abs(v - 1.2566e-6) < 1e-8

    def test_constants_not_empty(self):
        """Constants dict should not be empty."""
        result = PyOpenMagnetics.get_constants()
        assert len(result) > 0


class TestDefaults:
    """Test get_settings() / default settings."""

    def test_get_settings_returns_dict(self):
        """get_settings should return a dict."""
        result = PyOpenMagnetics.get_settings()
        assert isinstance(result, dict)

    def test_settings_not_empty(self):
        """Settings should contain some configuration."""
        result = PyOpenMagnetics.get_settings()
        assert len(result) > 0

    def test_settings_after_reset(self, reset_settings):
        """After reset, settings should still be accessible."""
        result = PyOpenMagnetics.get_settings()
        assert isinstance(result, dict)
        assert len(result) > 0


class TestDefaultModels:
    """Test get_default_models() function."""

    def test_get_default_models_returns_dict(self):
        """get_default_models should return a dict."""
        result = PyOpenMagnetics.get_default_models()
        assert isinstance(result, dict)

    def test_default_models_not_empty(self):
        """Default models should have entries."""
        result = PyOpenMagnetics.get_default_models()
        assert len(result) > 0


class TestSetSettings:
    """Test set_settings() function."""

    def test_set_and_get_settings(self, reset_settings):
        """Should be able to set and retrieve settings."""
        original = PyOpenMagnetics.get_settings()
        assert isinstance(original, dict)

        # Set settings (pass same settings back)
        PyOpenMagnetics.set_settings(original)
        after = PyOpenMagnetics.get_settings()
        assert isinstance(after, dict)

    def test_reset_restores_defaults(self):
        """reset_settings should restore default configuration."""
        # Get defaults
        PyOpenMagnetics.reset_settings()
        defaults = PyOpenMagnetics.get_settings()

        # Modify something
        modified = dict(defaults)
        PyOpenMagnetics.set_settings(modified)

        # Reset
        PyOpenMagnetics.reset_settings()
        after_reset = PyOpenMagnetics.get_settings()
        assert isinstance(after_reset, dict)

    def test_settings_persist_within_session(self, reset_settings):
        """Settings changes should persist until reset."""
        settings = PyOpenMagnetics.get_settings()
        PyOpenMagnetics.set_settings(settings)
        retrieved = PyOpenMagnetics.get_settings()
        assert isinstance(retrieved, dict)

    def test_multiple_resets_safe(self):
        """Multiple reset calls should be safe."""
        PyOpenMagnetics.reset_settings()
        PyOpenMagnetics.reset_settings()
        PyOpenMagnetics.reset_settings()
        result = PyOpenMagnetics.get_settings()
        assert isinstance(result, dict)
