"""
Tests for simplified TAS format (basic DC-DC converters).
"""

import pytest
import json
from pathlib import Path

from tas import (
    TASDocument,
    TASMetadata,
    TASWaveform,
    WaveformShape,
    TASInductor,
    TASCapacitor,
    TASSwitch,
    TASDiode,
    TASMagnetic,
    TASComponentList,
    TASInputs,
    TASRequirements,
    TASOperatingPoint,
    TASModulation,
    ModulationType,
    ControlMode,
    OperatingMode,
    TASLossBreakdown,
    TASKPIs,
    create_buck_tas,
    create_boost_tas,
    create_flyback_tas,
)


class TestWaveforms:
    """Test TASWaveform class."""

    def test_triangular_waveform(self):
        """Test triangular waveform creation."""
        wf = TASWaveform.triangular(0.0, 1.0, 0.5, 1e-5, "A")
        assert wf.shape == WaveformShape.TRIANGULAR
        assert wf.peak == 1.0
        assert wf.min == 0.0
        assert wf.peak_to_peak == 1.0
        assert wf.period == 1e-5
        assert wf.frequency == pytest.approx(100000, rel=0.01)

    def test_rectangular_waveform(self):
        """Test rectangular waveform creation."""
        wf = TASWaveform.rectangular(12.0, 0.0, 0.4, 2e-6, "V")
        assert wf.shape == WaveformShape.RECTANGULAR
        assert wf.peak == 12.0
        assert wf.min == 0.0
        assert wf.period == 2e-6

    def test_waveform_serialization(self):
        """Test waveform dict conversion."""
        wf = TASWaveform.triangular(1.0, 2.0, 0.5, 1e-5, "A")
        d = wf.to_dict()
        wf2 = TASWaveform.from_dict(d)
        assert wf2.data == wf.data
        assert wf2.time == wf.time
        assert wf2.unit == wf.unit

    def test_mas_compatibility(self):
        """Test MAS format conversion."""
        wf = TASWaveform(data=[0, 1, 0], time=[0, 0.5, 1.0])
        mas = wf.to_mas()
        assert "waveform" in mas
        assert mas["waveform"]["data"] == [0, 1, 0]
        wf2 = TASWaveform.from_mas(mas)
        assert wf2.data == wf.data


class TestComponents:
    """Test component classes."""

    def test_inductor(self):
        """Test inductor creation and serialization."""
        ind = TASInductor(
            name="L1",
            inductance=100e-6,
            dcr=0.02,
            saturation_current=5.0,
            core_material="N87",
        )
        d = ind.to_dict()
        assert d["inductance"] == 100e-6
        assert d["type"] == "inductor"
        ind2 = TASInductor.from_dict(d)
        assert ind2.inductance == ind.inductance

    def test_capacitor(self):
        """Test capacitor creation and serialization."""
        cap = TASCapacitor(name="C1", capacitance=47e-6, esr=0.01)
        d = cap.to_dict()
        assert d["capacitance"] == 47e-6
        cap2 = TASCapacitor.from_dict(d)
        assert cap2.capacitance == cap.capacitance

    def test_switch(self):
        """Test switch creation and serialization."""
        sw = TASSwitch(name="Q1", rds_on=0.01, v_ds_max=30.0)
        d = sw.to_dict()
        assert d["rds_on"] == 0.01
        sw2 = TASSwitch.from_dict(d)
        assert sw2.rds_on == sw.rds_on

    def test_diode(self):
        """Test diode creation and serialization."""
        diode = TASDiode(name="D1", vf=0.5, v_rrm=40.0)
        d = diode.to_dict()
        assert d["vf"] == 0.5
        diode2 = TASDiode.from_dict(d)
        assert diode2.vf == diode.vf

    def test_magnetic(self):
        """Test magnetic (transformer) creation."""
        mag = TASMagnetic(
            name="T1",
            magnetizing_inductance=200e-6,
            leakage_inductance=2e-6,
            turns_ratio=4.0,
        )
        d = mag.to_dict()
        assert d["turns_ratio"] == 4.0
        mag2 = TASMagnetic.from_dict(d)
        assert mag2.turns_ratio == mag.turns_ratio

    def test_component_list(self):
        """Test component list container."""
        cl = TASComponentList(
            inductors=[TASInductor(name="L1", inductance=100e-6)],
            capacitors=[TASCapacitor(name="C1", capacitance=47e-6)],
        )
        assert len(cl.all_components) == 2
        d = cl.to_dict()
        assert "inductors" in d
        assert "capacitors" in d


class TestModulation:
    """Test modulation types."""

    def test_modulation_types(self):
        """Test basic modulation types."""
        assert ModulationType.PWM.value == "pwm"
        assert ModulationType.PFM.value == "pfm"
        assert ModulationType.HYSTERETIC.value == "hysteretic"

    def test_control_modes(self):
        """Test control modes."""
        assert ControlMode.VOLTAGE_MODE.value == "voltage_mode"
        assert ControlMode.CURRENT_MODE.value == "current_mode"

    def test_modulation_serialization(self):
        """Test modulation dict conversion."""
        mod = TASModulation(
            type=ModulationType.PWM,
            control_mode=ControlMode.CURRENT_MODE,
            max_duty=0.85,
        )
        d = mod.to_dict()
        assert d["type"] == "pwm"
        assert d["control_mode"] == "current_mode"
        mod2 = TASModulation.from_dict(d)
        assert mod2.type == ModulationType.PWM


class TestInputs:
    """Test input classes."""

    def test_requirements(self):
        """Test requirements creation."""
        req = TASRequirements(
            v_in_min=10.0,
            v_in_max=14.0,
            v_out=5.0,
            i_out_max=3.0,
        )
        d = req.to_dict()
        assert d["v_in_min"] == 10.0
        req2 = TASRequirements.from_dict(d)
        assert req2.v_in_max == 14.0

    def test_operating_point(self):
        """Test operating point with waveforms."""
        op = TASOperatingPoint(
            name="full_load",
            frequency=500e3,
            duty_cycle=0.4,
            mode=OperatingMode.CCM,
            modulation=TASModulation(type=ModulationType.PWM),
            waveforms={"i_L": TASWaveform.triangular(2.5, 3.5, 0.4, 2e-6)},
        )
        d = op.to_dict()
        assert d["frequency"] == 500e3
        assert "waveforms" in d
        op2 = TASOperatingPoint.from_dict(d)
        assert op2.duty_cycle == 0.4


class TestOutputs:
    """Test output classes."""

    def test_loss_breakdown(self):
        """Test loss breakdown."""
        losses = TASLossBreakdown(
            core_loss=0.5,
            winding_loss=0.3,
            switch_conduction=0.1,
            switch_switching=0.2,
        )
        assert losses.total == 1.1
        d = losses.to_dict()
        assert d["total"] == 1.1

    def test_kpis(self):
        """Test KPI creation."""
        kpis = TASKPIs(efficiency=0.92, power_density=5.0)
        d = kpis.to_dict()
        assert d["efficiency"] == 0.92
        kpis2 = TASKPIs.from_dict(d)
        assert kpis2.power_density == 5.0


class TestDocument:
    """Test TASDocument class."""

    def test_document_creation(self):
        """Test basic document creation."""
        doc = TASDocument(
            metadata=TASMetadata(name="Test Buck"),
            inputs=TASInputs(
                requirements=TASRequirements(v_in_min=10, v_in_max=14, v_out=5),
                operating_points=[TASOperatingPoint(frequency=500e3)],
            ),
        )
        assert doc.metadata.name == "Test Buck"
        d = doc.to_dict()
        assert "metadata" in d
        assert "inputs" in d

    def test_document_json_roundtrip(self):
        """Test JSON serialization."""
        doc = TASDocument(
            metadata=TASMetadata(name="Test"),
            inputs=TASInputs(
                requirements=TASRequirements(v_out=12.0),
            ),
        )
        json_str = doc.to_json()
        doc2 = TASDocument.from_json(json_str)
        assert doc2.metadata.name == "Test"
        assert doc2.inputs.requirements.v_out == 12.0


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_buck(self):
        """Test buck converter factory."""
        doc = create_buck_tas(
            name="Test Buck",
            v_in_min=10,
            v_in_max=14,
            v_out=5,
            i_out=3,
            frequency=500e3,
        )
        assert doc.metadata.name == "Test Buck"
        assert doc.inputs.requirements.v_out == 5
        assert len(doc.inputs.operating_points) == 1

    def test_create_boost(self):
        """Test boost converter factory."""
        doc = create_boost_tas(
            name="Test Boost",
            v_in_min=4.5,
            v_in_max=5.5,
            v_out=12,
            i_out=1,
            frequency=300e3,
        )
        assert doc.metadata.name == "Test Boost"
        assert doc.inputs.requirements.v_out == 12

    def test_create_flyback(self):
        """Test flyback converter factory."""
        doc = create_flyback_tas(
            name="Test Flyback",
            v_in_min=36,
            v_in_max=60,
            v_out=12,
            i_out=2,
            frequency=100e3,
            turns_ratio=4,
        )
        assert doc.metadata.name == "Test Flyback"
        assert doc.inputs.requirements.isolation_voltage == 1500.0


class TestExampleFiles:
    """Test loading example JSON files."""

    EXAMPLES_DIR = Path(__file__).parent.parent / "tas" / "examples"

    @pytest.mark.parametrize("filename", [
        "buck_12v_to_5v.json",
        "boost_5v_to_12v.json",
        "buck_boost_inverting.json",
        "flyback_48v_to_12v.json",
    ])
    def test_load_example(self, filename):
        """Test loading and parsing example files."""
        filepath = self.EXAMPLES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"Example file not found: {filepath}")

        with open(filepath) as f:
            data = json.load(f)

        doc = TASDocument.from_dict(data)
        assert doc.metadata.name
        assert doc.inputs.requirements.v_out != 0

        # Verify round-trip
        d2 = doc.to_dict()
        assert d2["metadata"]["name"] == data["metadata"]["name"]
