"""Tests for PyOpenMagnetics Design Builder API."""

import pytest
import math


class TestDesignImports:
    """Test module imports."""

    def test_import_design(self):
        from api.design import Design
        assert Design is not None

    def test_import_result(self):
        from api.results import DesignResult
        assert DesignResult is not None

    def test_factory_methods(self):
        from api.design import Design
        assert callable(Design.flyback)
        assert callable(Design.buck)
        assert callable(Design.boost)
        assert callable(Design.inductor)
        assert callable(Design.forward)
        assert callable(Design.llc)


class TestFlybackBuilder:
    """Test FlybackBuilder."""

    def test_basic_flyback(self):
        from api.design import Design
        builder = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3)
        assert builder._vin_min == 85
        assert builder._vin_max == 265
        assert builder._vin_is_ac is True
        assert len(builder._outputs) == 1
        assert builder._frequency == 100e3

    def test_dc_input(self):
        from api.design import Design
        builder = Design.flyback().vin_dc(380, 420).output(12, 5).fsw(100e3)
        assert builder._vin_is_ac is False

    def test_multiple_outputs(self):
        from api.design import Design
        builder = Design.flyback().vin_ac(85, 265).output(12, 2).output(5, 1).output(3.3, 0.5).fsw(100e3)
        assert len(builder._outputs) == 3

    def test_calculated_parameters(self):
        from api.design import Design
        builder = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3)
        params = builder.get_calculated_parameters()
        assert "turns_ratio" in params
        assert "magnetizing_inductance_uH" in params

    def test_to_mas(self):
        from api.design import Design
        builder = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3)
        mas = builder.to_mas()
        assert "designRequirements" in mas
        assert "operatingPoints" in mas

    def test_solve_flyback(self):
        from api.design import Design
        results = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3).solve(max_results=3)
        assert isinstance(results, list)


class TestBuckBuilder:
    """Test BuckBuilder."""

    def test_basic_buck(self):
        from api.design import Design
        builder = Design.buck().vin(12, 24).vout(5).iout(3).fsw(500e3)
        assert builder._vin_min == 12
        assert builder._vout == 5
        assert builder._iout == 3

    def test_calculated_parameters(self):
        from api.design import Design
        builder = Design.buck().vin(12, 24).vout(5).iout(3).fsw(500e3)
        params = builder.get_calculated_parameters()
        assert "inductance_uH" in params
        assert params["inductance_uH"] > 0

    def test_solve_buck(self):
        from api.design import Design
        results = Design.buck().vin(12, 24).vout(5).iout(3).fsw(500e3).solve(max_results=3)
        assert isinstance(results, list)

    def test_invalid_vout(self):
        from api.design import Design
        builder = Design.buck().vin(5, 12).vout(15).iout(1).fsw(100e3)
        with pytest.raises(ValueError, match="Vout must be less than"):
            builder.get_calculated_parameters()


class TestBoostBuilder:
    """Test BoostBuilder."""

    def test_basic_boost(self):
        from api.design import Design
        builder = Design.boost().vin(3.0, 4.2).vout(5).pout(2).fsw(1e6)
        assert builder._vin_min == 3.0
        assert builder._vout == 5

    def test_solve_boost(self):
        from api.design import Design
        results = Design.boost().vin(3.0, 4.2).vout(5).pout(2).fsw(1e6).solve(max_results=3)
        assert isinstance(results, list)


class TestInductorBuilder:
    """Test InductorBuilder."""

    def test_basic_inductor(self):
        from api.design import Design
        builder = Design.inductor().inductance(100e-6).idc(5).iac_pp(1).fsw(100e3)
        assert builder._inductance == 100e-6
        assert builder._idc == 5

    def test_calculated_parameters(self):
        from api.design import Design
        builder = Design.inductor().inductance(100e-6).idc(5).iac_pp(1).fsw(100e3)
        params = builder.get_calculated_parameters()
        assert params["inductance_uH"] == 100

    def test_solve_inductor(self):
        from api.design import Design
        results = Design.inductor().inductance(100e-6).idc(5).iac_pp(1).fsw(100e3).solve(max_results=3)
        assert isinstance(results, list)


class TestForwardBuilder:
    """Test ForwardBuilder."""

    def test_basic_forward(self):
        from api.design import Design
        builder = Design.forward().vin_dc(380, 420).output(12, 10).fsw(100e3)
        assert builder._vin_min == 380
        assert len(builder._outputs) == 1

    def test_variant(self):
        from api.design import Design
        builder = Design.forward().variant("two_switch").vin_dc(380, 420).output(12, 10).fsw(100e3)
        assert builder._variant == "two_switch"


class TestLLCBuilder:
    """Test LLCBuilder."""

    def test_basic_llc(self):
        from api.design import Design
        builder = Design.llc().vin_dc(380, 420).output(12, 20).resonant_frequency(100e3)
        assert builder._vin_min == 380
        assert builder._resonant_freq == 100e3

    def test_calculated_parameters(self):
        from api.design import Design
        builder = Design.llc().vin_dc(380, 420).output(12, 20).resonant_frequency(100e3)
        params = builder.get_calculated_parameters()
        assert "turns_ratio" in params
        assert "magnetizing_inductance_uH" in params


class TestDesignResult:
    """Test DesignResult parsing."""

    def test_from_mas_basic(self):
        from api.results import DesignResult
        mas_data = {
            "magnetic": {
                "core": {"functionalDescription": {"shape": {"name": "ETD 34"}, "material": {"name": "3C95"},
                         "gapping": [{"type": "subtractive", "length": 0.0005}]}},
                "coil": {"functionalDescription": [{"name": "Primary", "numberTurns": 20, "wire": "AWG 24"}]}
            }
        }
        result = DesignResult.from_mas(mas_data)
        assert result.core == "ETD 34"
        assert result.material == "3C95"
        assert result.air_gap_mm == 0.5


class TestConstraints:
    """Test constraint methods."""

    def test_max_dimensions(self):
        from api.design import Design
        builder = Design.buck().vin(12, 24).vout(5).iout(3).fsw(500e3)
        builder.max_height(20).max_width(30).max_depth(25)
        dims = builder._get_max_dimensions()
        assert dims["height"] == 0.020

    def test_prefer_invalid(self):
        from api.design import Design
        with pytest.raises(ValueError):
            Design.buck().prefer("invalid")
