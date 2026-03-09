"""
Tests for PyOpenMagnetics visualization/plotting functions.

Covers plot_core, plot_magnetic, plot_wire, plot_bobbin SVG generation.
Plot functions return dict with {success: bool, svg: str} or just str.
"""
import pytest
import PyOpenMagnetics


def _get_svg(result):
    """Extract SVG string from plot result (may be str or dict)."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return result.get("svg", "")
    return ""


def _is_svg(result):
    """Check if result contains valid SVG content."""
    svg = _get_svg(result)
    return isinstance(svg, str) and "<svg" in svg.lower()


class TestPlotCore:
    """Test plot_core() SVG generation.

    Note: plot_core() takes a magnetic JSON (core+coil), not just a core dict.
    """

    def test_plot_core_returns_result(self, simple_magnetic):
        """plot_core should return a result."""
        result = PyOpenMagnetics.plot_core(simple_magnetic)
        assert result is not None

    def test_plot_core_contains_svg(self, simple_magnetic):
        """plot_core output should contain SVG content."""
        result = PyOpenMagnetics.plot_core(simple_magnetic)
        assert _is_svg(result), f"Expected SVG, got: {type(result)}"

    def test_plot_core_result_type(self, simple_magnetic):
        """plot_core should return a dict or str."""
        result = PyOpenMagnetics.plot_core(simple_magnetic)
        assert isinstance(result, (dict, str))


class TestPlotMagnetic:
    """Test plot_magnetic() SVG generation."""

    def test_plot_magnetic_returns_result(self, simple_magnetic):
        """plot_magnetic should return a result."""
        if not hasattr(PyOpenMagnetics, "plot_magnetic"):
            pytest.skip("plot_magnetic not available")
        result = PyOpenMagnetics.plot_magnetic(simple_magnetic)
        assert result is not None

    def test_plot_magnetic_contains_svg(self, simple_magnetic):
        """plot_magnetic output should contain SVG content."""
        if not hasattr(PyOpenMagnetics, "plot_magnetic"):
            pytest.skip("plot_magnetic not available")
        result = PyOpenMagnetics.plot_magnetic(simple_magnetic)
        assert _is_svg(result)


class TestPlotWire:
    """Test plot_wire() SVG generation."""

    def test_plot_wire_returns_result(self, sample_round_wire):
        """plot_wire should return a result."""
        result = PyOpenMagnetics.plot_wire(sample_round_wire)
        assert result is not None

    def test_plot_wire_contains_svg(self, sample_round_wire):
        """plot_wire output should contain SVG content."""
        result = PyOpenMagnetics.plot_wire(sample_round_wire)
        assert _is_svg(result)

    def test_plot_wire_success_flag(self, sample_round_wire):
        """plot_wire result should indicate success."""
        result = PyOpenMagnetics.plot_wire(sample_round_wire)
        if isinstance(result, dict):
            assert result.get("success", False) is True


class TestPlotBobbin:
    """Test plot_bobbin() SVG generation."""

    def test_plot_bobbin_returns_result(self, basic_bobbin):
        """plot_bobbin should return a result."""
        result = PyOpenMagnetics.plot_bobbin(basic_bobbin)
        assert result is not None

    def test_plot_bobbin_result_type(self, basic_bobbin):
        """plot_bobbin should return dict or str."""
        result = PyOpenMagnetics.plot_bobbin(basic_bobbin)
        assert isinstance(result, (dict, str))


class TestPlotFields:
    """Test field plotting functions."""

    def test_plot_magnetic_field_exists(self):
        """plot_magnetic_field should be available."""
        assert hasattr(PyOpenMagnetics, "plot_magnetic_field")

    def test_plot_electric_field_exists(self):
        """plot_electric_field should be available."""
        assert hasattr(PyOpenMagnetics, "plot_electric_field")
