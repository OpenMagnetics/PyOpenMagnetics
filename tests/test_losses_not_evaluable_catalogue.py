"""
A catalogue part whose core material carries no core-loss data any model can run
(`volumetricLosses: {}`, no `massLosses`) must neither abort the catalogue adviser nor vanish
from its results. Like a datasheet-only part, the loss-based filters do not apply to it (no score,
never a stand-in loss), it is ranked on the filters that do, and the result says why its losses
were not judged, in "lossesNotEvaluable".
"""
import json

import pytest

import PyOpenMagnetics

from .test_datasheet_only_catalogue import buck_inputs, modelled_part, references_of

LOSSLESS_MATERIAL = "Test Ferrite Without Loss Data"

FLOW = [
    {"filter": "Losses No Proximity", "invert": True, "log": False, "strictlyRequired": False, "weight": 1.0},
    {"filter": "Volume", "invert": True, "log": False, "strictlyRequired": False, "weight": 1.0},
]


def lossless_part(reference):
    """The modelled part, on N87 with its core-loss data removed, as MAS stores a material nobody
    has measured losses for."""
    material = PyOpenMagnetics.find_core_material_by_name("N87")
    material["name"] = LOSSLESS_MATERIAL
    material["volumetricLosses"] = {}
    material.pop("massLosses", None)
    part = modelled_part(reference)
    part["core"]["functionalDescription"]["material"] = material
    return part


@pytest.fixture
def catalogue(tmp_path):
    PyOpenMagnetics.clear_magnetic_cache()
    path = tmp_path / "catalogue.ndjson"
    parts = [modelled_part("NORMAL-A"), lossless_part("LOSSLESS"), modelled_part("NORMAL-B")]
    path.write_text("\n".join(json.dumps(part) for part in parts) + "\n", encoding="utf-8")
    PyOpenMagnetics.load_magnetics_from_file(str(path), True)
    yield
    PyOpenMagnetics.clear_magnetic_cache()


def test_a_part_without_a_core_loss_model_is_ranked_and_flagged(catalogue):
    result = PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), FLOW, 10)

    assert set(references_of(result)) == {"NORMAL-A", "LOSSLESS", "NORMAL-B"}
    by_reference = {item["mas"]["magnetic"]["manufacturerInfo"]["reference"]: item for item in result["data"]}

    flagged = by_reference["LOSSLESS"]
    assert LOSSLESS_MATERIAL in flagged["lossesNotEvaluable"]
    assert "no core-loss data" in flagged["lossesNotEvaluable"]
    # Ranked only on what applies to it: no loss score, never a stand-in.
    assert "LOSSES_NO_PROXIMITY" not in flagged["scoringPerFilter"]
    assert "VOLUME" in flagged["scoringPerFilter"]

    for reference in ("NORMAL-A", "NORMAL-B"):
        assert "lossesNotEvaluable" not in by_reference[reference]
        assert "LOSSES_NO_PROXIMITY" in by_reference[reference]["scoringPerFilter"]
