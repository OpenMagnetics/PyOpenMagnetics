#include "advisers.h"

namespace PyMKF {

json calculate_advised_cores(json inputsJson, json weightsJson, int maximumNumberResults, json coreModeJson) {
    try {
        OpenMagnetics::Inputs inputs(inputsJson);
        OpenMagnetics::CoreAdviser::CoreAdviserModes coreMode;
        from_json(coreModeJson, coreMode);
        std::map<std::string, double> weightsKeysJson = weightsJson;
        std::map<OpenMagnetics::CoreAdviser::CoreAdviserFilters, double> weights;

        weights[OpenMagnetics::CoreAdviser::CoreAdviserFilters::COST] = 1;
        weights[OpenMagnetics::CoreAdviser::CoreAdviserFilters::EFFICIENCY] = 1;
        weights[OpenMagnetics::CoreAdviser::CoreAdviserFilters::DIMENSIONS] = 1;

        for (auto const& [filterName, weight] : weightsKeysJson) {
            OpenMagnetics::CoreAdviser::CoreAdviserFilters filter;
            OpenMagnetics::from_json(filterName, filter);
            weights[filter] = weight;
        }

        OpenMagnetics::CoreAdviser coreAdviser;
        coreAdviser.set_mode(coreMode);
        auto masMagnetics = coreAdviser.get_advised_core(inputs, weights, maximumNumberResults);

        auto scoringsPerFilter = coreAdviser.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [masMagnetic, scoring] : masMagnetics) {
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        sort(results["data"].begin(), results["data"].end(), [](json& b1, json& b2) {
            return b1["scoring"] > b2["scoring"];
        });

        OpenMagnetics::settings.reset();

        return results;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_advised_magnetics(json inputsJson, int maximumNumberResults, json coreModeJson) {
    try {
        OpenMagnetics::Inputs inputs(inputsJson);
        OpenMagnetics::CoreAdviser::CoreAdviserModes coreMode;
        from_json(coreModeJson, coreMode);

        OpenMagnetics::MagneticAdviser magneticAdviser;
        magneticAdviser.set_core_mode(coreMode);
        auto masMagnetics = magneticAdviser.get_advised_magnetic(inputs, maximumNumberResults);

        auto scoringsPerFilter = magneticAdviser.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [masMagnetic, scoring] : masMagnetics) {
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        sort(results["data"].begin(), results["data"].end(), [](json& b1, json& b2) {
            return b1["scoring"] > b2["scoring"];
        });

        return results;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_advised_magnetics_with_filters(json inputsJson, json filterFlowJson, int maximumNumberResults, json coreModeJson) {
    // FAST custom design driven by a CALLER-SUPPLIED filter flow: strictlyRequired
    // filters (e.g. DC/EFFECTIVE_CURRENT_DENSITY, which the default custom flow
    // omits) DROP any wound candidate that fails them, so designed windings are
    // current-density gated while the fast path's loss ranking + core search are
    // preserved. Exposes MagneticAdviser::get_advised_magnetic_fast(inputs, flow, n).
    try {
        OpenMagnetics::Inputs inputs(inputsJson);
        OpenMagnetics::CoreAdviser::CoreAdviserModes coreMode;
        from_json(coreModeJson, coreMode);

        std::vector<OpenMagnetics::MagneticFilterOperation> filterFlow;
        for (auto filterJson : filterFlowJson) {
            OpenMagnetics::MagneticFilterOperation filter(filterJson);
            filterFlow.push_back(filter);
        }

        OpenMagnetics::MagneticAdviser magneticAdviser;
        magneticAdviser.set_core_mode(coreMode);
        auto masMagnetics = magneticAdviser.get_advised_magnetic_fast(inputs, filterFlow, maximumNumberResults);

        auto scoringsPerFilter = magneticAdviser.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [masMagnetic, scoring] : masMagnetics) {
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        sort(results["data"].begin(), results["data"].end(), [](json& b1, json& b2) {
            return b1["scoring"] > b2["scoring"];
        });

        return results;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_advised_magnetics_fast(json inputsJson, int maximumNumberResults, json coreModeJson) {
    try {
        OpenMagnetics::Inputs inputs(inputsJson);
        OpenMagnetics::CoreAdviser::CoreAdviserModes coreMode;
        from_json(coreModeJson, coreMode);

        OpenMagnetics::MagneticAdviser magneticAdviser;
        magneticAdviser.set_core_mode(coreMode);
        auto masMagnetics = magneticAdviser.get_advised_magnetic_fast(inputs, maximumNumberResults);

        json results = json();
        results["data"] = json::array();
        for (auto& [masMagnetic, scoring] : masMagnetics) {
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            results["data"].push_back(result);
        }

        return results;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_advised_magnetics_from_catalog(json inputsJson, json catalogJson, int maximumNumberResults) {
    try {
        OpenMagnetics::settings.set_coil_delimit_and_compact(true);
        OpenMagnetics::Inputs inputs(inputsJson);
        std::map<OpenMagnetics::MagneticFilters, double> weights;

        std::vector <OpenMagnetics::Magnetic> catalog;

        for (auto magneticJson : catalogJson) {
            OpenMagnetics::Magnetic magnetic(magneticJson);
            catalog.push_back(magnetic);
        }

        OpenMagnetics::MagneticAdviser magneticAdviser;
        auto masMagnetics = magneticAdviser.get_advised_magnetic(inputs, catalog, maximumNumberResults);

        auto scoringsPerFilter = magneticAdviser.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [masMagnetic, scoring] : masMagnetics) {
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        sort(results["data"].begin(), results["data"].end(), [](json& b1, json& b2) {
            return b1["scoring"] > b2["scoring"];
        });

        return results;
    }
    catch (const std::exception &exc) {
        std::cout << inputsJson << std::endl;
        std::cout << catalogJson << std::endl;
        std::cout << maximumNumberResults << std::endl;
        return "Exception: " + std::string{exc.what()};
    }
}

json calculate_advised_magnetics_from_cache(json inputsJson, json filterFlowJson, int maximumNumberResults) {
    try {
        OpenMagnetics::settings.set_coil_delimit_and_compact(true);
        OpenMagnetics::Inputs inputs(inputsJson);

        std::vector<OpenMagnetics::MagneticFilterOperation> filterFlow;
        for (auto filterJson : filterFlowJson) {
            OpenMagnetics::MagneticFilterOperation filter(filterJson);
            filterFlow.push_back(filter);
        }

        if (OpenMagnetics::magneticsCache.size() == 0) {
            return "Exception: No magnetics found in cache";
        }

        OpenMagnetics::MagneticAdviser magneticAdviser;
        auto masMagnetics = magneticAdviser.get_advised_magnetic(inputs, OpenMagnetics::magneticsCache.get(), filterFlow, maximumNumberResults);

        auto scoringsPerFilter = magneticAdviser.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [masMagnetic, scoring] : masMagnetics) {
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        sort(results["data"].begin(), results["data"].end(), [](json& b1, json& b2) {
            return b1["scoring"] > b2["scoring"];
        });

        return results;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json calculate_advised_sections(json masJson, json patternJson, int repetitions) {
    try {
        OpenMagnetics::Mas mas(masJson);
        std::vector<size_t> pattern;
        for (auto& elem : patternJson) {
            pattern.push_back(elem);
        }
        auto bobbin = mas.get_magnetic().get_coil().get_bobbin();
        if (std::holds_alternative<std::string>(bobbin)) {
            auto bobbinString = std::get<std::string>(bobbin);
            if (bobbinString == "Dummy") {
                mas.get_mutable_magnetic().get_mutable_coil().set_bobbin(
                    OpenMagnetics::Bobbin::create_quick_bobbin(mas.get_mutable_magnetic().get_mutable_core()));
            }
        }
        for (size_t windingIndex = 0; windingIndex < mas.get_magnetic().get_coil().get_functional_description().size(); ++windingIndex) {
            mas.get_mutable_magnetic().get_mutable_coil().get_mutable_functional_description()[windingIndex].set_wire("Dummy");
        }
        auto sections = OpenMagnetics::CoilAdviser().get_advised_sections(mas, pattern, repetitions);
        json result = json::array();
        for (auto& section : sections) {
            json aux;
            to_json(aux, section);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception& exc) {
        return json{{"error", std::string("calculate_advised_sections: ") + exc.what()}};
    }
}

json calculate_advised_coil(json masJson) {
    try {
        OpenMagnetics::Settings::GetInstance().set_coil_delimit_and_compact(true);
        OpenMagnetics::Mas mas(masJson);
        for (size_t windingIndex = 0; windingIndex < mas.get_magnetic().get_coil().get_functional_description().size(); ++windingIndex) {
            mas.get_mutable_magnetic().get_mutable_coil().get_mutable_functional_description()[windingIndex].set_wire("Dummy");
        }
        mas.get_mutable_magnetic().get_mutable_coil().set_turns_description(std::nullopt);
        mas.get_mutable_magnetic().get_mutable_coil().set_layers_description(std::nullopt);
        mas.get_mutable_magnetic().get_mutable_coil().set_sections_description(std::nullopt);
        mas.get_mutable_magnetic().get_mutable_coil().set_groups_description(std::nullopt);
        OpenMagnetics::CoilAdviser coilAdviser;
        auto masMagneticsWithCoil = coilAdviser.get_advised_coil(mas, 1);
        if (masMagneticsWithCoil.size() > 0) {
            json result;
            to_json(result, masMagneticsWithCoil[0]);
            return result;
        }
        else {
            return json{{"error", "No coil found"}};
        }
    }
    catch (const std::exception& exc) {
        return json{{"error", std::string("calculate_advised_coil: ") + exc.what()}};
    }
}

json calculate_advised_wires(json windingJson, json sectionJson, json currentJson, json solidInsulationRequirementsJson, double temperature, uint8_t numberSections, size_t maximumNumberResults, bool usePlanarWires) {
    try {
        OpenMagnetics::Settings::GetInstance().set_coil_delimit_and_compact(true);
        OpenMagnetics::Winding winding(windingJson);
        OpenMagnetics::WireSolidInsulationRequirements wireSolidInsulationRequirements(solidInsulationRequirementsJson);
        Section section(sectionJson);
        SignalDescriptor current(currentJson);
        OpenMagnetics::WireAdviser wireAdviser;
        wireAdviser.set_wire_solid_insulation_requirements(wireSolidInsulationRequirements);
        std::vector<std::pair<OpenMagnetics::Winding, double>> windingsWithScoring;
        if (usePlanarWires) {
            windingsWithScoring = wireAdviser.get_advised_planar_wire(winding, section, current, temperature, numberSections, maximumNumberResults);
        }
        else {
            windingsWithScoring = wireAdviser.get_advised_wire(winding, section, current, temperature, numberSections, maximumNumberResults);
        }
        json results;
        results["data"] = json::array();
        for (auto& [w, scoring] : windingsWithScoring) {
            json result;
            json windingJson;
            to_json(windingJson, w);
            result["winding"] = windingJson;
            result["scoring"] = scoring;
            results["data"].push_back(result);
        }
        return results;
    }
    catch (const std::exception& exc) {
        return json{{"error", std::string("calculate_advised_wires: ") + exc.what()}};
    }
}

void register_adviser_bindings(py::module& m) {
    m.def("calculate_advised_cores", &calculate_advised_cores,
        R"pbdoc(
        Get recommended cores for given design requirements.
        
        Analyzes the input requirements and returns a ranked list of suitable cores
        based on the specified weights for cost, efficiency, and dimensions.
        
        Args:
            inputs_json: JSON object containing design requirements and operating points.
                         Should be processed using process_inputs() first.
            weights_json: JSON object with filter weights. Keys can be:
                         "COST", "EFFICIENCY", "DIMENSIONS" with float values 0-1.
            max_results: Maximum number of core recommendations to return.
            core_mode_json: Core selection mode - "AVAILABLE_CORES" or "STANDARD_CORES".
        
        Returns:
            JSON object with "data" array containing ranked results.
            Each result has:
            - "mas": Mas object with magnetic data
            - "scoring": Overall float score
            - "scoringPerFilter": Object with individual scores per filter
              (e.g., {"COST": 0.8, "EFFICIENCY": 0.9, "DIMENSIONS": 0.7})
        
        Example:
            >>> inputs = PyMKF.process_inputs(raw_inputs)
            >>> weights = {"COST": 1, "EFFICIENCY": 1, "DIMENSIONS": 0.5}
            >>> result = PyMKF.calculate_advised_cores(inputs, weights, 10, "AVAILABLE_CORES")
            >>> for item in result["data"]:
            ...     print(f"Score: {item['scoring']}, Per filter: {item['scoringPerFilter']}")
        )pbdoc",
        py::arg("inputs_json"), py::arg("weights_json"), 
        py::arg("max_results"), py::arg("core_mode_json"));
    
    m.def("calculate_advised_magnetics", &calculate_advised_magnetics,
        R"pbdoc(
        Get recommended complete magnetic designs for given requirements.
        
        Performs full magnetic design optimization including core selection,
        winding configuration, and all parameters. Returns complete Mas
        (Magnetic Assembly Specification) objects ready for manufacturing.
        
        Args:
            inputs_json: JSON object containing design requirements and operating points.
                         Should be processed using process_inputs() first.
            max_results: Maximum number of magnetic recommendations to return.
            core_mode_json: Core selection mode - "AVAILABLE_CORES" or "STANDARD_CORES".
        
        Returns:
            JSON object with "data" array containing ranked results.
            Each result has:
            - "mas": Mas object with magnetic, inputs, and optionally outputs
            - "scoring": Overall float score
            - "scoringPerFilter": Object with individual scores per filter
              (e.g., {"COST": 0.8, "LOSSES": 0.9, "DIMENSIONS": 0.7})
        
        Example:
            >>> inputs = PyMKF.process_inputs(raw_inputs)
            >>> result = PyMKF.calculate_advised_magnetics(inputs, 5, "AVAILABLE_CORES")
            >>> for item in result["data"]:
            ...     print(f"Score: {item['scoring']}, Per filter: {item['scoringPerFilter']}")
        )pbdoc",
        py::arg("inputs_json"), py::arg("max_results"), py::arg("core_mode_json"));

    m.def("calculate_advised_magnetics_with_filters", &calculate_advised_magnetics_with_filters,
        R"pbdoc(
        Fast custom magnetic design with a CALLER-SUPPLIED filter flow.

        Like calculate_advised_magnetics_fast(), but strictlyRequired filters in
        filter_flow_json DROP any wound candidate that fails them — e.g. add
        DC_CURRENT_DENSITY / EFFECTIVE_CURRENT_DENSITY so designed windings are
        current-density gated. Each filter op is
        {"filter": <TitleCaseName>, "invert": bool, "log": bool,
         "strictlyRequired": bool, "weight": float}.
        )pbdoc",
        py::arg("inputs_json"), py::arg("filter_flow_json"), py::arg("max_results"), py::arg("core_mode_json"));

    m.def("calculate_advised_magnetics_fast", &calculate_advised_magnetics_fast,
        R"pbdoc(
        Get recommended complete magnetic designs using fast analytical mode.

        Performs rapid magnetic design exploration using analytical turn/gap
        calculation and simplified loss evaluation (DC ohmic + core losses only).
        Bypasses CoilAdviser optimization and full MagneticSimulator for speed.
        Results are sorted by ascending total losses (lower losses = better rank).

        Suitable for design space exploration and Pareto front generation.
        For production designs use calculate_advised_magnetics() instead.

        Args:
            inputs_json: JSON object containing design requirements and operating points.
                         Should be processed using process_inputs() first.
            max_results: Maximum number of magnetic recommendations to return.
            core_mode_json: Core selection mode - "AVAILABLE_CORES" or "STANDARD_CORES".

        Returns:
            JSON object with "data" array containing results sorted by total losses.
            Each result has:
            - "mas": Mas object with magnetic, inputs, and outputs (losses data)
            - "scoring": Total losses value in watts (lower is better)

        Example:
            >>> inputs = PyMKF.process_inputs(raw_inputs)
            >>> result = PyMKF.calculate_advised_magnetics_fast(inputs, 5, "STANDARD_CORES")
            >>> for item in result["data"]:
            ...     print(f"Total losses: {item['scoring']} W")
        )pbdoc",
        py::arg("inputs_json"), py::arg("max_results"), py::arg("core_mode_json"));

    m.def("calculate_advised_magnetics_from_catalog", &calculate_advised_magnetics_from_catalog,
        R"pbdoc(
        Get recommended magnetics from a custom component catalog.
        
        Evaluates magnetic components from a user-provided catalog against
        the design requirements and returns ranked recommendations.
        
        Args:
            inputs_json: JSON object containing design requirements and operating points.
            catalog_json: JSON array of Magnetic objects to evaluate.
            max_results: Maximum number of recommendations to return.
        
        Returns:
            JSON object with "data" array containing ranked results.
            Each result has:
            - "mas": Mas object with magnetic data
            - "scoring": Overall float score
            - "scoringPerFilter": Object with individual scores per filter
        
        Example:
            >>> inputs = PyMKF.process_inputs(raw_inputs)
            >>> catalog = [magnetic1, magnetic2, magnetic3]
            >>> result = PyMKF.calculate_advised_magnetics_from_catalog(inputs, catalog, 5)
            >>> for item in result["data"]:
            ...     print(f"Score: {item['scoring']}, Per filter: {item['scoringPerFilter']}")
        )pbdoc",
        py::arg("inputs_json"), py::arg("catalog_json"), py::arg("max_results"));
    
    m.def("calculate_advised_magnetics_from_cache", &calculate_advised_magnetics_from_cache,
        R"pbdoc(
        Get recommended magnetics from previously cached designs.
        
        Evaluates cached magnetic designs against the requirements using
        a custom filter flow for advanced filtering operations.
        
        Args:
            inputs_json: JSON object containing design requirements and operating points.
            filter_flow_json: JSON array of MagneticFilterOperation objects defining
                              the filtering pipeline.
            max_results: Maximum number of recommendations to return.
        
        Returns:
            JSON object with "data" array containing ranked results,
            or error string if cache is empty.
            Each result has:
            - "mas": Mas object with magnetic data
            - "scoring": Overall float score
            - "scoringPerFilter": Object with individual scores per filter
        
        Note:
            Cache must be populated before calling this function.
            Returns "Exception: No magnetics found in cache" if cache is empty.
        )pbdoc",
        py::arg("inputs_json"), py::arg("filter_flow_json"), py::arg("max_results"));

    m.def("calculate_advised_sections", &calculate_advised_sections,
        "Get advised coil sections.",
        py::arg("mas"), py::arg("pattern"), py::arg("repetitions"));

    m.def("calculate_advised_coil", &calculate_advised_coil,
        "Get full coil design advice.",
        py::arg("mas"));

    m.def("calculate_advised_wires", &calculate_advised_wires,
        "Get wire selection advice.",
        py::arg("winding"), py::arg("section"), py::arg("current"),
        py::arg("solid_insulation_requirements"), py::arg("temperature"), py::arg("number_sections"),
        py::arg("max_results"), py::arg("use_planar_wires") = false);
}

} // namespace PyMKF
