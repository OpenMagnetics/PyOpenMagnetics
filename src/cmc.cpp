#include "cmc.h"

// The CMC design moved to Kirchhoff with the rest of the converter models (MKF 3e0261fd deleted
// converter_models). This TU is a THIN shim over Kirchhoff::api::design_cmc — the string-in/JSON-out
// facade of libKirchhoffApi.so — that re-shapes its {"inputs", "cmcDiagnostics"} result into the
// legacy calculate_cmc_inputs contract El Choker and the WASM wizard consume: the MAS Inputs spread
// at the ROOT plus a "cmcDiagnostics" sibling, or {"error": "..."} on failure (never a throw).
// Only KirchhoffApi.hpp is included, so no Kirchhoff MAS type ever enters an MKF translation unit.

#include "pybind11_json/pybind11_json.hpp"
#include "json.hpp"
#include <KirchhoffApi.hpp>

#include <string>

namespace py = pybind11;
using json = nlohmann::json;

namespace PyMKF {

namespace {

json cmc_inputs_via_kirchhoff(const json& cmcInputsJson, const char* functionName) {
    const std::string out = Kirchhoff::api::design_cmc(cmcInputsJson.dump());
    constexpr const char* kExceptionPrefix = "Exception: ";
    if (out.rfind(kExceptionPrefix, 0) == 0) {
        return json{{"error", std::string(functionName) + ": " +
                              out.substr(std::string(kExceptionPrefix).size())}};
    }
    json parsed = json::parse(out);
    // Legacy contract: the MAS Inputs at the root + the diagnostics as a sibling key.
    json result = std::move(parsed.at("inputs"));
    result["cmcDiagnostics"] = std::move(parsed.at("cmcDiagnostics"));
    return result;
}

json calculate_cmc_inputs(json cmcInputsJson) {
    return cmc_inputs_via_kirchhoff(cmcInputsJson, "calculate_cmc_inputs");
}

json calculate_advanced_cmc_inputs(json cmcInputsJson) {
    // The advanced entry REQUIRES the pinned inductance (the legacy AdvancedCommonModeChoke ctor
    // did j.at("desiredInductance")); Kirchhoff treats its presence as the mode switch.
    if (!cmcInputsJson.contains("desiredInductance")) {
        return json{{"error", "calculate_advanced_cmc_inputs: 'desiredInductance' is required"}};
    }
    return cmc_inputs_via_kirchhoff(cmcInputsJson, "calculate_advanced_cmc_inputs");
}

} // namespace

void register_cmc_bindings(py::module& m) {
    m.def("calculate_cmc_inputs", &calculate_cmc_inputs,
        "Build MAS Inputs (designRequirements + operatingPoints) for a CMC from "
        "wizard params (operatingVoltage, operatingCurrent, lineFrequency, "
        "numberOfWindings, and an impedance/insertion-loss/noise spec). Mirrors "
        "the WASM `calculate_cmc_inputs` used by el-choker's CMC wizard. "
        "Delegates to Kirchhoff api::design_cmc.",
        py::arg("cmc_inputs"));
    m.def("calculate_advanced_cmc_inputs", &calculate_advanced_cmc_inputs,
        "Advanced-mode CMC inputs builder (user supplies `desiredInductance` + "
        "`designFrequency` directly rather than a spec). Delegates to Kirchhoff "
        "api::design_cmc.",
        py::arg("cmc_inputs"));
}

} // namespace PyMKF
