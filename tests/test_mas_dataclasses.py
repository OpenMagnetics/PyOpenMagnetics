"""
Tests for MAS.py auto-generated dataclasses.

Verifies from_dict/to_dict round-trip fidelity, enum validation,
Union type handling, and edge cases for the Magnetic Agnostic Structure
data model.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.MAS import (
    DimensionWithTolerance,
    CTI,
    InsulationType,
    InsulationStandards,
    InsulationRequirements,
    IsolationSide,
    Market,
    MaximumDimensions,
    DesignRequirements,
    Topology,
    OperatingConditions,
    Harmonics,
    WaveformLabel,
    Processed,
    Waveform,
    SignalDescriptor,
    OperatingPoint,
    Inputs,
    ManufacturerInfo,
    Status,
    Masfromdict,
    Mastodict,
    from_float,
    from_str,
    from_int,
    from_bool,
    from_list,
    from_none,
    from_union,
)


class TestDimensionWithTolerance:
    """Test DimensionWithTolerance dataclass."""

    def test_nominal_only(self):
        """Create with only nominal value."""
        obj = {"nominal": 100e-6}
        dim = DimensionWithTolerance.from_dict(obj)
        assert dim.nominal == 100e-6
        assert dim.minimum is None
        assert dim.maximum is None

    def test_all_fields(self):
        """Create with all fields populated."""
        obj = {
            "nominal": 100e-6,
            "minimum": 90e-6,
            "maximum": 110e-6,
            "excludeMinimum": False,
            "excludeMaximum": True
        }
        dim = DimensionWithTolerance.from_dict(obj)
        assert dim.nominal == 100e-6
        assert dim.minimum == 90e-6
        assert dim.maximum == 110e-6
        assert dim.excludeMinimum is False
        assert dim.excludeMaximum is True

    def test_round_trip(self):
        """from_dict(obj).to_dict() should preserve data."""
        obj = {"nominal": 50.0, "minimum": 45.0, "maximum": 55.0}
        dim = DimensionWithTolerance.from_dict(obj)
        result = dim.to_dict()
        assert result["nominal"] == 50.0
        assert result["minimum"] == 45.0
        assert result["maximum"] == 55.0

    def test_none_fields_omitted_from_to_dict(self):
        """to_dict() should omit None fields."""
        obj = {"nominal": 100e-6}
        dim = DimensionWithTolerance.from_dict(obj)
        result = dim.to_dict()
        assert "nominal" in result
        assert "minimum" not in result
        assert "maximum" not in result
        assert "excludeMinimum" not in result

    def test_integer_nominal_converted_to_float(self):
        """Integer input should be accepted and converted."""
        obj = {"nominal": 100}
        dim = DimensionWithTolerance.from_dict(obj)
        assert isinstance(dim.nominal, float)
        assert dim.nominal == 100.0


class TestEnumTypes:
    """Test enum dataclasses from MAS schema."""

    def test_cti_enum(self):
        """CTI enum should have correct values."""
        assert CTI.GroupI.value == "Group I"
        assert CTI.GroupII.value == "Group II"
        assert CTI.GroupIIIA.value == "Group IIIA"
        assert CTI.GroupIIIB.value == "Group IIIB"

    def test_insulation_type_enum(self):
        """InsulationType should have all standard types."""
        assert InsulationType.Basic.value == "Basic"
        assert InsulationType.Double.value == "Double"
        assert InsulationType.Functional.value == "Functional"
        assert InsulationType.Reinforced.value == "Reinforced"
        assert InsulationType.Supplementary.value == "Supplementary"

    def test_topology_enum(self):
        """Topology enum should include common converter topologies."""
        assert Topology.FlybackConverter.value == "Flyback Converter"
        assert Topology.BuckConverter.value == "Buck Converter"
        assert Topology.BoostConverter.value == "Boost Converter"
        assert Topology.PushPullConverter.value == "Push-Pull Converter"

    def test_waveform_label_enum(self):
        """WaveformLabel enum should include standard waveform types."""
        assert WaveformLabel.Sinusoidal.value == "Sinusoidal"
        assert WaveformLabel.Triangular.value == "Triangular"
        assert WaveformLabel.Rectangular.value == "Rectangular"
        assert WaveformLabel.Custom.value == "Custom"

    def test_isolation_side_enum(self):
        """IsolationSide should include primary and secondary."""
        assert IsolationSide.primary.value == "primary"
        assert IsolationSide.secondary.value == "secondary"
        assert IsolationSide.tertiary.value == "tertiary"

    def test_market_enum(self):
        """Market enum should have standard categories."""
        assert Market.Commercial.value == "Commercial"
        assert Market.Industrial.value == "Industrial"
        assert Market.Medical.value == "Medical"


class TestInsulationRequirements:
    """Test InsulationRequirements dataclass."""

    def test_basic_insulation(self):
        """Create basic insulation requirements."""
        obj = {
            "insulationType": "Basic",
            "cti": "Group I"
        }
        ins = InsulationRequirements.from_dict(obj)
        assert ins.insulationType == InsulationType.Basic
        assert ins.cti == CTI.GroupI

    def test_with_optional_fields(self):
        """Create with altitude and standards."""
        obj = {
            "insulationType": "Reinforced",
            "altitude": {"nominal": 2000},
            "standards": ["IEC 62368-1"]
        }
        ins = InsulationRequirements.from_dict(obj)
        assert ins.insulationType == InsulationType.Reinforced
        assert ins.altitude.nominal == 2000
        assert ins.standards == [InsulationStandards.IEC623681]

    def test_to_dict_omits_none(self):
        """to_dict should omit None fields."""
        obj = {"insulationType": "Double"}
        ins = InsulationRequirements.from_dict(obj)
        result = ins.to_dict()
        assert "insulationType" in result
        assert result["insulationType"] == "Double"
        assert "cti" not in result
        assert "altitude" not in result


class TestDesignRequirements:
    """Test DesignRequirements dataclass."""

    def test_inductor_requirements(self):
        """Inductor has inductance but no turns ratios."""
        obj = {
            "magnetizingInductance": {"nominal": 100e-6},
            "turnsRatios": []
        }
        dr = DesignRequirements.from_dict(obj)
        assert dr.magnetizingInductance.nominal == 100e-6
        assert dr.turnsRatios == []

    def test_transformer_requirements(self):
        """Transformer has turns ratios."""
        obj = {
            "magnetizingInductance": {"nominal": 500e-6},
            "turnsRatios": [{"nominal": 0.1}]
        }
        dr = DesignRequirements.from_dict(obj)
        assert len(dr.turnsRatios) == 1
        assert abs(dr.turnsRatios[0].nominal - 0.1) < 1e-9

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {
            "magnetizingInductance": {"nominal": 100e-6},
            "turnsRatios": [{"nominal": 0.5}],
            "name": "Test DR",
            "topology": "Flyback Converter"
        }
        dr = DesignRequirements.from_dict(obj)
        result = dr.to_dict()
        assert result["magnetizingInductance"]["nominal"] == 100e-6
        assert len(result["turnsRatios"]) == 1
        assert result["name"] == "Test DR"
        assert result["topology"] == "Flyback Converter"


class TestOperatingPoint:
    """Test OperatingPoint and related dataclasses."""

    def test_basic_operating_point(self):
        """Create basic operating point."""
        obj = {
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {"frequency": 100000}
            ]
        }
        op = OperatingPoint.from_dict(obj)
        assert op.conditions.ambientTemperature == 25
        assert len(op.excitationsPerWinding) == 1
        assert op.excitationsPerWinding[0].frequency == 100000

    def test_with_waveform(self):
        """Operating point with waveform data."""
        obj = {
            "conditions": {"ambientTemperature": 25},
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
        op = OperatingPoint.from_dict(obj)
        waveform = op.excitationsPerWinding[0].current.waveform
        assert len(waveform.data) == 3
        assert len(waveform.time) == 3

    def test_with_processed_data(self):
        """Operating point with processed signal data."""
        obj = {
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {
                    "frequency": 100000,
                    "current": {
                        "processed": {
                            "label": "Sinusoidal",
                            "offset": 0,
                            "peakToPeak": 10,
                            "dutyCycle": 0.5
                        }
                    }
                }
            ]
        }
        op = OperatingPoint.from_dict(obj)
        processed = op.excitationsPerWinding[0].current.processed
        assert processed.label == WaveformLabel.Sinusoidal
        assert processed.peakToPeak == 10

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {
            "name": "Nominal",
            "conditions": {"ambientTemperature": 42},
            "excitationsPerWinding": [
                {
                    "frequency": 200000,
                    "current": {
                        "processed": {
                            "label": "Triangular",
                            "offset": 5,
                            "peakToPeak": 3
                        }
                    }
                }
            ]
        }
        op = OperatingPoint.from_dict(obj)
        result = op.to_dict()
        assert result["name"] == "Nominal"
        assert result["conditions"]["ambientTemperature"] == 42
        assert result["excitationsPerWinding"][0]["frequency"] == 200000


class TestInputs:
    """Test Inputs dataclass."""

    def test_basic_inputs(self):
        """Create basic inputs structure."""
        obj = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": []
            },
            "operatingPoints": [
                {
                    "conditions": {"ambientTemperature": 25},
                    "excitationsPerWinding": [{"frequency": 100000}]
                }
            ]
        }
        inp = Inputs.from_dict(obj)
        assert inp.designRequirements.magnetizingInductance.nominal == 100e-6
        assert len(inp.operatingPoints) == 1

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 50e-6},
                "turnsRatios": [{"nominal": 0.25}]
            },
            "operatingPoints": [
                {
                    "conditions": {"ambientTemperature": 85},
                    "excitationsPerWinding": [{"frequency": 500000}]
                }
            ]
        }
        inp = Inputs.from_dict(obj)
        result = inp.to_dict()
        assert result["designRequirements"]["magnetizingInductance"]["nominal"] == 50e-6
        assert len(result["designRequirements"]["turnsRatios"]) == 1
        assert result["operatingPoints"][0]["conditions"]["ambientTemperature"] == 85

    def test_missing_required_field_raises(self):
        """Missing required field should raise AssertionError."""
        with pytest.raises((AssertionError, KeyError, TypeError)):
            Inputs.from_dict({"designRequirements": {"magnetizingInductance": {"nominal": 100e-6}, "turnsRatios": []}})


class TestSignalDescriptor:
    """Test SignalDescriptor (harmonics + processed + waveform)."""

    def test_with_waveform(self):
        """SignalDescriptor with waveform data."""
        obj = {
            "waveform": {
                "data": [0, 1, 0, -1, 0],
                "time": [0, 0.25e-5, 0.5e-5, 0.75e-5, 1e-5]
            }
        }
        sd = SignalDescriptor.from_dict(obj)
        assert sd.waveform is not None
        assert len(sd.waveform.data) == 5

    def test_with_processed(self):
        """SignalDescriptor with processed data."""
        obj = {
            "processed": {
                "label": "Sinusoidal",
                "offset": 0,
                "peakToPeak": 10,
                "rms": 3.54
            }
        }
        sd = SignalDescriptor.from_dict(obj)
        assert sd.processed is not None
        assert sd.processed.rms == 3.54

    def test_with_harmonics(self):
        """SignalDescriptor with harmonics."""
        obj = {
            "harmonics": {
                "amplitudes": [5.0, 0.1, 0.05],
                "frequencies": [100000, 200000, 300000]
            }
        }
        sd = SignalDescriptor.from_dict(obj)
        assert sd.harmonics is not None
        assert len(sd.harmonics.amplitudes) == 3

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {
            "processed": {
                "label": "Triangular",
                "offset": 2.5,
                "peakToPeak": 5
            },
            "harmonics": {
                "amplitudes": [2.5, 0.3],
                "frequencies": [100000, 300000]
            }
        }
        sd = SignalDescriptor.from_dict(obj)
        result = sd.to_dict()
        assert result["processed"]["label"] == "Triangular"
        assert len(result["harmonics"]["amplitudes"]) == 2


class TestWaveform:
    """Test Waveform dataclass."""

    def test_basic_waveform(self):
        """Create waveform with data and time."""
        obj = {"data": [1, 2, 3], "time": [0, 0.5, 1.0]}
        wf = Waveform.from_dict(obj)
        assert len(wf.data) == 3
        assert len(wf.time) == 3

    def test_equidistant_waveform(self):
        """Waveform without time (equidistant points)."""
        obj = {"data": [0, 1, 0, -1]}
        wf = Waveform.from_dict(obj)
        assert len(wf.data) == 4
        assert wf.time is None

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {"data": [1.0, 2.0, 3.0], "time": [0.0, 0.5, 1.0], "numberPeriods": 1}
        wf = Waveform.from_dict(obj)
        result = wf.to_dict()
        assert result["data"] == [1.0, 2.0, 3.0]
        assert result["numberPeriods"] == 1


class TestProcessed:
    """Test Processed dataclass."""

    def test_minimal_processed(self):
        """Create processed with only required fields."""
        obj = {"label": "Sinusoidal", "offset": 0}
        p = Processed.from_dict(obj)
        assert p.label == WaveformLabel.Sinusoidal
        assert p.offset == 0
        assert p.rms is None

    def test_full_processed(self):
        """Create processed with all fields."""
        obj = {
            "label": "Triangular",
            "offset": 5,
            "rms": 2.88,
            "peakToPeak": 10,
            "dutyCycle": 0.5,
            "peak": 10,
            "thd": 0.12
        }
        p = Processed.from_dict(obj)
        assert p.label == WaveformLabel.Triangular
        assert p.rms == 2.88
        assert p.dutyCycle == 0.5

    def test_round_trip(self):
        """from_dict -> to_dict round-trip preserving set fields."""
        obj = {"label": "Rectangular", "offset": 2.5, "peakToPeak": 10}
        p = Processed.from_dict(obj)
        result = p.to_dict()
        assert result["label"] == "Rectangular"
        assert result["offset"] == 2.5
        assert result["peakToPeak"] == 10
        # None fields omitted
        assert "rms" not in result


class TestHarmonicsDataclass:
    """Test Harmonics dataclass."""

    def test_basic_harmonics(self):
        """Create harmonics with amplitudes and frequencies."""
        obj = {
            "amplitudes": [5.0, 1.0, 0.5],
            "frequencies": [100000, 200000, 300000]
        }
        h = Harmonics.from_dict(obj)
        assert len(h.amplitudes) == 3
        assert len(h.frequencies) == 3

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {
            "amplitudes": [3.14, 0.5],
            "frequencies": [50000, 150000]
        }
        h = Harmonics.from_dict(obj)
        result = h.to_dict()
        assert result["amplitudes"] == [3.14, 0.5]
        assert result["frequencies"] == [50000, 150000]


class TestOperatingConditions:
    """Test OperatingConditions dataclass."""

    def test_basic_conditions(self):
        """Create with ambient temperature."""
        obj = {"ambientTemperature": 25}
        oc = OperatingConditions.from_dict(obj)
        assert oc.ambientTemperature == 25

    def test_with_cooling(self):
        """Create with cooling configuration."""
        obj = {
            "ambientTemperature": 40,
            "cooling": {
                "fluid": "air",
                "temperature": 25
            }
        }
        oc = OperatingConditions.from_dict(obj)
        assert oc.cooling is not None
        assert oc.cooling.fluid == "air"

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {"ambientTemperature": 85, "name": "Hot"}
        oc = OperatingConditions.from_dict(obj)
        result = oc.to_dict()
        assert result["ambientTemperature"] == 85
        assert result["name"] == "Hot"


class TestMaximumDimensions:
    """Test MaximumDimensions dataclass."""

    def test_all_dimensions(self):
        """Create with all three dimensions."""
        obj = {"width": 0.05, "height": 0.03, "depth": 0.04}
        md = MaximumDimensions.from_dict(obj)
        assert md.width == 0.05
        assert md.height == 0.03
        assert md.depth == 0.04

    def test_partial_dimensions(self):
        """Create with only height constraint."""
        obj = {"height": 0.025}
        md = MaximumDimensions.from_dict(obj)
        assert md.height == 0.025
        assert md.width is None
        assert md.depth is None

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {"height": 0.02}
        md = MaximumDimensions.from_dict(obj)
        result = md.to_dict()
        assert result["height"] == 0.02
        assert "width" not in result


class TestManufacturerInfo:
    """Test ManufacturerInfo dataclass."""

    def test_basic_info(self):
        """Create with required name field."""
        obj = {"name": "Ferroxcube"}
        mi = ManufacturerInfo.from_dict(obj)
        assert mi.name == "Ferroxcube"

    def test_with_status(self):
        """Create with production status."""
        obj = {"name": "TDK", "status": "production", "reference": "B66311"}
        mi = ManufacturerInfo.from_dict(obj)
        assert mi.status == Status.production
        assert mi.reference == "B66311"

    def test_round_trip(self):
        """from_dict -> to_dict round-trip."""
        obj = {"name": "Magnetics Inc", "family": "Kool Mu"}
        mi = ManufacturerInfo.from_dict(obj)
        result = mi.to_dict()
        assert result["name"] == "Magnetics Inc"
        assert result["family"] == "Kool Mu"


class TestHelperFunctions:
    """Test module-level helper functions."""

    def test_from_float_with_int(self):
        """from_float should accept int and return float."""
        result = from_float(42)
        assert isinstance(result, float)
        assert result == 42.0

    def test_from_float_with_float(self):
        """from_float should accept float."""
        result = from_float(3.14)
        assert result == 3.14

    def test_from_float_rejects_bool(self):
        """from_float should reject bool (subclass of int)."""
        with pytest.raises(AssertionError):
            from_float(True)

    def test_from_str_rejects_int(self):
        """from_str should reject non-string."""
        with pytest.raises(AssertionError):
            from_str(42)

    def test_from_int_rejects_bool(self):
        """from_int should reject bool."""
        with pytest.raises(AssertionError):
            from_int(True)

    def test_from_bool_accepts_bool(self):
        """from_bool should accept True/False."""
        assert from_bool(True) is True
        assert from_bool(False) is False

    def test_from_list_applies_function(self):
        """from_list should apply converter function to each element."""
        result = from_list(from_float, [1, 2.5, 3])
        assert result == [1.0, 2.5, 3.0]

    def test_from_none_accepts_none(self):
        """from_none should accept None."""
        assert from_none(None) is None

    def test_from_none_rejects_value(self):
        """from_none should reject non-None."""
        with pytest.raises(AssertionError):
            from_none(42)

    def test_from_union_tries_converters(self):
        """from_union should try each converter in order."""
        result = from_union([from_float, from_none], 42)
        assert result == 42.0

        result_none = from_union([from_float, from_none], None)
        assert result_none is None


class TestMasFunctions:
    """Test module-level Mas helper functions."""

    def test_masfromdict(self):
        """Masfromdict should create Mas from dict."""
        obj = {
            "inputs": {
                "designRequirements": {
                    "magnetizingInductance": {"nominal": 100e-6},
                    "turnsRatios": []
                },
                "operatingPoints": [
                    {
                        "conditions": {"ambientTemperature": 25},
                        "excitationsPerWinding": [{"frequency": 100000}]
                    }
                ]
            },
            "magnetic": {
                "core": {
                    "functionalDescription": {
                        "type": "two-piece set",
                        "material": "3C95",
                        "shape": "ETD 49/25/16",
                        "gapping": [],
                        "numberStacks": 1
                    }
                },
                "coil": {
                    "bobbin": "ETD 49/25/16",
                    "functionalDescription": [
                        {
                            "name": "Primary",
                            "numberTurns": 20,
                            "numberParallels": 1,
                            "isolationSide": "primary",
                            "wire": "Round 0.5 - Grade 1"
                        }
                    ]
                }
            },
            "outputs": []
        }
        mas = Masfromdict(obj)
        assert mas.inputs.designRequirements.magnetizingInductance.nominal == 100e-6

    def test_mastodict(self):
        """Mastodict should convert Mas to dict."""
        obj = {
            "inputs": {
                "designRequirements": {
                    "magnetizingInductance": {"nominal": 50e-6},
                    "turnsRatios": []
                },
                "operatingPoints": [
                    {
                        "conditions": {"ambientTemperature": 40},
                        "excitationsPerWinding": [{"frequency": 200000}]
                    }
                ]
            },
            "magnetic": {
                "core": {
                    "functionalDescription": {
                        "type": "two-piece set",
                        "material": "3C95",
                        "shape": "E 42/21/15",
                        "gapping": [],
                        "numberStacks": 1
                    }
                },
                "coil": {
                    "bobbin": "E 42/21/15",
                    "functionalDescription": [
                        {
                            "name": "Primary",
                            "numberTurns": 10,
                            "numberParallels": 1,
                            "isolationSide": "primary",
                            "wire": "Round 0.5 - Grade 1"
                        }
                    ]
                }
            },
            "outputs": []
        }
        mas = Masfromdict(obj)
        result = Mastodict(mas)
        assert isinstance(result, dict)
        assert "inputs" in result
        assert "magnetic" in result
        assert "outputs" in result
