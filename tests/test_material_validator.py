"""Magnetic Blade Runner (MKF MaterialValidator) through the Python binding."""
import copy

import pytest
import PyOpenMagnetics


def _material(name):
    return PyOpenMagnetics.get_material_data(name)


def test_real_power_ferrite_is_clean():
    verdict = PyOpenMagnetics.validate_material(_material("N87"))
    assert verdict["valid"] is True
    assert verdict["findings"] == []
    assert verdict["materialClass"] == "MnZn power ferrite"


def test_saturation_above_iron_is_impossible():
    record = copy.deepcopy(_material("N87"))
    record["name"] = "N87 Bs 3 T"
    record["saturation"][0]["magneticFluxDensity"] = 3.0
    verdict = PyOpenMagnetics.validate_material(record)
    assert verdict["valid"] is False
    assert any(f["code"] == "MAT_BSAT_CEILING" and f["severity"] == "IMPOSSIBLE" for f in verdict["findings"])


def test_extra_points_hysteresis_bound():
    points = [{"frequency": 1e3, "magneticFluxDensityPeak": 0.05, "temperature": 25,
               "volumetricLosses": 80e3, "origin": "manufacturer"}]
    verdict = PyOpenMagnetics.validate_material(_material("P63"), points)
    assert any(f["code"] == "MAT_LOSS_HYSTERESIS_BOUND" for f in verdict["findings"])


def test_embedded_catalogue_sweep():
    summary = PyOpenMagnetics.validate_all_materials()
    assert summary["records"] > 1000
    assert len(summary["verdicts"]) == summary["records"]
    assert "findingsByCode" in summary
    assert len(summary["classTable"]) > 0
