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
}

} // namespace PyMKF
