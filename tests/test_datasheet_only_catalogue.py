"""
A catalogue may hold parts known only by their datasheet: no core, no coil, just
manufacturerInfo.datasheetInfo, which MAS allows. They must load with expansion on, be ranked
by the cache adviser on the filters that apply to them (datasheet limits, the measured L(I),
the published body size), and come back in the results rather than be dropped.

`references` restricts a search to part of a cache several callers share.
"""
import json

import pytest

import PyOpenMagnetics


def datasheet_part(reference, rated_current=3.0):
    """A 10 uH single-winding inductor known only by its datasheet."""
    return {
        "manufacturerInfo": {
            "name": "Test Maker",
            "reference": reference,
            "datasheetInfo": {
                "electrical": [
                    {
                        "subtype": "inductor",
                        "inductance": {"nominal": 10e-6},
                        "inductancePoints": [
                            {"current": 0, "inductance": 10e-6, "temperature": 20},
                            {"current": 2, "inductance": 9e-6, "temperature": 20},
                            {"current": 4, "inductance": 6e-6, "temperature": 20},
                        ],
                        "ratedCurrents": [rated_current],
                        "saturationCurrents": [{"percentInductanceDrop": 30, "current": 4.0}],
                    }
                ],
                "mechanical": {"length": {"nominal": 5e-3}, "width": {"nominal": 5e-3}, "height": {"nominal": 3e-3}},
            },
        }
    }


def buck_inputs():
    """9 uH at 1 A DC with 0.4 A ripple, 1 MHz."""
    inputs = {
        "designRequirements": {"magnetizingInductance": {"minimum": 8e-6}, "turnsRatios": []},
        "operatingPoints": [
            {
                "name": "op",
                "conditions": {"ambientTemperature": 25},
                "excitationsPerWinding": [
                    {"name": "w", "frequency": 1e6, "current": {"waveform": {"data": [0.8, 1.2, 0.8], "time": [0, 0.5e-6, 1e-6]}}}
                ],
            }
        ],
    }
    return PyOpenMagnetics.process_inputs(inputs)


FLOW = [
    {"filter": "Datasheet Limits", "invert": True, "log": False, "strictlyRequired": True, "weight": 1.0},
    {"filter": "Magnetizing Inductance", "invert": True, "log": False, "strictlyRequired": False, "weight": 1.0},
    {"filter": "Volume", "invert": True, "log": False, "strictlyRequired": False, "weight": 1.0},
    {"filter": "Losses", "invert": True, "log": False, "strictlyRequired": False, "weight": 1.0},
]


@pytest.fixture
def catalogue(tmp_path):
    PyOpenMagnetics.clear_magnetic_cache()
    path = tmp_path / "catalogue.ndjson"
    parts = [datasheet_part("ROOMY", rated_current=5.0), datasheet_part("TIGHT", rated_current=1.3), datasheet_part("OTHER")]
    path.write_text("\n".join(json.dumps(part) for part in parts) + "\n", encoding="utf-8")
    PyOpenMagnetics.load_magnetics_from_file(str(path), True)
    yield
    PyOpenMagnetics.clear_magnetic_cache()


def references_of(result):
    return [item["mas"]["magnetic"]["manufacturerInfo"]["reference"] for item in result["data"]]


def test_datasheet_only_parts_are_ranked_on_the_filters_that_apply(catalogue):
    result = PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), FLOW, 10)

    assert set(references_of(result)) == {"ROOMY", "TIGHT", "OTHER"}
    scores = result["data"][0]["scoringPerFilter"]
    assert "MAGNETIZING_INDUCTANCE" in scores and "VOLUME" in scores
    # Losses cannot judge a part with no construction: no score, never a stand-in.
    assert "LOSSES" not in scores


def test_the_part_with_more_margin_to_its_ratings_ranks_first(catalogue):
    flow = [dict(FLOW[0], strictlyRequired=False)]
    result = PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), flow, 10)
    order = references_of(result)
    assert order.index("ROOMY") < order.index("TIGHT")


def test_references_restrict_the_search(catalogue):
    result = PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), FLOW, 10, ["ROOMY", "TIGHT"])
    assert set(references_of(result)) == {"ROOMY", "TIGHT"}


def test_an_unknown_reference_raises_instead_of_searching_less(catalogue):
    with pytest.raises(Exception, match="not in the cache"):
        PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), FLOW, 10, ["ROOMY", "MISSING"])


def test_datasheet_inductance_at_a_bias():
    part = datasheet_part("P")
    assert PyOpenMagnetics.calculate_datasheet_inductance(part, 1.0, 20) == pytest.approx(9.5e-6)
    assert PyOpenMagnetics.calculate_datasheet_inductance(part, 5.0, 20) is None


def modelled_part(reference):
    """A core and a coil on public MAS data, plus the datasheet the catalogue carries."""
    part = datasheet_part(reference)
    part["core"] = {"functionalDescription": {"type": "two-piece set", "material": "N87", "shape": "E 13/7/4", "gapping": [], "numberStacks": 1}}
    part["coil"] = {"bobbin": "Basic", "functionalDescription": [{"name": "primary", "numberTurns": 10, "numberParallels": 1, "isolationSide": "primary", "wire": "Round 0.4 - Grade 1"}]}
    return part


@pytest.fixture
def mixed_catalogue(tmp_path):
    PyOpenMagnetics.clear_magnetic_cache()
    path = tmp_path / "catalogue.ndjson"
    parts = [modelled_part("BUILT"), datasheet_part("SHEET")]
    path.write_text("\n".join(json.dumps(part) for part in parts) + "\n", encoding="utf-8")
    PyOpenMagnetics.load_magnetics_from_file(str(path), True)
    yield
    PyOpenMagnetics.clear_magnetic_cache()


def test_results_can_come_back_ranked_but_unsimulated(mixed_catalogue):
    """simulate_results=False: the same ranking and scores, without a simulation per part."""
    flow = [dict(operation, strictlyRequired=False) for operation in FLOW]
    simulated = PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), flow, 10)
    ranked = PyOpenMagnetics.calculate_advised_magnetics_from_cache(buck_inputs(), flow, 10, None, False)

    assert references_of(ranked) == references_of(simulated)
    assert [item["scoringPerFilter"] for item in ranked["data"]] == [item["scoringPerFilter"] for item in simulated["data"]]
    built = references_of(simulated).index("BUILT")
    assert simulated["data"][built]["mas"].get("outputs"), "the default still simulates a modelled part"
    assert not ranked["data"][built]["mas"].get("outputs")


def test_build_datasheet_states_what_mkf_simulates_for_a_modelled_part():
    """A modelled part with no datasheet gets one from MKF: the values a catalogue datasheet
    states, computed at the given conditions, with the part's own manufacturerInfo kept."""
    part = modelled_part("BUILT")
    del part["manufacturerInfo"]["datasheetInfo"]
    info = PyOpenMagnetics.build_datasheet(buck_inputs(), PyOpenMagnetics.magnetic_autocomplete(part, {}), {})

    assert info["reference"] == "BUILT"
    electrical = info["datasheetInfo"]["electrical"][0]
    assert electrical["subtype"] == "inductor"
    for key in ("inductance", "dcResistance", "ratedCurrents", "saturationCurrentPeak", "selfResonantFrequency"):
        assert electrical.get(key) is not None, key
    assert electrical["ratedCurrents"][0] > 0 and electrical["saturationCurrentPeak"] > 0
