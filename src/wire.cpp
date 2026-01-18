#include "wire.h"

namespace PyMKF {

json get_wires() {
    try {
        auto wires = OpenMagnetics::get_wires();
        json result = json::array();
        for (auto elem : wires) {
            json aux;
            to_json(aux, elem);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_wire_names() {
    try {
        auto wireNames = OpenMagnetics::get_wire_names();
        json result = json::array();
        for (auto elem : wireNames) {
            result.push_back(elem);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_wire_materials() {
    try {
        auto wireMaterials = OpenMagnetics::get_wire_materials();
        json result = json::array();
        for (auto elem : wireMaterials) {
            json aux;
            to_json(aux, elem);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_wire_material_names() {
    try {
        auto wireMaterialNames = OpenMagnetics::get_wire_material_names();
        json result = json::array();
        for (auto elem : wireMaterialNames) {
            result.push_back(elem);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json find_wire_by_name(json wireName) {
    try {
        auto wireData = OpenMagnetics::find_wire_by_name(wireName);
        json result;
        to_json(result, wireData);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json find_wire_material_by_name(json wireMaterialName) {
    try {
        auto wireMaterialData = OpenMagnetics::find_wire_material_by_name(wireMaterialName);
        json result;
        to_json(result, wireMaterialData);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json find_wire_by_dimension(double dimension, json wireTypeJson, json wireStandardJson) {
    try {
        WireType wireType;
        from_json(wireTypeJson, wireType);
        WireStandard wireStandard;
        from_json(wireStandardJson, wireStandard);
        auto wireMaterialData = OpenMagnetics::find_wire_by_dimension(dimension, wireType, wireStandard, false);
        json result;
        to_json(result, wireMaterialData);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_wire_data(json windingDataJson) {
    OpenMagnetics::Winding winding(windingDataJson);
    auto wire = OpenMagnetics::Coil::resolve_wire(winding);
    json result;
    to_json(result, wire);
    return result;
}

json get_wire_data_by_name(std::string name) {
    auto wireData = OpenMagnetics::find_wire_by_name(name);
    json result;
    to_json(result, wireData);
    return result;
}

json get_wire_data_by_standard_name(std::string standardName) {
    auto wires = OpenMagnetics::get_wires();
    for (auto wire : wires) {
        if (!wire.get_standard_name()) {
            continue;
        }
        if (wire.get_standard_name().value() == standardName) {
            auto coating = wire.resolve_coating();
            if (!coating) {
                continue;
            }
            if (!coating->get_grade()) {
                continue;
            }
            // Hardcoded
            if (coating->get_grade().value() == 1) {
                json result;
                to_json(result, wire);
                return result;
            }
        }
    }

    json result;
    result["errorMessage"] = "Wire not found by standard name";
    return result;
}

json get_strand_by_standard_name(std::string standardName) {
    auto wires = OpenMagnetics::get_wires();
    for (auto wire : wires) {
        if (!wire.get_standard_name()) {
            continue;
        }
        auto coating = wire.resolve_coating();
        if (!coating) {
            continue;
        }
        // We are looking for enamelled wires for strands
        if (coating->get_type() != InsulationWireCoatingType::ENAMELLED) {
            continue;
        }

        if (!coating->get_grade()) {
            throw std::runtime_error("Missing grade");
        }

        if (wire.get_standard_name().value() == standardName && coating->get_grade().value() == 1) {
            json result;
            to_json(result, wire);
            return result;
        }
    }

    json result;
    result["errorMessage"] = "Wire not found by standard name";
    return result;
}

double get_wire_conducting_diameter_by_standard_name(std::string standardName) {
    auto wires = OpenMagnetics::get_wires();
    for (auto wire : wires) {
        if (!wire.get_standard_name()) {
            continue;
        }
        if (wire.get_standard_name().value() == standardName) {
            return OpenMagnetics::resolve_dimensional_values(wire.get_conducting_diameter().value());
        }
    }
    return -1;
}

double get_wire_outer_width_rectangular(double conductingWidth, int grade, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_width_rectangular(conductingWidth, grade, wireStandard);
}

double get_wire_outer_height_rectangular(double conductingHeight, int grade, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_height_rectangular(conductingHeight, grade, wireStandard);
}

double get_wire_outer_diameter_bare_litz(double conductingDiameter, int numberConductors, int grade, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_diameter_bare_litz(conductingDiameter, numberConductors, grade, wireStandard);
}

double get_wire_outer_diameter_served_litz(double conductingDiameter, int numberConductors, int grade, int numberLayers, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_diameter_served_litz(conductingDiameter, numberConductors, grade, numberLayers, wireStandard);
}

double get_wire_outer_diameter_insulated_litz(double conductingDiameter, int numberConductors, int numberLayers, double thicknessLayers, int grade, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_diameter_insulated_litz(conductingDiameter, numberConductors, numberLayers, thicknessLayers, grade, wireStandard);
}

double get_wire_outer_diameter_enamelled_round(double conductingDiameter, int grade, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_diameter_round(conductingDiameter, grade, wireStandard);
}

double get_wire_outer_diameter_insulated_round(double conductingDiameter, int numberLayers, double thicknessLayers, json wireStandardJson) {
    WireStandard wireStandard;
    from_json(wireStandardJson, wireStandard);
    return OpenMagnetics::Wire::get_outer_diameter_round(conductingDiameter, numberLayers, thicknessLayers, wireStandard);
}

std::vector<double> get_outer_dimensions(json wireJson) {
    OpenMagnetics::Wire wire(wireJson);
    return {wire.get_maximum_outer_width(), wire.get_maximum_outer_height()};
}

json get_equivalent_wire(json oldWireJson, json newWireTypeJson, double effectivefrequency) {
    try {
        OpenMagnetics::Wire oldWire(oldWireJson);
        WireType newWireType;
        from_json(newWireTypeJson, newWireType);

        auto newWire = OpenMagnetics::Wire::get_equivalent_wire(oldWire, newWireType, effectivefrequency);

        json result;
        to_json(result, newWire);
        return result;
    }
    catch (const std::exception &exc) {
        std::cout << std::string{exc.what()} << std::endl;
        return "Exception: " + std::string{exc.what()};
    }
}

json get_coating(json wireJson) {
    try {
        OpenMagnetics::Wire wire(wireJson);
        InsulationWireCoating insulationWireCoating;
        if (wire.resolve_coating()) {
            insulationWireCoating = wire.resolve_coating().value();
        }
        else {
            insulationWireCoating.set_type(InsulationWireCoatingType::BARE);
        }
        json result;
        to_json(result, insulationWireCoating);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json get_coating_label(json wireJson) {
    try {
        OpenMagnetics::Wire wire(wireJson);
        auto coatingLabel = wire.encode_coating_label();
        return coatingLabel;
    }
    catch(const std::runtime_error& re) {
        return "Exception: " + std::string{re.what()};
    }
    catch(const std::exception& ex) {
        return "Exception: " + std::string{ex.what()};
    }
    catch(...) {
        return "Unknown failure occurred. Possible memory corruption";
    }
}

json get_wire_coating_by_label(std::string label) {
    auto wires = OpenMagnetics::get_wires();
    InsulationWireCoating insulationWireCoating;
    for (auto wire : wires) {
        auto coatingLabel = wire.encode_coating_label();
        if (coatingLabel == label) {
            if (wire.resolve_coating()) {
                insulationWireCoating = wire.resolve_coating().value();
            }
            else {
                insulationWireCoating.set_type(InsulationWireCoatingType::BARE);
            }
            break;
        }
    }
    json result;
    to_json(result, insulationWireCoating);
    return result;
}

std::vector<std::string> get_coating_labels_by_type(json wireTypeJson) {
    WireType wireType(wireTypeJson);

    auto wires = OpenMagnetics::get_wires(wireType);

    std::vector<std::string> coatingLabels;
    for (auto wire : wires) {
        auto coatingLabel = wire.encode_coating_label();
        if (std::find(coatingLabels.begin(), coatingLabels.end(), coatingLabel) == coatingLabels.end()) {
            coatingLabels.push_back(coatingLabel);
        }
    }

    return coatingLabels;
}

double get_coating_thickness(json wireJson) {
    try {
        OpenMagnetics::Wire wire(wireJson);
        return wire.get_coating_thickness();
    }
    catch (const std::exception &exc) {
        std::cout << std::string{exc.what()} << std::endl;
        return -1;
    }
}

double get_coating_relative_permittivity(json wireJson) {
    try {
        OpenMagnetics::Wire wire(wireJson);
        return wire.get_coating_relative_permittivity();
    }
    catch (const std::exception &exc) {
        std::cout << std::string{exc.what()} << std::endl;
        return -1;
    }
}

json get_coating_insulation_material(json wireJson) {
    try {
        OpenMagnetics::Wire wire(wireJson);
        OpenMagnetics::InsulationMaterial material;

        try {
            material = wire.resolve_coating_insulation_material();
        }
        catch (const std::exception &e) {
            if (std::string{e.what()} == "Coating is missing material information") {
                material = OpenMagnetics::find_insulation_material_by_name(OpenMagnetics::defaults.defaultEnamelledInsulationMaterial);
            }
        }

        json result;
        to_json(result, material);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

std::vector<std::string> get_available_wires() {
    return OpenMagnetics::get_wire_names();
}

std::vector<std::string> get_unique_wire_diameters(json wireStandardJson) {
    WireStandard wireStandard(wireStandardJson);

    auto wires = OpenMagnetics::get_wires(WireType::ROUND, wireStandard);

    std::vector<std::string> uniqueStandardName;
    for (auto wire : wires) {
        if (!wire.get_standard_name()) {
            continue;
        }
        auto standardName = wire.get_standard_name().value();
        if (std::find(uniqueStandardName.begin(), uniqueStandardName.end(), standardName) == uniqueStandardName.end()) {
            uniqueStandardName.push_back(standardName);
        }
    }

    return uniqueStandardName;
}

std::vector<std::string> get_available_wire_types() {
    std::vector<std::string> wireTypes;

    for (auto [value, name] : magic_enum::enum_entries<WireType>()) {
        json wireTypeJson;
        if (value == WireType::PLANAR) {
            // TODO Add support for planar
            continue;
        }
        to_json(wireTypeJson, value);
        wireTypes.push_back(wireTypeJson);
    }

    return wireTypes;
}

std::vector<std::string> get_available_wire_standards() {
    std::vector<std::string> wireStandards;

    for (auto [value, name] : magic_enum::enum_entries<WireStandard>()) {
        json wireStandardJson;
        to_json(wireStandardJson, value);
        wireStandards.push_back(wireStandardJson);
    }

    return wireStandards;
}

void register_wire_bindings(py::module& m) {
    // Wires and materials
    m.def("get_wires", &get_wires,
        R"pbdoc(
        Retrieve all available wires from the database.
        
        Returns complete wire specifications including:
        - Type (round, litz, rectangular, foil)
        - Conductor dimensions
        - Coating/insulation properties
        - Standard designation
        
        Returns:
            JSON array of Wire objects.
        )pbdoc");
    
    m.def("get_wire_materials", &get_wire_materials,
        R"pbdoc(
        Retrieve all available wire conductor materials.
        
        Returns material properties including:
        - Resistivity vs temperature
        - Density
        - Standard designations
        
        Returns:
            JSON array of WireMaterial objects (copper, aluminum, etc.).
        )pbdoc");
    
    m.def("get_wire_names", &get_wire_names,
        R"pbdoc(
        Retrieve list of all wire names in database.
        
        Returns:
            JSON array of wire name strings.
        )pbdoc");
    
    m.def("get_wire_material_names", &get_wire_material_names,
        R"pbdoc(
        Retrieve list of all wire material names.
        
        Returns:
            JSON array of material name strings.
        )pbdoc");

    // Lookup functions
    m.def("find_wire_by_name", &find_wire_by_name,
        R"pbdoc(
        Find complete wire data by name.
        
        Args:
            name: Wire name (e.g., "Round 0.5 - Grade 1").
        
        Returns:
            JSON Wire object with full specification.
        )pbdoc",
        py::arg("name"));
    
    m.def("find_wire_material_by_name", &find_wire_material_by_name,
        R"pbdoc(
        Find wire conductor material data by name.
        
        Args:
            name: Material name (e.g., "copper", "aluminum").
        
        Returns:
            JSON WireMaterial object.
        )pbdoc",
        py::arg("name"));
    
    m.def("find_wire_by_dimension", &find_wire_by_dimension,
        R"pbdoc(
        Find wire by dimension, type, and standard.
        
        Searches for the closest matching wire in the database.
        
        Args:
            dimension: Target dimension in meters (diameter for round wire).
            wire_type_json: Wire type ("round", "litz", "rectangular", "foil").
            wire_standard_json: Standard ("IEC 60317", "NEMA MW 1000", etc.).
        
        Returns:
            JSON Wire object matching criteria.
        )pbdoc",
        py::arg("dimension"), py::arg("wire_type_json"), py::arg("wire_standard_json"));

    // Wire data functions
    m.def("get_wire_data", &get_wire_data,
        R"pbdoc(
        Get complete wire data from winding specification.
        
        Resolves wire reference to full wire data.
        
        Args:
            winding_data_json: JSON Winding object with wire field.
        
        Returns:
            JSON Wire object with complete specification.
        )pbdoc",
        py::arg("winding_data_json"));
    
    m.def("get_wire_data_by_name", &get_wire_data_by_name,
        R"pbdoc(
        Get wire data by name.
        
        Args:
            name: Wire name string.
        
        Returns:
            JSON Wire object.
        )pbdoc",
        py::arg("name"));
    
    m.def("get_wire_data_by_standard_name", &get_wire_data_by_standard_name,
        R"pbdoc(
        Get wire data by standard designation (e.g., AWG or IEC size).
        
        Args:
            standard_name: Standard wire size (e.g., "AWG 24", "0.50 mm").
        
        Returns:
            JSON Wire object.
        )pbdoc",
        py::arg("standard_name"));
    
    m.def("get_strand_by_standard_name", &get_strand_by_standard_name,
        R"pbdoc(
        Get strand wire data by standard name (for litz wire strands).
        
        Args:
            standard_name: Strand size designation.
        
        Returns:
            JSON Wire object for individual strand.
        )pbdoc",
        py::arg("standard_name"));
    
    m.def("get_wire_conducting_diameter_by_standard_name", &get_wire_conducting_diameter_by_standard_name,
        R"pbdoc(
        Get bare conductor diameter by standard name.
        
        Args:
            standard_name: Wire size designation.
        
        Returns:
            Conducting diameter in meters.
        )pbdoc",
        py::arg("standard_name"));

    // Wire dimensions
    m.def("get_wire_outer_width_rectangular", &get_wire_outer_width_rectangular,
        R"pbdoc(
        Get total outer width of rectangular wire including insulation.
        
        Args:
            conducting_width: Conductor width in meters.
            grade: Insulation grade (1, 2, 3).
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Outer width in meters.
        )pbdoc",
        py::arg("conducting_width"), py::arg("grade"), py::arg("wire_standard_json"));
    
    m.def("get_wire_outer_height_rectangular", &get_wire_outer_height_rectangular,
        R"pbdoc(
        Get total outer height of rectangular wire including insulation.
        
        Args:
            conducting_height: Conductor height in meters.
            grade: Insulation grade (1, 2, 3).
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Outer height in meters.
        )pbdoc",
        py::arg("conducting_height"), py::arg("grade"), py::arg("wire_standard_json"));
    
    m.def("get_wire_outer_diameter_bare_litz", &get_wire_outer_diameter_bare_litz,
        R"pbdoc(
        Get outer diameter of bare litz bundle (no serving).
        
        Args:
            conducting_diameter: Strand conductor diameter in meters.
            number_conductors: Number of strands in bundle.
            grade: Strand insulation grade (1, 2, 3).
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Bundle diameter in meters.
        )pbdoc",
        py::arg("conducting_diameter"), py::arg("number_conductors"), py::arg("grade"), py::arg("wire_standard_json"));
    
    m.def("get_wire_outer_diameter_served_litz", &get_wire_outer_diameter_served_litz,
        R"pbdoc(
        Get outer diameter of litz wire with serving.
        
        Args:
            conducting_diameter: Strand conductor diameter in meters.
            number_conductors: Number of strands in bundle.
            grade: Strand insulation grade (1, 2, 3).
            number_layers: Number of serving layers.
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Served diameter in meters.
        )pbdoc",
        py::arg("conducting_diameter"), py::arg("number_conductors"), py::arg("grade"), py::arg("number_layers"), py::arg("wire_standard_json"));
    
    m.def("get_wire_outer_diameter_insulated_litz", &get_wire_outer_diameter_insulated_litz,
        R"pbdoc(
        Get outer diameter of fully insulated litz wire.
        
        Args:
            conducting_diameter: Strand conductor diameter in meters.
            number_conductors: Number of strands in bundle.
            number_layers: Number of insulation layers.
            thickness_layers: Thickness per insulation layer in meters.
            grade: Strand insulation grade (1, 2, 3).
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Insulated diameter in meters.
        )pbdoc",
        py::arg("conducting_diameter"), py::arg("number_conductors"), py::arg("number_layers"), py::arg("thickness_layers"), py::arg("grade"), py::arg("wire_standard_json"));
    
    m.def("get_wire_outer_diameter_enamelled_round", &get_wire_outer_diameter_enamelled_round,
        R"pbdoc(
        Get outer diameter of enamelled round wire.
        
        Includes conductor plus enamel coating.
        
        Args:
            conducting_diameter: Conductor diameter in meters.
            grade: Insulation grade (1, 2, 3).
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Outer diameter in meters.
        )pbdoc",
        py::arg("conducting_diameter"), py::arg("grade"), py::arg("wire_standard_json"));
    
    m.def("get_wire_outer_diameter_insulated_round", &get_wire_outer_diameter_insulated_round,
        R"pbdoc(
        Get outer diameter of insulated round wire.
        
        Includes all insulation layers.
        
        Args:
            conducting_diameter: Conductor diameter in meters.
            number_layers: Number of insulation layers.
            thickness_layers: Thickness per insulation layer in meters.
            wire_standard_json: Wire standard (e.g., "IEC 60317").
        
        Returns:
            Outer diameter in meters.
        )pbdoc",
        py::arg("conducting_diameter"), py::arg("number_layers"), py::arg("thickness_layers"), py::arg("wire_standard_json"));
    
    m.def("get_outer_dimensions", &get_outer_dimensions,
        R"pbdoc(
        Get outer dimensions of any wire type.
        
        Universal function that handles all wire types.
        
        Args:
            wire_json: JSON Wire object.
        
        Returns:
            JSON array of dimensions [width, height] or [diameter] in meters.
        )pbdoc",
        py::arg("wire_json"));

    // Wire utilities
    m.def("get_equivalent_wire", &get_equivalent_wire,
        R"pbdoc(
        Get equivalent wire for comparison or substitution.
        
        Finds a wire with similar electrical characteristics.
        
        Args:
            old_wire_json: JSON Wire object to find equivalent for.
            new_wire_type_json: Target wire type ("round", "litz", etc.).
            effective_frequency: Operating frequency in Hz.
        
        Returns:
            JSON Wire object representing equivalent.
        )pbdoc",
        py::arg("old_wire_json"), py::arg("new_wire_type_json"), py::arg("effective_frequency"));
    
    m.def("get_coating", &get_coating,
        R"pbdoc(
        Get coating/insulation data for a wire.
        
        Args:
            wire_json: JSON Wire object.
        
        Returns:
            JSON WireCoating object.
        )pbdoc",
        py::arg("wire_json"));
    
    m.def("get_coating_label", &get_coating_label,
        R"pbdoc(
        Get human-readable coating label for a wire.
        
        Args:
            wire_json: JSON Wire object.
        
        Returns:
            Coating label string (e.g., "Grade 1", "Triple Insulated").
        )pbdoc",
        py::arg("wire_json"));
    
    m.def("get_wire_coating_by_label", &get_wire_coating_by_label,
        R"pbdoc(
        Get wire coating specification by label.
        
        Args:
            label: Coating label string.
        
        Returns:
            JSON WireCoating object.
        )pbdoc",
        py::arg("label"));
    
    m.def("get_coating_labels_by_type", &get_coating_labels_by_type,
        R"pbdoc(
        Get available coating labels for a wire type.
        
        Args:
            wire_type_json: Wire type.
        
        Returns:
            List of available coating label strings.
        )pbdoc",
        py::arg("wire_type_json"));
    
    m.def("get_coating_thickness", &get_coating_thickness,
        R"pbdoc(
        Get thickness of wire coating/insulation.
        
        Args:
            wire_json: JSON Wire object.
        
        Returns:
            Coating thickness in meters.
        )pbdoc",
        py::arg("wire_json"));
    
    m.def("get_coating_relative_permittivity", &get_coating_relative_permittivity,
        R"pbdoc(
        Get relative permittivity (dielectric constant) of coating.
        
        Used for stray capacitance calculations.
        
        Args:
            wire_json: JSON Wire object.
        
        Returns:
            Relative permittivity (dimensionless).
        )pbdoc",
        py::arg("wire_json"));
    
    m.def("get_coating_insulation_material", &get_coating_insulation_material,
        R"pbdoc(
        Get insulation material of wire coating.
        
        Args:
            wire_json: JSON Wire object.
        
        Returns:
            JSON InsulationMaterial object.
        )pbdoc",
        py::arg("wire_json"));

    // Availability queries
    m.def("get_available_wires", &get_available_wires,
        R"pbdoc(
        Get list of all available wire names.
        
        Returns:
            List of wire name strings.
        )pbdoc");
    
    m.def("get_unique_wire_diameters", &get_unique_wire_diameters,
        R"pbdoc(
        Get list of unique wire diameters for a standard.
        
        Useful for wire selection UI.
        
        Args:
            wire_standard_json: Wire standard to query.
        
        Returns:
            List of standard size designation strings.
        )pbdoc",
        py::arg("wire_standard_json"));
    
    m.def("get_available_wire_types", &get_available_wire_types,
        R"pbdoc(
        Get list of available wire types.
        
        Returns:
            List of type strings: "round", "litz", "rectangular", "foil".
        )pbdoc");
    
    m.def("get_available_wire_standards", &get_available_wire_standards,
        R"pbdoc(
        Get list of available wire standards.
        
        Returns:
            List of standard strings: "IEC 60317", "NEMA MW 1000", etc.
        )pbdoc");
}

} // namespace PyMKF
