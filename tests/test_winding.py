"""
Tests for PyOpenMagnetics Winding functions.

These tests verify wire, bobbin, and insulation material retrieval.
"""
import pytest
import PyOpenMagnetics


class TestWires:
    """Wire data retrieval tests."""

    def test_get_wires_returns_list(self):
        """Wires should be returned as a list."""
        wires = PyOpenMagnetics.get_wires()
        assert isinstance(wires, list)
        assert len(wires) > 0

    def test_get_wire_names(self):
        """Wire names should be retrievable."""
        names = PyOpenMagnetics.get_wire_names()
        assert isinstance(names, list)
        assert len(names) > 0
        assert all(isinstance(name, str) for name in names)

    def test_find_wire_by_name(self):
        """Should be able to find specific wire by name."""
        names = PyOpenMagnetics.get_wire_names()
        if len(names) > 0:
            wire = PyOpenMagnetics.find_wire_by_name(names[0])
            assert isinstance(wire, dict)

    def test_wire_has_type(self):
        """Wires should have type information."""
        names = PyOpenMagnetics.get_wire_names()
        if len(names) > 0:
            wire = PyOpenMagnetics.find_wire_by_name(names[0])
            assert "type" in wire


class TestWireMaterials:
    """Test wire material data."""

    def test_get_wire_materials(self):
        """Wire materials should be retrievable."""
        materials = PyOpenMagnetics.get_wire_materials()
        assert isinstance(materials, list)

    def test_get_wire_material_names(self):
        """Wire material names should be retrievable."""
        names = PyOpenMagnetics.get_wire_material_names()
        assert isinstance(names, list)

    def test_find_wire_material_by_name(self):
        """Should be able to find wire material by name."""
        names = PyOpenMagnetics.get_wire_material_names()
        if len(names) > 0:
            material = PyOpenMagnetics.find_wire_material_by_name(names[0])
            assert isinstance(material, dict)


class TestBobbins:
    """Bobbin data tests."""

    def test_get_bobbins_returns_list(self):
        """Bobbins should be returned as a list."""
        bobbins = PyOpenMagnetics.get_bobbins()
        assert isinstance(bobbins, list)

    def test_get_bobbin_names(self):
        """Bobbin names should be retrievable."""
        names = PyOpenMagnetics.get_bobbin_names()
        assert isinstance(names, list)

    def test_find_bobbin_by_name(self):
        """Should be able to find specific bobbin by name."""
        names = PyOpenMagnetics.get_bobbin_names()
        if len(names) > 0:
            bobbin = PyOpenMagnetics.find_bobbin_by_name(names[0])
            assert isinstance(bobbin, dict)


class TestInsulationMaterials:
    """Test insulation material data."""

    def test_get_insulation_materials(self):
        """Insulation materials should be retrievable."""
        materials = PyOpenMagnetics.get_insulation_materials()
        assert isinstance(materials, list)

    def test_get_insulation_material_names(self):
        """Insulation material names should be retrievable."""
        names = PyOpenMagnetics.get_insulation_material_names()
        assert isinstance(names, list)

    def test_find_insulation_material_by_name(self):
        """Should be able to find insulation material by name."""
        names = PyOpenMagnetics.get_insulation_material_names()
        if len(names) > 0:
            material = PyOpenMagnetics.find_insulation_material_by_name(names[0])
            assert isinstance(material, dict)


class TestGuessRoundWireFromDcResistance:
    """Round-wire estimation from measured per-winding DC resistance."""

    @staticmethod
    def _current_transformer_coil(sample_toroidal_core, primary_wire, secondary_wire):
        core = PyOpenMagnetics.calculate_core_data(sample_toroidal_core, False)
        bobbin = PyOpenMagnetics.create_basic_bobbin(core, True)
        return {
            "bobbin": bobbin,
            "functionalDescription": [
                {"name": "primary", "numberTurns": 1, "numberParallels": 1,
                 "isolationSide": PyOpenMagnetics.get_isolation_side_from_index(0), "wire": primary_wire},
                {"name": "secondary", "numberTurns": 50, "numberParallels": 1,
                 "isolationSide": PyOpenMagnetics.get_isolation_side_from_index(1), "wire": secondary_wire},
            ],
        }

    def test_round_trip_recovers_dc_resistance(self, sample_toroidal_core):
        """Wires guessed from a known coil's DC resistances reproduce those resistances."""
        reference = self._current_transformer_coil(sample_toroidal_core, "Round 0.90 - Grade 1", "Round 0.212 - Grade 1")
        wound = PyOpenMagnetics.wind(reference, 1, [0.5, 0.5], [0, 1], [])
        dc_resistances = PyOpenMagnetics.calculate_dc_resistance_per_winding(wound, 25)

        # Start from the thinnest wire, as heimdall's current-transformer translator does.
        guess = self._current_transformer_coil(sample_toroidal_core, "Round 0.01 - Grade 1", "Round 0.01 - Grade 1")
        wires = PyOpenMagnetics.guess_round_wire_from_dc_resistance(guess, dc_resistances)

        assert isinstance(wires, list)
        assert len(wires) == 2
        for wire in wires:
            assert wire["type"] == "round"

        # A 1-turn primary needs a far thicker conductor than a 50-turn secondary.
        assert wires[0]["conductingDiameter"]["nominal"] > wires[1]["conductingDiameter"]["nominal"]

        guess["functionalDescription"][0]["wire"] = wires[0]
        guess["functionalDescription"][1]["wire"] = wires[1]
        rewound = PyOpenMagnetics.wind(guess, 1, [0.5, 0.5], [0, 1], [])
        recovered = PyOpenMagnetics.calculate_dc_resistance_per_winding(rewound, 25)
        for target, value in zip(dc_resistances, recovered):
            assert abs(value - target) / target < 0.05

    def test_rejects_resistance_count_mismatch(self, sample_toroidal_core):
        """One DC resistance per winding is required."""
        coil = self._current_transformer_coil(sample_toroidal_core, "Round 0.01 - Grade 1", "Round 0.01 - Grade 1")
        with pytest.raises(PyOpenMagnetics.EngineError):
            PyOpenMagnetics.guess_round_wire_from_dc_resistance(coil, [0.001])

    def test_rejects_non_positive_resistance(self, sample_toroidal_core):
        """A zero DC resistance has no wire and must not be silently mapped to one."""
        coil = self._current_transformer_coil(sample_toroidal_core, "Round 0.01 - Grade 1", "Round 0.01 - Grade 1")
        with pytest.raises(PyOpenMagnetics.EngineError):
            PyOpenMagnetics.guess_round_wire_from_dc_resistance(coil, [0.001, 0.0])
