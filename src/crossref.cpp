#include "crossref.h"

#include "advisers/CoreCrossReferencer.h"
#include "advisers/CoreMaterialCrossReferencer.h"

namespace PyMKF {

// The cross-referencers were reachable only from the WASM build (the web app's
// `crossReferencers` module), so a Python consumer could not offer the
// CoreCrossReferencer / CoreMaterialCrossReferencer tools the app has. These
// mirror that surface, following the same {"data": ...} envelope and
// "Exception: ..." error convention as the advisers.

json calculate_cross_referenced_core(json referenceCoreJson, json inputsJson,
                                     int64_t referenceNumberTurns, json weightsJson,
                                     int maximumNumberResults) {
    try {
        OpenMagnetics::Core referenceCore(referenceCoreJson);
        OpenMagnetics::Inputs inputs(inputsJson);

        std::map<std::string, double> weightsKeysJson = weightsJson;
        std::map<OpenMagnetics::CoreCrossReferencerFilters, double> weights;
        for (auto const& [filterName, weight] : weightsKeysJson) {
            OpenMagnetics::CoreCrossReferencerFilters filter;
            OpenMagnetics::from_json(filterName, filter);
            weights[filter] = weight;
        }

        OpenMagnetics::CoreCrossReferencer coreCrossReferencer;
        auto scoredCores = weights.empty()
            ? coreCrossReferencer.get_cross_referenced_core(referenceCore, referenceNumberTurns,
                                                            inputs, maximumNumberResults)
            : coreCrossReferencer.get_cross_referenced_core(referenceCore, referenceNumberTurns,
                                                            inputs, weights, maximumNumberResults);

        auto scoringsPerFilter = coreCrossReferencer.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [core, scoring] : scoredCores) {
            json result;
            json coreJson;
            to_json(coreJson, core);
            result["core"] = coreJson;
            result["scoring"] = scoring;

            std::string name = core.get_name().value_or("");
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        OpenMagnetics::settings.reset();
        return results;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_cross_referenced_core_material(json referenceCoreMaterialJson, double temperature,
                                              json weightsJson, int maximumNumberResults) {
    try {
        CoreMaterial referenceCoreMaterial(referenceCoreMaterialJson);

        std::map<std::string, double> weightsKeysJson = weightsJson;
        std::map<OpenMagnetics::CoreMaterialCrossReferencerFilters,
                 double> weights;
        for (auto const& [filterName, weight] : weightsKeysJson) {
            OpenMagnetics::CoreMaterialCrossReferencerFilters filter;
            OpenMagnetics::from_json(filterName, filter);
            weights[filter] = weight;
        }

        OpenMagnetics::CoreMaterialCrossReferencer coreMaterialCrossReferencer;
        auto scoredMaterials = weights.empty()
            ? coreMaterialCrossReferencer.get_cross_referenced_core_material(
                  referenceCoreMaterial, temperature, maximumNumberResults)
            : coreMaterialCrossReferencer.get_cross_referenced_core_material(
                  referenceCoreMaterial, temperature, weights, maximumNumberResults);

        auto scoringsPerFilter = coreMaterialCrossReferencer.get_scorings();

        json results = json();
        results["data"] = json::array();
        for (auto& [material, scoring] : scoredMaterials) {
            json result;
            json materialJson;
            to_json(materialJson, material);
            result["material"] = materialJson;
            result["scoring"] = scoring;

            std::string name = material.get_name();
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& [filter, filterScore] : scoringsPerFilter[name]) {
                    filterScorings[std::string(magic_enum::enum_name(filter))] = filterScore;
                }
                result["scoringPerFilter"] = filterScorings;
            }
            results["data"].push_back(result);
        }

        OpenMagnetics::settings.reset();
        return results;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

void register_crossref_bindings(py::module& m) {
    m.def("calculate_cross_referenced_core", &calculate_cross_referenced_core,
        R"pbdoc(
        Rank cores that could replace a reference core.

        Args:
            reference_core_json: the core being replaced (shape, material, gapping).
            inputs_json: design requirements and operating points the replacement must meet.
            reference_number_turns: turns on the reference design.
            weights_json: optional filter weights. Keys: "PERMEANCE", "CORE_LOSSES",
                          "SATURATION", "WINDING_WINDOW_AREA", "EFFECTIVE_AREA",
                          "ENVELOPING_VOLUME". Empty uses the adviser's defaults.
            max_results: how many alternatives to return.

        Returns:
            {"data": [{"core", "scoring", "scoringPerFilter"}]} best first, or
            {"data": "Exception: ..."} on failure.
        )pbdoc",
        py::arg("reference_core_json"), py::arg("inputs_json"),
        py::arg("reference_number_turns"), py::arg("weights_json") = json::object(),
        py::arg("max_results") = 10);

    m.def("calculate_cross_referenced_core_material", &calculate_cross_referenced_core_material,
        R"pbdoc(
        Rank core materials that could replace a reference material.

        Args:
            reference_core_material_json: the material being replaced.
            temperature: operating temperature in Celsius (material properties are
                         strongly temperature dependent, so this is not optional).
            weights_json: optional filter weights. Keys: "INITIAL_PERMEABILITY",
                          "REMANENCE", "COERCIVE_FORCE", "SATURATION",
                          "CURIE_TEMPERATURE", "VOLUMETRIC_LOSSES".
            max_results: how many alternatives to return.

        Returns:
            {"data": [{"material", "scoring", "scoringPerFilter"}]} best first, or
            {"data": "Exception: ..."} on failure.
        )pbdoc",
        py::arg("reference_core_material_json"), py::arg("temperature"),
        py::arg("weights_json") = json::object(), py::arg("max_results") = 10);
}

} // namespace PyMKF
