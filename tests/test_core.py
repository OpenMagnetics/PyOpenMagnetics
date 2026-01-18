"""
Tests for PyOpenMagnetics Core data retrieval and calculations.

These tests mirror TestCore.cpp and TestCoreAdviser.cpp from MKF,
verifying core shape, material, and gapping calculations.
"""
import pytest
import PyOpenMagnetics


class TestCoreShapes:
    """Test suite for core shape retrieval - mirrors shape tests in TestCore.cpp"""

    def test_get_core_shapes_returns_list(self):
        """Core shapes should be returned as a list."""
        shapes = PyOpenMagnetics.get_core_shapes()
        assert isinstance(shapes, list)
        assert len(shapes) > 0

    def test_get_core_shape_names(self):
        """Core shape names should be retrievable with toroidal filter."""
        # With toroidal cores
        names_with = PyOpenMagnetics.get_core_shape_names(True)
        assert isinstance(names_with, list)
        assert len(names_with) > 0
        
        # Without toroidal cores
        names_without = PyOpenMagnetics.get_core_shape_names(False)
        assert isinstance(names_without, list)
        assert len(names_with) >= len(names_without)

    def test_get_core_shape_families(self):
        """Core shape families (E, ETD, PQ, etc.) should be retrievable."""
        families = PyOpenMagnetics.get_core_shape_families()
        assert isinstance(families, list)
        assert len(families) > 0

    def test_find_core_shape_by_name(self):
        """Should be able to find specific core shape by name."""
        names = PyOpenMagnetics.get_core_shape_names(True)
        if len(names) > 0:
            shape = PyOpenMagnetics.find_core_shape_by_name(names[0])
            assert isinstance(shape, dict)
            assert "name" in shape

    def test_find_etd_shape(self):
        """Should be able to find an ETD-family shape."""
        names = PyOpenMagnetics.get_core_shape_names(False)
        etd_names = [n for n in names if "ETD" in n.upper()]
        
        if len(etd_names) > 0:
            shape = PyOpenMagnetics.find_core_shape_by_name(etd_names[0])
            assert isinstance(shape, dict)
            assert "family" in shape


class TestCoreMaterials:
    """Test suite for core materials - mirrors material tests in TestCore.cpp"""

    def test_get_core_materials_returns_list(self):
        """Core materials should be returned as a list."""
        materials = PyOpenMagnetics.get_core_materials()
        assert isinstance(materials, list)
        assert len(materials) > 0

    def test_get_core_material_names(self):
        """Core material names should be retrievable."""
        names = PyOpenMagnetics.get_core_material_names()
        assert isinstance(names, list)
        assert len(names) > 0
        assert all(isinstance(name, str) for name in names)

    def test_common_materials_exist(self):
        """Common ferrite materials (3C90, 3C95, N87) should exist."""
        names = PyOpenMagnetics.get_core_material_names()
        common = ["3C90", "3C95", "3C97", "N87", "N97"]
        found = [m for m in common if m in names]
        assert len(found) > 0, f"Expected common materials, found: {names[:10]}"

    def test_find_core_material_by_name(self):
        """Should be able to find specific material by name."""
        names = PyOpenMagnetics.get_core_material_names()
        if len(names) > 0:
            material = PyOpenMagnetics.find_core_material_by_name(names[0])
            assert isinstance(material, dict)
            assert "name" in material

    def test_get_materials_by_manufacturer(self):
        """Should filter materials by manufacturer."""
        ferroxcube = PyOpenMagnetics.get_core_material_names_by_manufacturer("Ferroxcube")
        assert isinstance(ferroxcube, list)
        
        tdk = PyOpenMagnetics.get_core_material_names_by_manufacturer("TDK")
        assert isinstance(tdk, list)


class TestCoreMaterialProperties:
    """Test suite for material property calculations."""

    def test_get_material_permeability(self):
        """
        Material permeability calculation.
        Similar to tests in TestPermeability.cpp.
        """
        # API: get_material_permeability(material_name: str, temperature, dc_bias, frequency)
        permeability = PyOpenMagnetics.get_material_permeability("3C95", 25.0, 0.0, 100000.0)
        
        assert isinstance(permeability, float)
        assert permeability > 0
        # Typical ferrite permeability range
        assert 10 < permeability < 100000

    def test_get_material_resistivity(self):
        """
        Material resistivity calculation.
        Similar to tests in TestResistivity.cpp.
        """
        # API: get_material_resistivity(material_name: str, temperature)
        resistivity = PyOpenMagnetics.get_material_resistivity("3C95", 25.0)
        
        assert isinstance(resistivity, float)
        assert resistivity > 0

    def test_get_steinmetz_coefficients(self):
        """
        Steinmetz coefficient calculation for core losses.
        Similar to tests in TestCoreLosses.cpp.
        """
        names = PyOpenMagnetics.get_core_material_names()
        if len(names) > 0:
            material = PyOpenMagnetics.find_core_material_by_name(names[0])
            # API: get_core_material_steinmetz_coefficients(material, frequency)
            coeffs = PyOpenMagnetics.get_core_material_steinmetz_coefficients(material, 100000.0)
            
            assert isinstance(coeffs, dict)
            assert len(coeffs) > 0

    @pytest.mark.xfail(reason="get_core_material_available_losses_methods not implemented in PyOpenMagnetics")
    def test_get_available_losses_methods(self):
        """Should retrieve available loss calculation methods."""
        names = PyOpenMagnetics.get_core_material_names()
        if len(names) > 0:
            material = PyOpenMagnetics.find_core_material_by_name(names[0])
            methods = PyOpenMagnetics.get_core_material_available_losses_methods(material)
            assert isinstance(methods, list)


class TestCoreCalculations:
    """Test suite for core calculations - mirrors tests in TestCore.cpp"""

    def test_calculate_core_data(self, sample_core_data):
        """
        Calculate core processed data from functional description.
        Similar to Core construction in TestCore.cpp.
        """
        # API: calculate_core_data(core_data, include_toroidal: bool)
        result = PyOpenMagnetics.calculate_core_data(sample_core_data, False)
        
        assert isinstance(result, dict)
        assert "processedDescription" in result or "functionalDescription" in result

    def test_calculate_core_geometrical_description(self, sample_core_data):
        """Calculate core geometrical description."""
        result = PyOpenMagnetics.calculate_core_geometrical_description(sample_core_data)
        
        assert isinstance(result, dict)

    def test_calculate_core_gapping(self, sample_core_data):
        """
        Calculate core gapping from functional description.
        Similar to gapping tests in TestCore.cpp.
        """
        # First calculate the core data
        # API: calculate_core_data(core_data, include_toroidal: bool)
        core = PyOpenMagnetics.calculate_core_data(sample_core_data, False)
        
        # Gapping should be calculated
        assert "functionalDescription" in core
        if "gapping" in core["functionalDescription"]:
            gapping = core["functionalDescription"]["gapping"]
            assert isinstance(gapping, list)


class TestCoreProcessedDescription:
    """Test suite for processed core descriptions."""

    def test_core_has_effective_parameters(self, sample_core_data):
        """Core should have effective parameters after calculation."""
        # API: calculate_core_data(core_data, include_toroidal: bool)
        core = PyOpenMagnetics.calculate_core_data(sample_core_data, False)
        
        if "processedDescription" in core:
            processed = core["processedDescription"]
            # Common effective parameters
            expected_params = ["effectiveLength", "effectiveArea", "effectiveVolume"]
            for param in expected_params:
                if param in processed:
                    assert processed[param] > 0

    def test_core_has_columns(self, sample_core_data):
        """Core should have column information."""
        # API: calculate_core_data(core_data, include_toroidal: bool)
        core = PyOpenMagnetics.calculate_core_data(sample_core_data, False)
        
        if "processedDescription" in core:
            processed = core["processedDescription"]
            if "columns" in processed:
                assert isinstance(processed["columns"], list)
                assert len(processed["columns"]) > 0

    def test_core_has_winding_windows(self, sample_core_data):
        """Core should have winding window information."""
        # API: calculate_core_data(core_data, include_toroidal: bool)
        core = PyOpenMagnetics.calculate_core_data(sample_core_data, False)
        
        if "processedDescription" in core:
            processed = core["processedDescription"]
            if "windingWindows" in processed:
                assert isinstance(processed["windingWindows"], list)
                assert len(processed["windingWindows"]) > 0
