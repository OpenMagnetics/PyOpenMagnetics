#include "winding.h"

namespace PyMKF {

json wind(json coilJson, size_t repetitions, json proportionPerWindingJson, json patternJson, json marginPairsJson) {
    try {
        std::vector<std::vector<double>> marginPairs;
        for (auto elem : marginPairsJson) {
            std::vector<double> vectorElem;
            for (auto value : elem) {
                vectorElem.push_back(value);
            }
            marginPairs.push_back(vectorElem);
        }

        std::vector<double> proportionPerWinding = proportionPerWindingJson;
        std::vector<size_t> pattern = patternJson;
        std::vector<OpenMagnetics::Winding> winding;
        for (auto elem : coilJson["functionalDescription"]) {
            winding.push_back(OpenMagnetics::Winding(elem));
        }
        OpenMagnetics::Coil coil;
        coil.set_bobbin(coilJson["bobbin"]);
        coil.set_functional_description(winding);
        coil.preload_margins(marginPairs);
        if (coilJson.contains("layersOrientation")) {

            if (coilJson["layersOrientation"].is_object()) {
                std::map<std::string, WindingOrientation> layersOrientationPerSection;
                for (auto [key, value] : coilJson["layersOrientation"].items()) {
                    layersOrientationPerSection[key] = value;
                }

                for (auto [sectionName, layerOrientation] : layersOrientationPerSection) {
                    coil.set_layers_orientation(layerOrientation, sectionName);
                }
            }
            else if (coilJson["layersOrientation"].is_array()) {
                coil.wind_by_sections(proportionPerWinding, pattern, repetitions);
                if (coil.get_sections_description()) {
                    auto sections = coil.get_sections_description_conduction();

                    std::vector<WindingOrientation> layersOrientationPerSection;
                    for (auto elem : coilJson["layersOrientation"]) {
                        layersOrientationPerSection.push_back(WindingOrientation(elem));
                    }

                    for (size_t sectionIndex = 0; sectionIndex < sections.size(); ++sectionIndex) {
                        if (sectionIndex < layersOrientationPerSection.size()) {
                            coil.set_layers_orientation(layersOrientationPerSection[sectionIndex], sections[sectionIndex].get_name());
                        }
                    }
                }
            }
            else {
                WindingOrientation layerOrientation(coilJson["layersOrientation"]);
                coil.set_layers_orientation(layerOrientation);

            }
        }

        if (coilJson.contains("turnsAlignment")) {
            if (coilJson["turnsAlignment"].is_object()) {
                std::map<std::string, CoilAlignment> turnsAlignmentPerSection;
                for (auto [key, value] : coilJson["turnsAlignment"].items()) {
                    turnsAlignmentPerSection[key] = value;
                }


                for (auto [sectionName, turnsAlignment] : turnsAlignmentPerSection) {
                    coil.set_turns_alignment(turnsAlignment, sectionName);
                }
            }
            else if (coilJson["turnsAlignment"].is_array()) {
                coil.wind_by_sections(proportionPerWinding, pattern, repetitions);
                if (coil.get_sections_description()) {
                    auto sections = coil.get_sections_description_conduction();

                    std::vector<CoilAlignment> turnsAlignmentPerSection;
                    for (auto elem : coilJson["turnsAlignment"]) {
                        turnsAlignmentPerSection.push_back(CoilAlignment(elem));
                    }

                    for (size_t sectionIndex = 0; sectionIndex < sections.size(); ++sectionIndex) {
                        if (sectionIndex < turnsAlignmentPerSection.size()) {
                            coil.set_turns_alignment(turnsAlignmentPerSection[sectionIndex], sections[sectionIndex].get_name());
                        }
                    }
                }
            }
            else {
                CoilAlignment turnsAlignment(coilJson["turnsAlignment"]);
                coil.set_turns_alignment(turnsAlignment);
            }
        }

        if (proportionPerWinding.size() == winding.size()) {
            if (pattern.size() > 0 && repetitions > 0) {
                coil.wind(proportionPerWinding, pattern, repetitions);
            }
            else if (repetitions > 0) {
                coil.wind(repetitions);
            }
            else {
                coil.wind();
            }
        }
        else {
            if (pattern.size() > 0 && repetitions > 0) {
                coil.wind(pattern, repetitions);
            }
            else if (repetitions > 0) {
                coil.wind(repetitions);
            }
            else {
                coil.wind();
            }
        }

        if (!coil.get_turns_description()) {
            throw std::runtime_error("Turns not created");
        }

        json result;
        to_json(result, coil);
        return result;
    }
    catch (const std::exception &exc) {
        std::cout << "coilJson" << std::endl;
        std::cout << coilJson << std::endl;
        std::cout << "repetitions" << std::endl;
        std::cout << repetitions << std::endl;
        std::cout << "proportionPerWindingJson" << std::endl;
        std::cout << proportionPerWindingJson << std::endl;
        std::cout << "patternJson" << std::endl;
        std::cout << patternJson << std::endl;
        std::cout << "marginPairsJson" << std::endl;
        std::cout << marginPairsJson << std::endl;
        return "Exception: " + std::string{exc.what()};
    }
}

json wind_planar(json coilJson, json stackUpJson, double borderToWireDistance, json wireToWireDistanceJson, json insulationThicknessJson, double coreToLayerDistance) {
    try {
        OpenMagnetics::settings.set_coil_wind_even_if_not_fit(true);
        auto coil = OpenMagnetics::Coil(coilJson, false);
        std::vector<size_t> stackUp = stackUpJson;
        std::map<std::pair<size_t, size_t>, double> insulationThickness = insulationThicknessJson.get<std::map<std::pair<size_t, size_t>, double>>();
        std::map<size_t, double> wireToWireDistance = wireToWireDistanceJson.get<std::map<size_t, double>>();

        coil.set_strict(false);
        coil.wind_planar(stackUp, borderToWireDistance, wireToWireDistance, insulationThickness, coreToLayerDistance);

        if (!coil.get_turns_description()) {
            throw std::runtime_error("Turns not created");
        }

        return coil;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json wind_by_sections(json coilJson, size_t repetitions, json proportionPerWindingJson, json patternJson, double insulationThickness) {
    try {

        std::vector<double> proportionPerWinding = proportionPerWindingJson;
        std::vector<size_t> pattern = patternJson;
        std::vector<OpenMagnetics::Winding> winding;
        for (auto elem : coilJson["functionalDescription"]) {
            winding.push_back(OpenMagnetics::Winding(elem));
        }
        OpenMagnetics::Coil coil;

        if (coilJson.contains("interleavingLevel")) {
            coil.set_interleaving_level(coilJson["interleavingLevel"]);
        }
        if (coilJson.contains("windingOrientation")) {
            coil.set_winding_orientation(coilJson["windingOrientation"]);
        }
        if (coilJson.contains("layersOrientation")) {
            coil.set_layers_orientation(coilJson["layersOrientation"]);
        }
        if (coilJson.contains("turnsAlignment")) {
            coil.set_turns_alignment(coilJson["turnsAlignment"]);
        }
        if (coilJson.contains("sectionAlignment")) {
            coil.set_section_alignment(coilJson["sectionAlignment"]);
        }

        coil.set_bobbin(coilJson["bobbin"]);
        coil.set_functional_description(winding);

        if (insulationThickness > 0) {
            coil.calculate_custom_thickness_insulation(insulationThickness);
        }

        if (proportionPerWinding.size() == winding.size()) {
            if (pattern.size() > 0 && repetitions > 0) {
                coil.wind_by_sections(proportionPerWinding, pattern, repetitions);
            }
            else if (repetitions > 0) {
                coil.wind_by_sections(repetitions);
            }
            else {
                coil.wind_by_sections();
            }
        }
        else {
            if (pattern.size() > 0 && repetitions > 0) {
                coil.wind_by_sections(pattern, repetitions);
            }
            else if (repetitions > 0) {
                coil.wind_by_sections(repetitions);
            }
            else {
                coil.wind_by_sections();
            }
        }

        json result;
        to_json(result, coil);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json wind_by_layers(json coilJson, json insulationLayersJson, double insulationThickness) {
    try {
        std::map<std::pair<size_t, size_t>, std::vector<Layer>> insulationLayers;

        for (auto [key, layersJson] : insulationLayersJson.items()) {
            auto keys = OpenMagnetics::split(key, ",");
            std::pair<size_t, size_t> windingsMapKey(stoi(keys[0]), stoi(keys[1]));
            std::vector<Layer> layers;
            for (auto layerJson : layersJson) {
                layers.push_back(Layer(layerJson));
            }
            insulationLayers[windingsMapKey] = layers;
        }

        std::vector<OpenMagnetics::Winding> winding;
        for (auto elem : coilJson["functionalDescription"]) {
            winding.push_back(OpenMagnetics::Winding(elem));
        }

        std::vector<Section> coilSectionsDescription;
        for (auto elem : coilJson["sectionsDescription"]) {
            coilSectionsDescription.push_back(Section(elem));
        }
        OpenMagnetics::Coil coil;

        if (insulationThickness > 0) {
            coil.calculate_custom_thickness_insulation(insulationThickness);
        }

        if (insulationLayers.size() > 0) {
            coil.set_insulation_layers(insulationLayers);
        }

        if (coilJson.contains("interleavingLevel")) {
            coil.set_interleaving_level(coilJson["interleavingLevel"]);
        }
        if (coilJson.contains("windingOrientation")) {
            coil.set_winding_orientation(coilJson["windingOrientation"]);
        }
        if (coilJson.contains("layersOrientation")) {
            coil.set_layers_orientation(coilJson["layersOrientation"]);
        }
        if (coilJson.contains("turnsAlignment")) {
            coil.set_turns_alignment(coilJson["turnsAlignment"]);
        }
        if (coilJson.contains("sectionAlignment")) {
            coil.set_section_alignment(coilJson["sectionAlignment"]);
        }

        coil.set_bobbin(coilJson["bobbin"]);
        coil.set_functional_description(winding);
        coil.set_sections_description(coilSectionsDescription);
        coil.wind_by_layers();

        json result;
        to_json(result, coil);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json wind_by_turns(json coilJson) {
    try {

        std::vector<OpenMagnetics::Winding> winding;
        for (auto elem : coilJson["functionalDescription"]) {
            winding.push_back(OpenMagnetics::Winding(elem));
        }
        std::vector<Section> coilSectionsDescription;
        for (auto elem : coilJson["sectionsDescription"]) {
            coilSectionsDescription.push_back(Section(elem));
        }
        std::vector<Layer> coilLayersDescription;
        for (auto elem : coilJson["layersDescription"]) {
            coilLayersDescription.push_back(Layer(elem));
        }

        OpenMagnetics::Coil coil;

        if (coilJson.contains("interleavingLevel")) {
            coil.set_interleaving_level(coilJson["interleavingLevel"]);
        }
        if (coilJson.contains("windingOrientation")) {
            coil.set_winding_orientation(coilJson["windingOrientation"]);
        }
        if (coilJson.contains("layersOrientation")) {
            coil.set_layers_orientation(coilJson["layersOrientation"]);
        }
        if (coilJson.contains("turnsAlignment")) {
            coil.set_turns_alignment(coilJson["turnsAlignment"]);
        }
        if (coilJson.contains("sectionAlignment")) {
            coil.set_section_alignment(coilJson["sectionAlignment"]);
        }

        coil.set_bobbin(coilJson["bobbin"]);
        coil.set_functional_description(winding);
        coil.set_sections_description(coilSectionsDescription);
        coil.set_layers_description(coilLayersDescription);
        coil.wind_by_turns();

        json result;
        to_json(result, coil);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json delimit_and_compact(json coilJson) {
    try {

        std::vector<OpenMagnetics::Winding> winding;
        for (auto elem : coilJson["functionalDescription"]) {
            winding.push_back(OpenMagnetics::Winding(elem));
        }
        std::vector<Section> coilSectionsDescription;
        for (auto elem : coilJson["sectionsDescription"]) {
            coilSectionsDescription.push_back(Section(elem));
        }
        std::vector<Layer> coilLayersDescription;
        for (auto elem : coilJson["layersDescription"]) {
            coilLayersDescription.push_back(Layer(elem));
        }
        std::vector<Turn> coilTurnsDescription;
        for (auto elem : coilJson["turnsDescription"]) {
            coilTurnsDescription.push_back(Turn(elem));
        }

        OpenMagnetics::Coil coil;

        if (coilJson.contains("interleavingLevel")) {
            coil.set_interleaving_level(coilJson["interleavingLevel"]);
        }
        if (coilJson.contains("windingOrientation")) {
            coil.set_winding_orientation(coilJson["windingOrientation"]);
        }
        if (coilJson.contains("layersOrientation")) {
            coil.set_layers_orientation(coilJson["layersOrientation"]);
        }
        if (coilJson.contains("turnsAlignment")) {
            coil.set_turns_alignment(coilJson["turnsAlignment"]);
        }
        if (coilJson.contains("sectionAlignment")) {
            coil.set_section_alignment(coilJson["sectionAlignment"]);
        }

        coil.set_bobbin(coilJson["bobbin"]);
        coil.set_functional_description(winding);
        coil.set_sections_description(coilSectionsDescription);
        coil.set_layers_description(coilLayersDescription);
        coil.set_turns_description(coilTurnsDescription);
        coil.delimit_and_compact();

        json result;
        to_json(result, coil);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json get_layers_by_winding_index(json coilJson, int windingIndex) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);

        json result = json::array();
        for (auto& layer : coil.get_layers_by_winding_index(windingIndex)) {
            json aux;
            to_json(aux, layer);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json get_layers_by_section(json coilJson, json sectionName) {
    try {
        json result = json::array();
        OpenMagnetics::Coil coil(coilJson, false);
        for (auto& layer : coil.get_layers_by_section(sectionName)) {
            json aux;
            to_json(aux, layer);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json get_sections_description_conduction(json coilJson) {
    try {
        json result = json::array();
        OpenMagnetics::Coil coil(coilJson, false);
        for (auto& section : coil.get_sections_description_conduction()) {
            json aux;
            to_json(aux, section);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

bool are_sections_and_layers_fitting(json coilJson) {
    try {
        json result = json::array();
        OpenMagnetics::Coil coil(coilJson, false);
        return coil.are_sections_and_layers_fitting();
    }
    catch (const std::exception &exc) {
        std::cout << "Exception: " + std::string{exc.what()} << std::endl;
        return false;
    }
}

json add_margin_to_section_by_index(json coilJson, int sectionIndex, double top_or_left_margin, double bottom_or_right_margin) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        coil.add_margin_to_section_by_index(sectionIndex, {top_or_left_margin, bottom_or_right_margin});

        json result;
        to_json(result, coil);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

std::vector<std::string> get_available_winding_orientations() {
    std::vector<std::string> orientations;
    for (auto& [orientation, _] : magic_enum::enum_entries<WindingOrientation>()) {
        json orientationJson;
        to_json(orientationJson, orientation);
        orientations.push_back(orientationJson);
    }
    return orientations;
}

std::vector<std::string> get_available_coil_alignments() {
    std::vector<std::string> orientations;
    for (auto& [orientation, _] : magic_enum::enum_entries<CoilAlignment>()) {
        json orientationJson;
        to_json(orientationJson, orientation);
        orientations.push_back(orientationJson);
    }
    return orientations;
}

std::vector<int> calculate_number_turns(int numberTurnsPrimary, json designRequirementsJson) {
    DesignRequirements designRequirements(designRequirementsJson);

    OpenMagnetics::NumberTurns numberTurns(numberTurnsPrimary, designRequirements);
    auto numberTurnsCombination = numberTurns.get_next_number_turns_combination();

    std::vector<int> numberTurnsResult;
    for (auto turns : numberTurnsCombination) {
        numberTurnsResult.push_back(static_cast<std::make_signed<int>::type>(turns));
    }
    return numberTurnsResult;
}

json get_insulation_materials() {
    try {
        auto insulationMaterials = OpenMagnetics::get_insulation_materials();
        json result = json::array();
        for (auto elem : insulationMaterials) {
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

json get_insulation_material_names() {
    try {
        auto insulationMaterialNames = OpenMagnetics::get_insulation_material_names();
        json result = json::array();
        for (auto elem : insulationMaterialNames) {
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

json find_insulation_material_by_name(json insulationMaterialName) {
    try {
        auto insulationMaterialData = OpenMagnetics::find_insulation_material_by_name(insulationMaterialName);
        json result;
        to_json(result, insulationMaterialData);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_insulation(json inputsJson) {
    auto standard = OpenMagnetics::InsulationCoordinator();
    OpenMagnetics::Inputs inputs(inputsJson, false);

    json result;
    try {
        result["creepageDistance"] = standard.calculate_creepage_distance(inputs);
        result["clearance"] = standard.calculate_clearance(inputs);
        result["withstandVoltage"] = standard.calculate_withstand_voltage(inputs);
        result["distanceThroughInsulation"] = standard.calculate_distance_through_insulation(inputs);
        result["errorMessage"] = "";
    }
    catch(const std::runtime_error& re) {
        result["errorMessage"] = "Exception: " + std::string{re.what()};
    }
    catch(const std::exception& ex) {
        result["errorMessage"] = "Exception: " + std::string{ex.what()};
    }
    catch(...) {
        result["errorMessage"] = "Unknown failure occurred. Possible memory corruption";
    }
    return result;
}

json get_insulation_layer_insulation_material(json coilJson, std::string layerName) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        auto material = OpenMagnetics::Coil::resolve_insulation_layer_insulation_material(coil, layerName);

        json result;
        to_json(result, material);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json get_isolation_side_from_index(size_t index) {
    return OpenMagnetics::get_isolation_side_from_index(index);
}

void register_winding_bindings(py::module& m) {
    // Winding functions
    m.def("wind", &wind,
        R"pbdoc(
        Wind coils on a magnetic core according to specifications.
        
        The main winding function that places turns in the winding window,
        organizing them into sections, layers, and individual turns. Supports
        various winding patterns including interleaved and sectored windings.
        
        Args:
            coil_json: JSON object containing:
                - bobbin: Bobbin specification or name
                - functionalDescription: Array of Winding objects with:
                    - name: Winding identifier (e.g., "Primary", "Secondary")
                    - numberTurns: Number of turns for this winding
                    - numberParallels: Number of parallel conductors
                    - wire: Wire specification or name
                - layersOrientation: Optional layer stacking direction
                - turnsAlignment: Optional turn alignment within layers
            repetitions: Number of times to repeat the winding pattern.
            proportion_per_winding_json: Proportion of window for each winding.
            pattern_json: Winding order pattern (e.g., [0, 1] for P-S-P-S).
            margin_pairs_json: Margin tape pairs [[left, right], ...].
        
        Returns:
            JSON Coil object with complete descriptions:
                - functionalDescription: Input winding specs
                - sectionsDescription: Section-level organization
                - layersDescription: Layer-level arrangement
                - turnsDescription: Individual turn positions
        
        Example:
            >>> coil = {
            ...     "bobbin": bobbin_data,
            ...     "functionalDescription": [
            ...         {"name": "Primary", "numberTurns": 20, "numberParallels": 1, "wire": "Round 0.5 - Grade 1"},
            ...         {"name": "Secondary", "numberTurns": 5, "numberParallels": 2, "wire": "Round 1.0 - Grade 1"}
            ...     ]
            ... }
            >>> result = PyMKF.wind(coil, 2, [0.5, 0.5], [0, 1], [[0.001, 0.001]])
        )pbdoc",
        py::arg("coil_json"), py::arg("repetitions"), py::arg("proportion_per_winding_json"),
        py::arg("pattern_json"), py::arg("margin_pairs_json"));
    
    m.def("wind_planar", &wind_planar,
        R"pbdoc(
        Wind planar (PCB) coils with layer stack-up specification.
        
        For PCB-integrated magnetics with traces on multiple layers.
        
        Args:
            coil_json: JSON Coil specification.
            stack_up_json: Layer stack-up array [winding_index per layer].
            border_to_wire_distance: Clearance from board edge in meters.
            wire_to_wire_distance_json: Spacing between traces per layer.
            insulation_thickness_json: Insulation between layer pairs.
            core_to_layer_distance: Gap between core and first layer.
        
        Returns:
            JSON Coil object with planar winding arrangement.
        )pbdoc",
        py::arg("coil_json"), py::arg("stack_up_json"), py::arg("border_to_wire_distance"),
        py::arg("wire_to_wire_distance_json"), py::arg("insulation_thickness_json"), py::arg("core_to_layer_distance"));
    
    m.def("wind_by_sections", &wind_by_sections,
        R"pbdoc(
        Wind coil organized by sections only (no layer/turn details).
        
        Creates section-level description for initial design exploration.
        
        Args:
            coil_json: JSON Coil specification.
            repetitions: Pattern repetition count.
            proportion_per_winding_json: Window proportion per winding.
            pattern_json: Winding order pattern.
            insulation_thickness: Inter-section insulation in meters.
        
        Returns:
            JSON Coil with sectionsDescription populated.
        )pbdoc",
        py::arg("coil_json"), py::arg("repetitions"), py::arg("proportion_per_winding_json"),
        py::arg("pattern_json"), py::arg("insulation_thickness"));
    
    m.def("wind_by_layers", &wind_by_layers,
        R"pbdoc(
        Wind coil with layer-level detail from section description.
        
        Takes a coil with sections and generates layer arrangement.
        
        Args:
            coil_json: JSON Coil with sectionsDescription.
            insulation_layers_json: Insulation layer specs between windings.
            insulation_thickness: Default insulation thickness in meters.
        
        Returns:
            JSON Coil with layersDescription populated.
        )pbdoc",
        py::arg("coil_json"), py::arg("insulation_layers_json"), py::arg("insulation_thickness"));
    
    m.def("wind_by_turns", &wind_by_turns,
        R"pbdoc(
        Wind coil with turn-level detail from layer description.
        
        Places individual turns within defined layers.
        
        Args:
            coil_json: JSON Coil with layersDescription.
        
        Returns:
            JSON Coil with turnsDescription populated.
        )pbdoc",
        py::arg("coil_json"));
    
    m.def("delimit_and_compact", &delimit_and_compact,
        R"pbdoc(
        Delimit and compact winding layout to minimize window usage.
        
        Optimizes turn positions within the winding window.
        
        Args:
            coil_json: JSON Coil with complete winding description.
        
        Returns:
            JSON Coil with optimized turn positions.
        )pbdoc",
        py::arg("coil_json"));

    // Layer and section functions
    m.def("get_layers_by_winding_index", &get_layers_by_winding_index,
        R"pbdoc(
        Get all layers belonging to a specific winding.
        
        Args:
            coil_json: JSON Coil with layersDescription.
            winding_index: Zero-based winding index.
        
        Returns:
            JSON array of Layer objects for that winding.
        )pbdoc",
        py::arg("coil_json"), py::arg("winding_index"));
    
    m.def("get_layers_by_section", &get_layers_by_section,
        R"pbdoc(
        Get all layers within a named section.
        
        Args:
            coil_json: JSON Coil with layersDescription.
            section_name: Name of the section.
        
        Returns:
            JSON array of Layer objects in that section.
        )pbdoc",
        py::arg("coil_json"), py::arg("section_name"));
    
    m.def("get_sections_description_conduction", &get_sections_description_conduction,
        R"pbdoc(
        Get only conduction sections (excluding insulation sections).
        
        Args:
            coil_json: JSON Coil with sectionsDescription.
        
        Returns:
            JSON array of Section objects with type "conduction".
        )pbdoc",
        py::arg("coil_json"));
    
    m.def("are_sections_and_layers_fitting", &are_sections_and_layers_fitting,
        R"pbdoc(
        Check if all sections and layers fit within the winding window.
        
        Args:
            coil_json: JSON Coil with winding description.
        
        Returns:
            True if everything fits, False otherwise.
        )pbdoc",
        py::arg("coil_json"));
    
    m.def("add_margin_to_section_by_index", &add_margin_to_section_by_index,
        R"pbdoc(
        Add margin tape to a section.
        
        Args:
            coil_json: JSON Coil specification.
            section_index: Zero-based section index.
            top_or_left_margin: Top/left margin in meters.
            bottom_or_right_margin: Bottom/right margin in meters.
        
        Returns:
            Updated JSON Coil with margin added.
        )pbdoc",
        py::arg("coil_json"), py::arg("section_index"), 
        py::arg("top_or_left_margin"), py::arg("bottom_or_right_margin"));

    // Winding orientation and alignment
    m.def("get_available_winding_orientations", &get_available_winding_orientations,
        R"pbdoc(
        Get list of available winding orientation options.
        
        Returns:
            List of orientation strings: "contiguous", "overlapping".
        )pbdoc");
    
    m.def("get_available_coil_alignments", &get_available_coil_alignments,
        R"pbdoc(
        Get list of available coil alignment options.
        
        Returns:
            List of alignment strings: "inner or top", "outer or bottom", "spread", "centered".
        )pbdoc");

    // Number of turns
    m.def("calculate_number_turns", &calculate_number_turns,
        R"pbdoc(
        Calculate optimal number of turns for all windings.
        
        Given primary turns and design requirements (turns ratios),
        calculates the turns for all windings.
        
        Args:
            number_turns_primary: Number of primary turns.
            design_requirements_json: JSON DesignRequirements with turnsRatios.
        
        Returns:
            List of integer turns for each winding [primary, secondary, ...].
        )pbdoc",
        py::arg("number_turns_primary"), py::arg("design_requirements_json"));

    // Insulation
    m.def("get_insulation_materials", &get_insulation_materials,
        R"pbdoc(
        Retrieve all available insulation materials from database.
        
        Returns:
            JSON array of InsulationMaterial objects with dielectric
            properties, thickness, and temperature ratings.
        )pbdoc");
    
    m.def("get_insulation_material_names", &get_insulation_material_names,
        R"pbdoc(
        Retrieve list of all insulation material names.
        
        Returns:
            JSON array of material name strings.
        )pbdoc");
    
    m.def("find_insulation_material_by_name", &find_insulation_material_by_name,
        R"pbdoc(
        Find insulation material data by name.
        
        Args:
            name: Insulation material name.
        
        Returns:
            JSON InsulationMaterial object.
        )pbdoc",
        py::arg("name"));
    
    m.def("calculate_insulation", &calculate_insulation,
        R"pbdoc(
        Calculate insulation requirements per safety standards.
        
        Computes creepage, clearance, and dielectric requirements based on
        IEC 60664-1, IEC 61558-1, IEC 62368-1, or IEC 60335-1 standards.
        
        Args:
            inputs_json: JSON Inputs with insulation requirements:
                - insulationType: "Functional", "Basic", "Reinforced", etc.
                - pollutionDegree: "P1", "P2", "P3"
                - overvoltageCategory: "OVC-I" to "OVC-IV"
                - altitude: Operating altitude
                - standards: Array of applicable standards
        
        Returns:
            JSON object with:
                - creepageDistance: Required creepage in meters
                - clearance: Required clearance in meters
                - withstandVoltage: Test voltage in Volts
                - distanceThroughInsulation: Solid insulation in meters
                - errorMessage: Empty if successful, error description otherwise
        )pbdoc",
        py::arg("inputs_json"));
    
    m.def("get_insulation_layer_insulation_material", &get_insulation_layer_insulation_material,
        R"pbdoc(
        Get the insulation material used in a specific insulation layer.
        
        Args:
            coil_json: JSON Coil specification.
            layer_name: Name of the insulation layer.
        
        Returns:
            JSON InsulationMaterial object.
        )pbdoc",
        py::arg("coil_json"), py::arg("layer_name"));
    
    m.def("get_isolation_side_from_index", &get_isolation_side_from_index,
        R"pbdoc(
        Get isolation side designation from winding index.
        
        Used for insulation coordination between primary and secondary sides.
        
        Args:
            index: Winding index (0 = primary, 1+ = secondaries).
        
        Returns:
            JSON IsolationSide string ("Primary", "Secondary", etc.).
        )pbdoc",
        py::arg("index"));
}

} // namespace PyMKF
