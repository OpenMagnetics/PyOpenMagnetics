"""
Tests for loading a catalogue of magnetics from NDJSON (ABT #823).

The bug these pin: a 236-record common-mode-choke catalogue failed to load with the
bare string "bad optional access". Nothing named the file, the line, the part or the
field, and because records were cached as they were read, the first 77 stayed loaded
while the call reported an error -- so a caller that did not treat the return as fatal
went on answering from a third of the catalogue.
"""
import copy
import json

import pytest

import PyOpenMagnetics


# A real Wurth common-mode choke, trimmed to the fields that matter here: a named core
# shape, a named wire and a "Basic" bobbin, so the whole record resolves out of the
# reference databases.
VALID_MAGNETIC = {
    "manufacturerInfo": {"name": "Wurth Elektronik", "reference": "7446120027"},
    "core": {
        "functionalDescription": {
            "type": "toroidal",
            "material": "A064",
            "shape": "T 13.4/6.5/5.4",
            "gapping": [],
            "numberStacks": 1,
        }
    },
    "coil": {
        "bobbin": "Basic",
        "functionalDescription": [
            {
                "name": "primary",
                "numberTurns": 81,
                "numberParallels": 1,
                "isolationSide": "primary",
                "wire": "Round 0.265 - Grade 1",
            },
            {
                "name": "secondary",
                "numberTurns": 81,
                "numberParallels": 1,
                "isolationSide": "secondary",
                "wire": "Round 0.265 - Grade 1",
            },
        ],
    },
}


def magnetic(reference, **overrides):
    """A copy of the valid record under its own part number."""
    record = copy.deepcopy(VALID_MAGNETIC)
    record["manufacturerInfo"]["reference"] = reference
    record.update(overrides)
    return record


def write_ndjson(path, records):
    with open(path, "w") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    return str(path)


@pytest.fixture(autouse=True)
def empty_cache():
    """Every test starts from an empty magnetics cache."""
    PyOpenMagnetics.clear_magnetic_cache()
    yield
    PyOpenMagnetics.clear_magnetic_cache()


class TestStrictLoad:
    """load_magnetics_from_file: all or nothing, and say which record failed."""

    def test_loads_every_record(self, tmp_path):
        path = write_ndjson(tmp_path / "good.ndjson", [magnetic("A1"), magnetic("A2")])
        assert PyOpenMagnetics.load_magnetics_from_file(path, True) == "2"

    def test_blank_lines_are_skipped(self, tmp_path):
        path = tmp_path / "blanks.ndjson"
        path.write_text(
            "\n" + json.dumps(magnetic("A1")) + "\n\n   \n" + json.dumps(magnetic("A2")) + "\n"
        )
        assert PyOpenMagnetics.load_magnetics_from_file(str(path), True) == "2"

    def test_missing_file_raises_instead_of_reporting_a_count(self, tmp_path):
        missing = str(tmp_path / "not_here.ndjson")
        with pytest.raises(PyOpenMagnetics.EngineError) as error:
            PyOpenMagnetics.load_magnetics_from_file(missing, True)
        assert missing in str(error.value)

    def test_bad_record_names_the_line_and_the_part(self, tmp_path):
        # A wire that exists in neither the wire database nor the record itself: the
        # record parses, then fails to become a usable magnetic.
        broken = magnetic("B2")
        broken["coil"]["functionalDescription"][0]["wire"] = "No Such Wire In The Database"
        path = write_ndjson(tmp_path / "mixed.ndjson", [magnetic("B1"), broken, magnetic("B3")])

        with pytest.raises(PyOpenMagnetics.EngineError) as error:
            PyOpenMagnetics.load_magnetics_from_file(path, True)

        message = str(error.value)
        assert "mixed.ndjson:2" in message, message
        assert "B2" in message, message
        assert message.strip() != "bad optional access"

    def test_nothing_is_cached_when_a_record_fails(self, tmp_path):
        broken = magnetic("C2")
        broken["coil"]["functionalDescription"][0]["wire"] = "No Such Wire In The Database"
        path = write_ndjson(tmp_path / "mixed.ndjson", [magnetic("C1"), broken])
        with pytest.raises(PyOpenMagnetics.EngineError):
            PyOpenMagnetics.load_magnetics_from_file(path, True)

        # The cache size is what a load reports, so loading one known-good record tells
        # us how much of the failed batch survived: "1" means none of it did.
        good = write_ndjson(tmp_path / "good.ndjson", [magnetic("C9")])
        assert PyOpenMagnetics.load_magnetics_from_file(good, True) == "1"

    def test_malformed_json_names_the_line(self, tmp_path):
        path = tmp_path / "broken.ndjson"
        path.write_text(json.dumps(magnetic("D1")) + "\n{not json}\n")
        with pytest.raises(PyOpenMagnetics.EngineError) as error:
            PyOpenMagnetics.load_magnetics_from_file(str(path), True)
        assert "broken.ndjson:2" in str(error.value)

    def test_record_without_a_reference_says_which_field_is_missing(self, tmp_path):
        anonymous = copy.deepcopy(VALID_MAGNETIC)
        del anonymous["manufacturerInfo"]
        path = write_ndjson(tmp_path / "anonymous.ndjson", [anonymous])

        with pytest.raises(PyOpenMagnetics.EngineError) as error:
            PyOpenMagnetics.load_magnetics_from_file(path, True)

        message = str(error.value)
        assert "manufacturerInfo" in message, message
        assert "anonymous.ndjson:1" in message, message


class TestReportingLoad:
    """load_magnetics_from_file_report: keep the good records, name the dropped ones."""

    def test_keeps_the_good_records_and_reports_the_bad_one(self, tmp_path):
        broken = magnetic("E2")
        broken["coil"]["functionalDescription"][0]["wire"] = "No Such Wire In The Database"
        path = write_ndjson(
            tmp_path / "mixed.ndjson", [magnetic("E1"), broken, magnetic("E3")]
        )

        report = PyOpenMagnetics.load_magnetics_from_file_report(path, True)

        assert report["loaded"] == 2
        assert report["cacheSize"] == 2
        assert len(report["rejected"]) == 1
        rejected = report["rejected"][0]
        assert rejected["line"] == 2
        assert rejected["reference"] == "E2"
        assert rejected["reason"]

    def test_a_clean_file_reports_nothing_rejected(self, tmp_path):
        path = write_ndjson(tmp_path / "good.ndjson", [magnetic("F1"), magnetic("F2")])
        report = PyOpenMagnetics.load_magnetics_from_file_report(path, True)
        assert report["loaded"] == 2
        assert report["rejected"] == []

    def test_missing_file_still_raises(self, tmp_path):
        with pytest.raises(PyOpenMagnetics.EngineError):
            PyOpenMagnetics.load_magnetics_from_file_report(str(tmp_path / "nope.ndjson"), True)


class TestLoadFromString:
    """load_magnetics_from_string shares the file loader's contract."""

    def test_loads_every_record(self):
        text = "\n".join(json.dumps(magnetic(ref)) for ref in ("G1", "G2"))
        assert PyOpenMagnetics.load_magnetics_from_string(text) == "2"

    def test_bad_record_names_the_line_and_the_part(self):
        broken = magnetic("H2")
        broken["coil"]["functionalDescription"][0]["wire"] = "No Such Wire In The Database"
        text = json.dumps(magnetic("H1")) + "\n" + json.dumps(broken) + "\n"
        with pytest.raises(PyOpenMagnetics.EngineError) as error:
            PyOpenMagnetics.load_magnetics_from_string(text)
        message = str(error.value)
        assert ":2" in message, message
        assert "H2" in message, message

    def test_report_variant_keeps_the_good_records(self):
        broken = magnetic("I2")
        broken["coil"]["functionalDescription"][0]["wire"] = "No Such Wire In The Database"
        text = json.dumps(magnetic("I1")) + "\n" + json.dumps(broken) + "\n"
        report = PyOpenMagnetics.load_magnetics_from_string_report(text)
        assert report["loaded"] == 1
        assert [record["reference"] for record in report["rejected"]] == ["I2"]


# The exact record class that filed ABT #823: an inline custom toroid whose windings
# carry an inline wire with a conductor and a coating but no outer size, and a coil
# that therefore still has to be wound. 49 of asgard's 236 common-mode chokes look
# like this, and the first one killed the whole batch with "bad optional access".
# The outer size is derived from the conductor and its coating in MKF's
# magnetic_autocomplete; this pins that the record loads through PyOpenMagnetics.
INLINE_WIRE_MAGNETIC = {
    "manufacturerInfo": {"name": "Wurth Elektronik", "reference": "744821110"},
    "core": {
        "functionalDescription": {
            "type": "toroidal",
            "material": "A07",
            "shape": {
                "magneticCircuit": "closed",
                "type": "custom",
                "family": "t",
                "name": "T 12.7/7.92/4.9",
                "dimensions": {
                    "A": {"nominal": 0.0127},
                    "B": {"nominal": 0.00792},
                    "C": {"nominal": 0.0049},
                },
            },
            "gapping": [],
            "numberStacks": 1,
            "coating": {"type": "epoxy", "thickness": 0.0006, "material": "epoxy"},
        }
    },
    "coil": {
        "bobbin": "Basic",
        "functionalDescription": [
            {
                "name": name,
                "numberTurns": 56,
                "numberParallels": 1,
                "isolationSide": name,
                "wire": {
                    "type": "round",
                    "name": "Round 0.28 - Grade 1",
                    "conductingDiameter": {"nominal": 0.00028},
                    "coating": {"type": "enamelled", "grade": 1},
                    "material": "copper",
                },
            }
            for name in ("primary", "secondary")
        ],
    },
}


class TestInlineWireWithoutOuterSize:
    """The record class ABT #823 was filed about."""

    def test_loads(self, tmp_path):
        path = write_ndjson(tmp_path / "inline_wire.ndjson", [INLINE_WIRE_MAGNETIC])
        assert PyOpenMagnetics.load_magnetics_from_file(path, True) == "1"
