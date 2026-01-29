"""
Tests for PyOpenMagnetics wire functions (extended coverage).

Covers wire lookup, wire dimensions, coating data, and wire type/standard
availability. Note: diameter functions take scalar args, not wire dicts.
"""
import pytest
import PyOpenMagnetics


class TestWireLookup:
    """Test wire lookup and search functions."""

    def test_find_wire_by_name(self):
        """Find wire by exact name."""
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        assert isinstance(wire, dict)
        assert "type" in wire

    def test_find_wire_by_dimension_round(self):
        """Find round wire closest to given dimension."""
        wire = PyOpenMagnetics.find_wire_by_dimension(0.0005, "round", "IEC 60317")
        assert isinstance(wire, dict)

    def test_find_wire_from_database(self):
        """Find first wire from database by name."""
        names = PyOpenMagnetics.get_wire_names()
        assert len(names) > 0
        wire = PyOpenMagnetics.find_wire_by_name(names[0])
        assert isinstance(wire, dict)

    def test_find_wire_has_type_field(self):
        """Wire should have type information."""
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        assert "type" in wire

    def test_wire_names_are_strings(self):
        """All wire names should be strings."""
        names = PyOpenMagnetics.get_wire_names()
        assert all(isinstance(n, str) for n in names)


class TestWireDiameters:
    """Test wire outer diameter calculation functions.

    These functions take scalar arguments (diameter, grade, standard), not wire dicts.
    """

    def test_enamelled_round_diameter(self):
        """Get outer diameter for enamelled round wire."""
        result = PyOpenMagnetics.get_wire_outer_diameter_enamelled_round(0.0005, 1, "IEC 60317")
        assert isinstance(result, float)
        assert result > 0

    def test_enamelled_larger_than_bare(self):
        """Enamelled diameter should be larger than bare conductor."""
        enamelled = PyOpenMagnetics.get_wire_outer_diameter_enamelled_round(0.0005, 1, "IEC 60317")
        assert enamelled > 0.0005

    def test_enamelled_grade_2_larger_than_grade_1(self):
        """Grade 2 enamel should be thicker than grade 1."""
        grade_1 = PyOpenMagnetics.get_wire_outer_diameter_enamelled_round(0.0005, 1, "IEC 60317")
        grade_2 = PyOpenMagnetics.get_wire_outer_diameter_enamelled_round(0.0005, 2, "IEC 60317")
        assert grade_2 >= grade_1

    def test_outer_dimensions_round_wire(self):
        """Get outer dimensions for round wire."""
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        result = PyOpenMagnetics.get_outer_dimensions(wire)
        assert result is not None

    def test_bare_litz_diameter(self):
        """Get bare litz wire diameter."""
        if not hasattr(PyOpenMagnetics, "get_wire_outer_diameter_bare_litz"):
            pytest.skip("get_wire_outer_diameter_bare_litz not available")
        # Typical litz: 10 strands of 0.1mm
        result = PyOpenMagnetics.get_wire_outer_diameter_bare_litz(0.0001, 10, 1, "IEC 60317")
        assert isinstance(result, float)
        assert result > 0


class TestWireCoating:
    """Test wire coating and insulation data functions."""

    def test_get_coating(self):
        """Get coating information for wire."""
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        result = PyOpenMagnetics.get_coating(wire)
        assert isinstance(result, dict)

    def test_coating_has_data(self):
        """Coating info should contain some data."""
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        result = PyOpenMagnetics.get_coating(wire)
        assert len(result) > 0

    def test_get_coating_label(self):
        """Get coating label for wire."""
        if not hasattr(PyOpenMagnetics, "get_coating_label"):
            pytest.skip("get_coating_label not available")
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        result = PyOpenMagnetics.get_coating_label(wire)
        assert isinstance(result, str)

    def test_get_coating_thickness(self):
        """Get coating thickness for wire."""
        if not hasattr(PyOpenMagnetics, "get_coating_thickness"):
            pytest.skip("get_coating_thickness not available")
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
        result = PyOpenMagnetics.get_coating_thickness(wire)
        assert isinstance(result, (int, float))


class TestWireAvailability:
    """Test wire type and standard availability functions."""

    def test_get_available_wire_types(self):
        """Get list of available wire types."""
        types = PyOpenMagnetics.get_available_wire_types()
        assert isinstance(types, list)
        assert len(types) > 0

    def test_wire_types_include_round(self):
        """Wire types should include 'round'."""
        types = PyOpenMagnetics.get_available_wire_types()
        types_lower = [t.lower() for t in types]
        assert "round" in types_lower

    def test_get_available_wire_standards(self):
        """Get list of available wire standards."""
        standards = PyOpenMagnetics.get_available_wire_standards()
        assert isinstance(standards, list)
        assert len(standards) > 0

    def test_wire_database_not_empty(self):
        """Wire database should have entries."""
        wires = PyOpenMagnetics.get_wires()
        assert isinstance(wires, list)
        assert len(wires) > 0

    def test_wires_have_consistent_types(self):
        """All wires should have a type field."""
        wires = PyOpenMagnetics.get_wires()
        for wire in wires[:10]:
            assert "type" in wire, f"Wire missing 'type': {wire.get('name', 'unknown')}"

    def test_get_unique_wire_diameters(self):
        """Get unique wire conducting diameters for a standard."""
        if not hasattr(PyOpenMagnetics, "get_unique_wire_diameters"):
            pytest.skip("get_unique_wire_diameters not available")
        result = PyOpenMagnetics.get_unique_wire_diameters("IEC 60317")
        assert isinstance(result, list)
        assert len(result) > 0


class TestWireMaterials:
    """Test wire material data access."""

    def test_get_wire_materials(self):
        """Wire materials should be retrievable."""
        if not hasattr(PyOpenMagnetics, "get_wire_materials"):
            pytest.skip("get_wire_materials not available")
        materials = PyOpenMagnetics.get_wire_materials()
        assert isinstance(materials, list)

    def test_get_wire_material_names(self):
        """Wire material names should be retrievable."""
        if not hasattr(PyOpenMagnetics, "get_wire_material_names"):
            pytest.skip("get_wire_material_names not available")
        names = PyOpenMagnetics.get_wire_material_names()
        assert isinstance(names, list)

    def test_find_wire_material_by_name(self):
        """Should find wire material by name."""
        if not hasattr(PyOpenMagnetics, "get_wire_material_names"):
            pytest.skip("get_wire_material_names not available")
        names = PyOpenMagnetics.get_wire_material_names()
        if len(names) > 0:
            material = PyOpenMagnetics.find_wire_material_by_name(names[0])
            assert isinstance(material, dict)
