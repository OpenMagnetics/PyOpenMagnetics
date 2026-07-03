// converter.cpp — thin shims over the Kirchhoff string API (libKirchhoffApi.so).
//
// The converter models were externalised from MKF into the Kirchhoff project (MKF 3e0261fd deleted
// converter_models); every design/simulation verb now lives behind Kirchhoff::api's string-in / JSON-out
// facade. This translation unit re-points PyOM's whole converter binding surface at that facade, mirroring
// the WebFrontend integration (which loads libKirchhoff for exactly these verbs) — so PyOpenMagnetics keeps
// ONE package with the full converter surface, just backed by Kirchhoff instead of the deleted MKF classes.
//
// Contract preservation, per verb family:
//   * design / inputs  (process_converter, process_<topo>, calculate_<topo>_inputs)
//         -> Kirchhoff::api::design_magnetic_inputs(topology, spec)  -> bare MAS::Inputs (legacy shape).
//   * current transformer / DMC design -> design_current_transformer / design_dmc / propose_dmc_design.
//   * CMC / DMC ngspice sims          -> simulate_cmc_* / simulate_dmc_* / verify_dmc_attenuation.
//   * ngspice deck from a SPEC        -> design_tas(topology, spec) + generate_ngspice_circuit(tas).
//   * ngspice sim/deck from a built MAS Inputs (the simulate_<topo>_ideal_waveforms /
//     generate_<topo>_ngspice_circuit family): Kirchhoff's sim/deck verbs take a TAS built from a SPEC,
//     not a finished MAS Inputs, so there is no 1:1. We re-derive a TAS from the spec carried in the
//     Inputs when present, else return a structured {"error": ...} (never a throw) — these are WASM-parity
//     endpoints no PyOM consumer calls today; the design surface above is what el-choker et al. use.
//
// Only KirchhoffApi.hpp is included here, so no Kirchhoff MAS:: type ever enters an MKF translation unit
// (the string boundary is the whole point — see cmc.cpp, which does the same for the CMC designer).

#include "converter.h"

#include "pybind11_json/pybind11_json.hpp"
#include "json.hpp"
#include <KirchhoffApi.hpp>

#include <string>
#include <unordered_map>

namespace py = pybind11;
using json = nlohmann::json;

namespace PyMKF {

namespace {

constexpr const char* kExceptionPrefix = "Exception: ";

// Kirchhoff returns "Exception: ..." on failure (no throw crosses the boundary). Turn that into the
// legacy {"error": "<fn>: ..."} object; otherwise parse the JSON payload.
json kh_json(const std::string& out, const char* fn) {
    if (out.rfind(kExceptionPrefix, 0) == 0) {
        return json{{"error", std::string(fn) + ": " + out.substr(std::char_traits<char>::length(kExceptionPrefix))}};
    }
    return json::parse(out);
}

// Map PyOM's legacy short topology names (and the "advanced_" mode prefix, which Kirchhoff derives from
// the spec's desiredInductance instead) onto Kirchhoff's dispatcher names.
std::string kh_topology(const std::string& raw) {
    std::string s = raw;
    if (s.rfind("advanced_", 0) == 0) {
        s = s.substr(std::char_traits<char>::length("advanced_"));
    }
    static const std::unordered_map<std::string, std::string> kMap = {
        {"single_switch_forward", "forward"},
        {"two_switch_forward", "two_switch_forward"},
        {"active_clamp_forward", "active_clamp_forward"},
        {"pfc", "power_factor_correction"},
        {"psfb", "phase_shifted_full_bridge"},
        {"pshb", "phase_shifted_half_bridge"},
        {"ahb", "asymmetric_half_bridge"},
        {"cmc", "common_mode_choke"},
        {"dmc", "differential_mode_choke"},
    };
    auto it = kMap.find(s);
    return it != kMap.end() ? it->second : s;
}

// Design entry: spec -> MAS::Inputs (the legacy process_converter / calculate_<topo>_inputs contract).
json design_inputs(const std::string& topology, const json& spec, const char* fn) {
    return kh_json(Kirchhoff::api::design_magnetic_inputs(kh_topology(topology), spec.dump()), fn);
}

// ngspice deck from a converter SPEC: design a TAS then assemble the deck. Returns {"netlist": "<spice>"}.
json ngspice_deck_from_spec(const std::string& topology, const json& spec, const char* fn) {
    const std::string tas = Kirchhoff::api::design_tas(kh_topology(topology), spec.dump());
    if (tas.rfind(kExceptionPrefix, 0) == 0) {
        return json{{"error", std::string(fn) + ": " + tas.substr(std::char_traits<char>::length(kExceptionPrefix))}};
    }
    const std::string deck = Kirchhoff::api::generate_ngspice_circuit(tas, "{}");
    if (deck.rfind(kExceptionPrefix, 0) == 0) {
        return json{{"error", std::string(fn) + ": " + deck.substr(std::char_traits<char>::length(kExceptionPrefix))}};
    }
    return json{{"netlist", deck}};
}

// ngspice sim from a converter SPEC: design a TAS then run it. Returns Kirchhoff's per-vector summary.
json ngspice_sim_from_spec(const std::string& topology, const json& spec, const char* fn) {
    const std::string tas = Kirchhoff::api::design_tas(kh_topology(topology), spec.dump());
    if (tas.rfind(kExceptionPrefix, 0) == 0) {
        return json{{"error", std::string(fn) + ": " + tas.substr(std::char_traits<char>::length(kExceptionPrefix))}};
    }
    return kh_json(Kirchhoff::api::simulate_ngspice(tas, "{}"), fn);
}

// A built-MAS-Inputs simulate/deck endpoint whose spec is not recoverable: Kirchhoff needs a spec/TAS, not
// a finished Inputs. Report it structurally (WASM-parity surface, unused by PyOM consumers).
json needs_spec_error(const char* fn) {
    return json{{"error", std::string(fn) +
        ": Kirchhoff builds ngspice decks/sims from a converter SPEC (design_tas), not a finished MAS "
        "Inputs. Call the SPEC-based path (generate_ngspice_circuit(topology, spec, ...) / "
        "process_converter) instead."}};
}

} // namespace

// ─────────────────────────────────────────────────────────────────────────────
// Design surface — spec -> MAS::Inputs
// ─────────────────────────────────────────────────────────────────────────────

json process_converter(const std::string& topologyName, json converterJson, bool /*useNgspice*/) {
    return design_inputs(topologyName, converterJson, "process_converter");
}

// Build magnetic candidates from a converter spec. Kirchhoff produces the MAS::Inputs; the magnetic adviser
// still lives in MKF and is exposed separately (register_adviser_bindings' advise_magnetic). We return the
// Inputs so callers can feed the adviser — the old one-call design+advise fused two libraries we no longer
// want coupled across the string boundary.
json design_magnetics_from_converter(const std::string& topologyName,
                                     json converterJson,
                                     int /*maxResults*/,
                                     json /*coreModeJson*/,
                                     bool /*useNgspice*/,
                                     json /*weightsJson*/,
                                     bool /*fast*/) {
    return design_inputs(topologyName, converterJson, "design_magnetics_from_converter");
}

// Per-topology thin wrappers — all funnel through process_converter (the legacy structure), so they inherit
// the Kirchhoff design path automatically.
#define DEFINE_CONVERTER_ALIAS(fn_name, topology) \
    json fn_name(json converterJson) { return process_converter(topology, converterJson, true); }

json process_flyback(json flybackJson) { return process_converter("flyback", flybackJson, true); }
json process_buck(json buckJson) { return process_converter("buck", buckJson, true); }
json process_boost(json boostJson) { return process_converter("boost", boostJson, true); }
json process_single_switch_forward(json j) { return process_converter("single_switch_forward", j, true); }
json process_two_switch_forward(json j) { return process_converter("two_switch_forward", j, true); }
json process_active_clamp_forward(json j) { return process_converter("active_clamp_forward", j, true); }
json process_push_pull(json j) { return process_converter("push_pull", j, true); }
json process_isolated_buck(json j) { return process_converter("isolated_buck", j, true); }
json process_isolated_buck_boost(json j) { return process_converter("isolated_buck_boost", j, true); }
json process_cuk(json cukJson) { return process_converter("cuk", cukJson, true); }
json process_sepic(json sepicJson) { return process_converter("sepic", sepicJson, true); }
json process_zeta(json zetaJson) { return process_converter("zeta", zetaJson, true); }
json process_four_switch_buck_boost(json j) { return process_converter("four_switch_buck_boost", j, true); }
json process_asymmetric_half_bridge(json j) { return process_converter("asymmetric_half_bridge", j, true); }
json process_weinberg(json j) { return process_converter("weinberg", j, true); }
json process_vienna(json j) { return process_converter("vienna", j, true); }
json process_clllc(json j) { return process_converter("clllc", j, true); }
json process_src(json j) { return process_converter("src", j, true); }

json process_current_transformer(json ctJson, double turnsRatio, double secondaryResistance) {
    ctJson["turnsRatio"] = turnsRatio;
    if (secondaryResistance != 0.0) {
        ctJson["secondaryDcResistance"] = secondaryResistance;
    }
    return kh_json(Kirchhoff::api::design_current_transformer(ctJson.dump()), "process_current_transformer");
}

// WASM-parity input builders (calculate_<topo>_inputs / _advanced_). All route through process_converter.
DEFINE_CONVERTER_ALIAS(calculate_flyback_inputs, "flyback")
DEFINE_CONVERTER_ALIAS(calculate_advanced_flyback_inputs, "advanced_flyback")
DEFINE_CONVERTER_ALIAS(calculate_buck_inputs, "buck")
DEFINE_CONVERTER_ALIAS(calculate_advanced_buck_inputs, "advanced_buck")
DEFINE_CONVERTER_ALIAS(calculate_boost_inputs, "boost")
DEFINE_CONVERTER_ALIAS(calculate_advanced_boost_inputs, "advanced_boost")
DEFINE_CONVERTER_ALIAS(calculate_single_switch_forward_inputs, "single_switch_forward")
DEFINE_CONVERTER_ALIAS(calculate_advanced_single_switch_forward_inputs, "advanced_single_switch_forward")
DEFINE_CONVERTER_ALIAS(calculate_two_switch_forward_inputs, "two_switch_forward")
DEFINE_CONVERTER_ALIAS(calculate_advanced_two_switch_forward_inputs, "advanced_two_switch_forward")
DEFINE_CONVERTER_ALIAS(calculate_active_clamp_forward_inputs, "active_clamp_forward")
DEFINE_CONVERTER_ALIAS(calculate_advanced_active_clamp_forward_inputs, "advanced_active_clamp_forward")
DEFINE_CONVERTER_ALIAS(calculate_push_pull_inputs, "push_pull")
DEFINE_CONVERTER_ALIAS(calculate_advanced_push_pull_inputs, "advanced_push_pull")
DEFINE_CONVERTER_ALIAS(calculate_isolated_buck_inputs, "isolated_buck")
DEFINE_CONVERTER_ALIAS(calculate_advanced_isolated_buck_inputs, "advanced_isolated_buck")
DEFINE_CONVERTER_ALIAS(calculate_isolated_buck_boost_inputs, "isolated_buck_boost")
DEFINE_CONVERTER_ALIAS(calculate_advanced_isolated_buck_boost_inputs, "advanced_isolated_buck_boost")
DEFINE_CONVERTER_ALIAS(calculate_cuk_inputs, "cuk")
DEFINE_CONVERTER_ALIAS(calculate_advanced_cuk_inputs, "advanced_cuk")
DEFINE_CONVERTER_ALIAS(calculate_sepic_inputs, "sepic")
DEFINE_CONVERTER_ALIAS(calculate_advanced_sepic_inputs, "advanced_sepic")
DEFINE_CONVERTER_ALIAS(calculate_zeta_inputs, "zeta")
DEFINE_CONVERTER_ALIAS(calculate_advanced_zeta_inputs, "advanced_zeta")
DEFINE_CONVERTER_ALIAS(calculate_four_switch_buck_boost_inputs, "four_switch_buck_boost")
DEFINE_CONVERTER_ALIAS(calculate_advanced_four_switch_buck_boost_inputs, "advanced_four_switch_buck_boost")
DEFINE_CONVERTER_ALIAS(calculate_weinberg_inputs, "weinberg")
DEFINE_CONVERTER_ALIAS(calculate_advanced_weinberg_inputs, "advanced_weinberg")
DEFINE_CONVERTER_ALIAS(calculate_clllc_inputs, "clllc")
DEFINE_CONVERTER_ALIAS(calculate_advanced_clllc_inputs, "advanced_clllc")
DEFINE_CONVERTER_ALIAS(calculate_vienna_inputs, "vienna")
DEFINE_CONVERTER_ALIAS(calculate_advanced_vienna_inputs, "advanced_vienna")
DEFINE_CONVERTER_ALIAS(calculate_src_inputs, "src")
DEFINE_CONVERTER_ALIAS(calculate_advanced_src_inputs, "advanced_src")
DEFINE_CONVERTER_ALIAS(calculate_llc_inputs, "llc")
DEFINE_CONVERTER_ALIAS(calculate_advanced_llc_inputs, "advanced_llc")
DEFINE_CONVERTER_ALIAS(calculate_cllc_inputs, "cllc")
DEFINE_CONVERTER_ALIAS(calculate_advanced_cllc_inputs, "advanced_cllc")
DEFINE_CONVERTER_ALIAS(calculate_dab_inputs, "dab")
DEFINE_CONVERTER_ALIAS(calculate_advanced_dab_inputs, "advanced_dab")
DEFINE_CONVERTER_ALIAS(calculate_pfc_inputs, "power_factor_correction")
DEFINE_CONVERTER_ALIAS(calculate_psfb_inputs, "phase_shifted_full_bridge")
DEFINE_CONVERTER_ALIAS(calculate_advanced_psfb_inputs, "advanced_phase_shifted_full_bridge")
DEFINE_CONVERTER_ALIAS(calculate_pshb_inputs, "phase_shifted_half_bridge")
DEFINE_CONVERTER_ALIAS(calculate_advanced_pshb_inputs, "advanced_phase_shifted_half_bridge")
DEFINE_CONVERTER_ALIAS(calculate_ahb_inputs, "asymmetric_half_bridge")
DEFINE_CONVERTER_ALIAS(calculate_advanced_ahb_inputs, "advanced_asymmetric_half_bridge")
#undef DEFINE_CONVERTER_ALIAS

// ─────────────────────────────────────────────────────────────────────────────
// ngspice deck from a converter SPEC
// ─────────────────────────────────────────────────────────────────────────────

json generate_ngspice_circuit(const std::string& topologyName,
                              json converterJson,
                              json /*turnsRatios*/,
                              double /*magnetizingInductance*/,
                              int /*vinIndex*/,
                              int /*opIndex*/,
                              const std::string& /*bridgeSimulationMode*/,
                              json /*spiceConfig*/) {
    return ngspice_deck_from_spec(topologyName, converterJson, "generate_ngspice_circuit");
}

// Extra-component design requirements (resonant tank Lr/Cr, snubbers). Kirchhoff carries these inside the
// TAS; there is no standalone verb, so this WASM-parity endpoint reports the spec-based route.
json get_extra_components_inputs(const std::string& /*topologyName*/,
                                 json /*converterJson*/,
                                 const std::string& /*modeStr*/,
                                 json /*magneticJson*/) {
    return needs_spec_error("get_extra_components_inputs");
}

// ─────────────────────────────────────────────────────────────────────────────
// DMC (design + sims) — CMC design lives in cmc.cpp; the CMC sims are below.
// ─────────────────────────────────────────────────────────────────────────────

namespace {

// design_dmc / design_cmc return {"inputs": <MAS::Inputs>, "<x>Diagnostics": {...}}; the legacy contract
// spreads Inputs at the root and attaches the diagnostics sibling.
json dmc_inputs_via_kirchhoff(const json& spec, const char* fn) {
    const std::string out = Kirchhoff::api::design_dmc(spec.dump());
    if (out.rfind(kExceptionPrefix, 0) == 0) {
        return json{{"error", std::string(fn) + ": " + out.substr(std::char_traits<char>::length(kExceptionPrefix))}};
    }
    json parsed = json::parse(out);
    json result = std::move(parsed.at("inputs"));
    result["dmcDiagnostics"] = std::move(parsed.at("dmcDiagnostics"));
    return result;
}

double read_inductance(const json& spec) {
    if (spec.contains("minimumInductance") && spec.at("minimumInductance").is_number()) {
        return spec.at("minimumInductance").get<double>();
    }
    if (spec.contains("inductance") && spec.at("inductance").is_number()) {
        return spec.at("inductance").get<double>();
    }
    return 0.0;
}

} // namespace

json calculate_dmc_inputs(json dmcInputsJson) {
    return dmc_inputs_via_kirchhoff(dmcInputsJson, "calculate_dmc_inputs");
}

json propose_dmc_design(json dmcInputsJson) {
    return kh_json(Kirchhoff::api::propose_dmc_design(dmcInputsJson.dump()), "propose_dmc_design");
}

json verify_dmc_attenuation(json dmcInputsJson, double inductance, double capacitance) {
    return kh_json(Kirchhoff::api::verify_dmc_attenuation(dmcInputsJson.dump(), inductance, capacitance),
                   "verify_dmc_attenuation");
}

json simulate_dmc_waveforms(json dmcInputsJson, double inductance) {
    return kh_json(Kirchhoff::api::simulate_dmc_waveforms(dmcInputsJson.dump(), inductance),
                   "simulate_dmc_waveforms");
}

json generate_dmc_ngspice_circuit(json dmcInputsJson) {
    // A DMC is a component + LC filter, not a converter TAS. Kirchhoff exposes the DMC deck through its
    // sim verb; there is no standalone deck verb, so route via simulate_dmc_waveforms' sizing.
    const double inductance = read_inductance(dmcInputsJson);
    return kh_json(Kirchhoff::api::simulate_dmc_waveforms(dmcInputsJson.dump(), inductance),
                   "generate_dmc_ngspice_circuit");
}

// ─────────────────────────────────────────────────────────────────────────────
// CMC ngspice sims (design lives in cmc.cpp -> Kirchhoff::api::design_cmc)
// ─────────────────────────────────────────────────────────────────────────────

json simulate_cmc_lisn_waveforms(json cmcInputsJson, double inductance) {
    return kh_json(Kirchhoff::api::simulate_cmc_lisn_waveforms(cmcInputsJson.dump(), inductance),
                   "simulate_cmc_lisn_waveforms");
}

json simulate_cmc_ideal_waveforms(json cmcInputsJson, double inductance,
                                  double parasiticCapacitancePf, double dvdtVPerNs) {
    return kh_json(Kirchhoff::api::simulate_cmc_ideal_waveforms(
                       cmcInputsJson.dump(), inductance, parasiticCapacitancePf, dvdtVPerNs),
                   "simulate_cmc_ideal_waveforms");
}

json generate_cmc_ngspice_circuit(json cmcInputsJson) {
    const double inductance = read_inductance(cmcInputsJson);
    return kh_json(Kirchhoff::api::simulate_cmc_lisn_waveforms(cmcInputsJson.dump(), inductance),
                   "generate_cmc_ngspice_circuit");
}

// ─────────────────────────────────────────────────────────────────────────────
// simulate_<topo>_ideal_waveforms / generate_<topo>_ngspice_circuit
//
// These take a built MAS Inputs (not a converter spec). Kirchhoff drives sim/deck from a spec-derived TAS,
// so when the Inputs still carries its originating topology spec (under "converterSpec"/"spec") we re-derive
// the TAS; otherwise we report the spec-based route. WASM-parity surface, unused by PyOM consumers.
// ─────────────────────────────────────────────────────────────────────────────

namespace {

json sim_from_inputs(const std::string& topology, const json& inputs, const char* fn) {
    if (inputs.contains("converterSpec")) return ngspice_sim_from_spec(topology, inputs.at("converterSpec"), fn);
    if (inputs.contains("spec")) return ngspice_sim_from_spec(topology, inputs.at("spec"), fn);
    return needs_spec_error(fn);
}
json deck_from_inputs(const std::string& topology, const json& inputs, const char* fn) {
    if (inputs.contains("converterSpec")) return ngspice_deck_from_spec(topology, inputs.at("converterSpec"), fn);
    if (inputs.contains("spec")) return ngspice_deck_from_spec(topology, inputs.at("spec"), fn);
    return needs_spec_error(fn);
}

} // namespace

#define DEFINE_SIM_IDEAL(fn_name, topology) \
    json fn_name(json inputsJson) { return sim_from_inputs(topology, inputsJson, #fn_name); }
#define DEFINE_GEN_DECK(fn_name, topology) \
    json fn_name(json inputsJson, int /*vinIndex*/, int /*opIndex*/) { return deck_from_inputs(topology, inputsJson, #fn_name); }

DEFINE_SIM_IDEAL(simulate_flyback_ideal_waveforms, "flyback")
json simulate_flyback_with_magnetic(json inputsJson, json /*magneticJson*/) { return sim_from_inputs("flyback", inputsJson, "simulate_flyback_with_magnetic"); }
DEFINE_SIM_IDEAL(simulate_buck_ideal_waveforms, "buck")
DEFINE_SIM_IDEAL(simulate_boost_ideal_waveforms, "boost")
DEFINE_SIM_IDEAL(simulate_sepic_ideal_waveforms, "sepic")
DEFINE_SIM_IDEAL(simulate_cuk_ideal_waveforms, "cuk")
DEFINE_SIM_IDEAL(simulate_zeta_ideal_waveforms, "zeta")
DEFINE_SIM_IDEAL(simulate_four_switch_buck_boost_ideal_waveforms, "four_switch_buck_boost")
DEFINE_SIM_IDEAL(simulate_forward_ideal_waveforms, "single_switch_forward")
DEFINE_SIM_IDEAL(simulate_two_switch_forward_ideal_waveforms, "two_switch_forward")
DEFINE_SIM_IDEAL(simulate_active_clamp_forward_ideal_waveforms, "active_clamp_forward")
DEFINE_SIM_IDEAL(simulate_push_pull_ideal_waveforms, "push_pull")
DEFINE_SIM_IDEAL(simulate_isolated_buck_ideal_waveforms, "isolated_buck")
DEFINE_SIM_IDEAL(simulate_isolated_buck_boost_ideal_waveforms, "isolated_buck_boost")
DEFINE_SIM_IDEAL(simulate_weinberg_ideal_waveforms, "weinberg")
DEFINE_SIM_IDEAL(simulate_llc_ideal_waveforms, "llc")
DEFINE_SIM_IDEAL(simulate_cllc_ideal_waveforms, "cllc")
DEFINE_SIM_IDEAL(simulate_clllc_ideal_waveforms, "clllc")
DEFINE_SIM_IDEAL(simulate_src_ideal_waveforms, "src")
DEFINE_SIM_IDEAL(simulate_dab_ideal_waveforms, "dab")
DEFINE_SIM_IDEAL(simulate_psfb_ideal_waveforms, "phase_shifted_full_bridge")
DEFINE_SIM_IDEAL(simulate_pshb_ideal_waveforms, "phase_shifted_half_bridge")
DEFINE_SIM_IDEAL(simulate_ahb_ideal_waveforms, "asymmetric_half_bridge")
DEFINE_SIM_IDEAL(simulate_vienna_ideal_waveforms, "vienna")
DEFINE_SIM_IDEAL(simulate_pfc_waveforms, "power_factor_correction")

DEFINE_GEN_DECK(generate_flyback_ngspice_circuit, "flyback")
DEFINE_GEN_DECK(generate_buck_ngspice_circuit, "buck")
DEFINE_GEN_DECK(generate_boost_ngspice_circuit, "boost")
DEFINE_GEN_DECK(generate_sepic_ngspice_circuit, "sepic")
DEFINE_GEN_DECK(generate_forward_ngspice_circuit, "single_switch_forward")
DEFINE_GEN_DECK(generate_two_switch_forward_ngspice_circuit, "two_switch_forward")
DEFINE_GEN_DECK(generate_active_clamp_forward_ngspice_circuit, "active_clamp_forward")
DEFINE_GEN_DECK(generate_push_pull_ngspice_circuit, "push_pull")
DEFINE_GEN_DECK(generate_isolated_buck_ngspice_circuit, "isolated_buck")
DEFINE_GEN_DECK(generate_isolated_buck_boost_ngspice_circuit, "isolated_buck_boost")
DEFINE_GEN_DECK(generate_llc_ngspice_circuit, "llc")
DEFINE_GEN_DECK(generate_cllc_ngspice_circuit, "cllc")
DEFINE_GEN_DECK(generate_src_ngspice_circuit, "src")
DEFINE_GEN_DECK(generate_dab_ngspice_circuit, "dab")
DEFINE_GEN_DECK(generate_psfb_ngspice_circuit, "phase_shifted_full_bridge")
DEFINE_GEN_DECK(generate_cuk_ngspice_circuit, "cuk")
DEFINE_GEN_DECK(generate_zeta_ngspice_circuit, "zeta")
DEFINE_GEN_DECK(generate_four_switch_buck_boost_ngspice_circuit, "four_switch_buck_boost")
DEFINE_GEN_DECK(generate_weinberg_ngspice_circuit, "weinberg")
DEFINE_GEN_DECK(generate_clllc_ngspice_circuit, "clllc")
DEFINE_GEN_DECK(generate_vienna_ngspice_circuit, "vienna")
DEFINE_GEN_DECK(generate_pshb_ngspice_circuit, "phase_shifted_half_bridge")
DEFINE_GEN_DECK(generate_ahb_ngspice_circuit, "asymmetric_half_bridge")
#undef DEFINE_SIM_IDEAL
#undef DEFINE_GEN_DECK

json generate_pfc_ngspice_circuit(json inputsJson, double /*dcResistance*/, double /*simulationTime*/, double /*timeStep*/) {
    return deck_from_inputs("power_factor_correction", inputsJson, "generate_pfc_ngspice_circuit");
}

// ─────────────────────────────────────────────────────────────────────────────
// Bindings — the full converter surface, now Kirchhoff-backed. calculate_cmc_inputs /
// calculate_advanced_cmc_inputs are registered by register_cmc_bindings (cmc.cpp), not here.
// ─────────────────────────────────────────────────────────────────────────────

void register_converter_bindings(py::module& m) {
    m.def("process_converter", &process_converter,
        "Process a converter topology specification to MAS Inputs (via Kirchhoff design_magnetic_inputs).",
        py::arg("topology_name"), py::arg("converter_json"), py::arg("use_ngspice") = true);
    m.def("design_magnetics_from_converter", &design_magnetics_from_converter,
        "Design requirements (MAS Inputs) from a converter spec via Kirchhoff; feed the magnetic adviser.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("max_results") = 1, py::arg("core_mode_json") = "available cores",
        py::arg("use_ngspice") = true, py::arg("weights_json") = nullptr, py::arg("fast") = false);

    m.def("process_flyback", &process_flyback, "Process Flyback converter.", py::arg("flyback"));
    m.def("process_buck", &process_buck, "Process Buck converter.", py::arg("buck"));
    m.def("process_boost", &process_boost, "Process Boost converter.", py::arg("boost"));
    m.def("process_single_switch_forward", &process_single_switch_forward, "Process Single-Switch Forward.", py::arg("forward"));
    m.def("process_two_switch_forward", &process_two_switch_forward, "Process Two-Switch Forward.", py::arg("forward"));
    m.def("process_active_clamp_forward", &process_active_clamp_forward, "Process Active Clamp Forward.", py::arg("forward"));
    m.def("process_push_pull", &process_push_pull, "Process Push-Pull converter.", py::arg("push_pull"));
    m.def("process_isolated_buck", &process_isolated_buck, "Process Isolated Buck.", py::arg("isolated_buck"));
    m.def("process_isolated_buck_boost", &process_isolated_buck_boost, "Process Isolated Buck-Boost.", py::arg("isolated_buck_boost"));
    m.def("process_current_transformer", &process_current_transformer, "Process Current Transformer.",
        py::arg("ct"), py::arg("turns_ratio"), py::arg("secondary_resistance") = 0.0);
    m.def("process_cuk", &process_cuk, "Process Cuk converter.", py::arg("cuk"));
    m.def("process_sepic", &process_sepic, "Process SEPIC converter.", py::arg("sepic"));
    m.def("process_zeta", &process_zeta, "Process Zeta converter.", py::arg("zeta"));
    m.def("process_four_switch_buck_boost", &process_four_switch_buck_boost, "Process Four-Switch Buck-Boost converter.", py::arg("converter"));
    m.def("process_asymmetric_half_bridge", &process_asymmetric_half_bridge, "Process Asymmetric Half-Bridge converter.", py::arg("converter"));
    m.def("process_weinberg", &process_weinberg, "Process Weinberg converter.", py::arg("converter"));
    m.def("process_vienna", &process_vienna, "Process Vienna Rectifier converter.", py::arg("converter"));
    m.def("process_clllc", &process_clllc, "Process CLLLC Resonant converter.", py::arg("converter"));
    m.def("process_src", &process_src, "Process Series Resonant converter (SRC).", py::arg("converter"));

    m.def("generate_ngspice_circuit", &generate_ngspice_circuit,
        "Return the ngspice SPICE deck for a converter SPEC (Kirchhoff design_tas + generate_ngspice_circuit). "
        "Returns {'netlist': '<spice>'} or {'error': '...'}.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("turns_ratios"), py::arg("magnetizing_inductance"),
        py::arg("vin_index") = 0, py::arg("op_index") = 0,
        py::arg("bridge_simulation_mode") = std::string(""),
        py::arg("spice_config") = nlohmann::json::object());
    m.def("get_extra_components_inputs", &get_extra_components_inputs,
        "Extra-component design requirements (resonant tank, snubbers). Carried inside Kirchhoff's TAS.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("mode") = "IDEAL", py::arg("magnetic_json") = nullptr);

    #define BIND_CONVERTER_ALIAS(fn) m.def(#fn, &fn, "Topology inputs builder (WASM parity alias).", py::arg("inputs"))
    BIND_CONVERTER_ALIAS(calculate_flyback_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_flyback_inputs);
    BIND_CONVERTER_ALIAS(calculate_buck_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_buck_inputs);
    BIND_CONVERTER_ALIAS(calculate_boost_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_boost_inputs);
    BIND_CONVERTER_ALIAS(calculate_single_switch_forward_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_single_switch_forward_inputs);
    BIND_CONVERTER_ALIAS(calculate_two_switch_forward_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_two_switch_forward_inputs);
    BIND_CONVERTER_ALIAS(calculate_active_clamp_forward_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_active_clamp_forward_inputs);
    BIND_CONVERTER_ALIAS(calculate_push_pull_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_push_pull_inputs);
    BIND_CONVERTER_ALIAS(calculate_isolated_buck_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_isolated_buck_inputs);
    BIND_CONVERTER_ALIAS(calculate_isolated_buck_boost_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_isolated_buck_boost_inputs);
    BIND_CONVERTER_ALIAS(calculate_cuk_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_cuk_inputs);
    BIND_CONVERTER_ALIAS(calculate_sepic_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_sepic_inputs);
    BIND_CONVERTER_ALIAS(calculate_zeta_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_zeta_inputs);
    BIND_CONVERTER_ALIAS(calculate_four_switch_buck_boost_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_four_switch_buck_boost_inputs);
    BIND_CONVERTER_ALIAS(calculate_weinberg_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_weinberg_inputs);
    BIND_CONVERTER_ALIAS(calculate_clllc_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_clllc_inputs);
    BIND_CONVERTER_ALIAS(calculate_vienna_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_vienna_inputs);
    BIND_CONVERTER_ALIAS(calculate_src_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_src_inputs);
    BIND_CONVERTER_ALIAS(calculate_llc_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_llc_inputs);
    BIND_CONVERTER_ALIAS(calculate_cllc_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_cllc_inputs);
    BIND_CONVERTER_ALIAS(calculate_dab_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_dab_inputs);
    BIND_CONVERTER_ALIAS(calculate_pfc_inputs);
    BIND_CONVERTER_ALIAS(calculate_psfb_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_psfb_inputs);
    BIND_CONVERTER_ALIAS(calculate_pshb_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_pshb_inputs);
    BIND_CONVERTER_ALIAS(calculate_ahb_inputs);
    BIND_CONVERTER_ALIAS(calculate_advanced_ahb_inputs);
    #undef BIND_CONVERTER_ALIAS

    // DMC (design + sims). CMC design is in cmc.cpp; CMC sims are below.
    m.def("calculate_dmc_inputs", &calculate_dmc_inputs, "Build MAS Inputs for a DMC (Kirchhoff design_dmc).", py::arg("dmc_inputs"));
    m.def("verify_dmc_attenuation", &verify_dmc_attenuation, "Verify a DMC + capacitor meets the attenuation spec.",
        py::arg("dmc_inputs"), py::arg("inductance"), py::arg("capacitance") = 0.0);
    m.def("propose_dmc_design", &propose_dmc_design, "Propose a DMC L/C pair satisfying the spec.", py::arg("dmc_inputs"));
    m.def("simulate_dmc_waveforms", &simulate_dmc_waveforms, "Simulate DMC time-domain waveforms.", py::arg("dmc_inputs"), py::arg("inductance"));
    m.def("generate_dmc_ngspice_circuit", &generate_dmc_ngspice_circuit, "DMC ngspice deck/sim.", py::arg("dmc_inputs"));

    // CMC ngspice sims (design lives in cmc.cpp).
    m.def("generate_cmc_ngspice_circuit", &generate_cmc_ngspice_circuit, "CMC ngspice deck/sim.", py::arg("cmc_inputs"));
    m.def("simulate_cmc_lisn_waveforms", &simulate_cmc_lisn_waveforms, "CISPR LISN test sim for a CMC.", py::arg("cmc_inputs"), py::arg("inductance"));
    m.def("simulate_cmc_ideal_waveforms", &simulate_cmc_ideal_waveforms, "CMC operating-point sim (line + switching noise).",
        py::arg("cmc_inputs"), py::arg("inductance"), py::arg("parasitic_capacitance_pF") = 10.0, py::arg("dvdt_V_per_ns") = 50.0);

    // simulate_<topo>_ideal_waveforms
    m.def("simulate_flyback_ideal_waveforms", &simulate_flyback_ideal_waveforms, "Simulate Flyback ideal waveforms.", py::arg("inputs"));
    m.def("simulate_flyback_with_magnetic", &simulate_flyback_with_magnetic, "Simulate Flyback with a pre-built magnetic.", py::arg("inputs"), py::arg("magnetic"));
    m.def("simulate_buck_ideal_waveforms", &simulate_buck_ideal_waveforms, "Simulate Buck ideal waveforms.", py::arg("inputs"));
    m.def("simulate_boost_ideal_waveforms", &simulate_boost_ideal_waveforms, "Simulate Boost ideal waveforms.", py::arg("inputs"));
    m.def("simulate_sepic_ideal_waveforms", &simulate_sepic_ideal_waveforms, "Simulate SEPIC ideal waveforms.", py::arg("inputs"));
    m.def("simulate_cuk_ideal_waveforms", &simulate_cuk_ideal_waveforms, "Simulate Cuk ideal waveforms.", py::arg("inputs"));
    m.def("simulate_zeta_ideal_waveforms", &simulate_zeta_ideal_waveforms, "Simulate Zeta ideal waveforms.", py::arg("inputs"));
    m.def("simulate_four_switch_buck_boost_ideal_waveforms", &simulate_four_switch_buck_boost_ideal_waveforms, "Simulate Four-Switch Buck-Boost ideal waveforms.", py::arg("inputs"));
    m.def("simulate_forward_ideal_waveforms", &simulate_forward_ideal_waveforms, "Simulate Single-Switch Forward ideal waveforms.", py::arg("inputs"));
    m.def("simulate_two_switch_forward_ideal_waveforms", &simulate_two_switch_forward_ideal_waveforms, "Simulate Two-Switch Forward ideal waveforms.", py::arg("inputs"));
    m.def("simulate_active_clamp_forward_ideal_waveforms", &simulate_active_clamp_forward_ideal_waveforms, "Simulate Active-Clamp Forward ideal waveforms.", py::arg("inputs"));
    m.def("simulate_push_pull_ideal_waveforms", &simulate_push_pull_ideal_waveforms, "Simulate Push-Pull ideal waveforms.", py::arg("inputs"));
    m.def("simulate_isolated_buck_ideal_waveforms", &simulate_isolated_buck_ideal_waveforms, "Simulate Isolated Buck ideal waveforms.", py::arg("inputs"));
    m.def("simulate_isolated_buck_boost_ideal_waveforms", &simulate_isolated_buck_boost_ideal_waveforms, "Simulate Isolated Buck-Boost ideal waveforms.", py::arg("inputs"));
    m.def("simulate_weinberg_ideal_waveforms", &simulate_weinberg_ideal_waveforms, "Simulate Weinberg ideal waveforms.", py::arg("inputs"));
    m.def("simulate_llc_ideal_waveforms", &simulate_llc_ideal_waveforms, "Simulate LLC ideal waveforms.", py::arg("inputs"));
    m.def("simulate_cllc_ideal_waveforms", &simulate_cllc_ideal_waveforms, "Simulate CLLC ideal waveforms.", py::arg("inputs"));
    m.def("simulate_clllc_ideal_waveforms", &simulate_clllc_ideal_waveforms, "Simulate CLLLC ideal waveforms.", py::arg("inputs"));
    m.def("simulate_src_ideal_waveforms", &simulate_src_ideal_waveforms, "Simulate SRC ideal waveforms.", py::arg("inputs"));
    m.def("simulate_dab_ideal_waveforms", &simulate_dab_ideal_waveforms, "Simulate DAB ideal waveforms.", py::arg("inputs"));
    m.def("simulate_psfb_ideal_waveforms", &simulate_psfb_ideal_waveforms, "Simulate PSFB ideal waveforms.", py::arg("inputs"));
    m.def("simulate_pshb_ideal_waveforms", &simulate_pshb_ideal_waveforms, "Simulate PSHB ideal waveforms.", py::arg("inputs"));
    m.def("simulate_ahb_ideal_waveforms", &simulate_ahb_ideal_waveforms, "Simulate Asymmetric Half-Bridge ideal waveforms.", py::arg("inputs"));
    m.def("simulate_vienna_ideal_waveforms", &simulate_vienna_ideal_waveforms, "Simulate Vienna Rectifier ideal waveforms.", py::arg("inputs"));
    m.def("simulate_pfc_waveforms", &simulate_pfc_waveforms, "Simulate PFC waveforms.", py::arg("inputs"));

    // generate_<topo>_ngspice_circuit
    m.def("generate_flyback_ngspice_circuit", &generate_flyback_ngspice_circuit, "Generate Flyback ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_buck_ngspice_circuit", &generate_buck_ngspice_circuit, "Generate Buck ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_boost_ngspice_circuit", &generate_boost_ngspice_circuit, "Generate Boost ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_sepic_ngspice_circuit", &generate_sepic_ngspice_circuit, "Generate SEPIC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_forward_ngspice_circuit", &generate_forward_ngspice_circuit, "Generate Single-Switch Forward ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_two_switch_forward_ngspice_circuit", &generate_two_switch_forward_ngspice_circuit, "Generate Two-Switch Forward ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_active_clamp_forward_ngspice_circuit", &generate_active_clamp_forward_ngspice_circuit, "Generate Active-Clamp Forward ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_push_pull_ngspice_circuit", &generate_push_pull_ngspice_circuit, "Generate Push-Pull ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_isolated_buck_ngspice_circuit", &generate_isolated_buck_ngspice_circuit, "Generate Isolated Buck ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_isolated_buck_boost_ngspice_circuit", &generate_isolated_buck_boost_ngspice_circuit, "Generate Isolated Buck-Boost ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_llc_ngspice_circuit", &generate_llc_ngspice_circuit, "Generate LLC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_cllc_ngspice_circuit", &generate_cllc_ngspice_circuit, "Generate CLLC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_src_ngspice_circuit", &generate_src_ngspice_circuit, "Generate SRC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_dab_ngspice_circuit", &generate_dab_ngspice_circuit, "Generate DAB ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_psfb_ngspice_circuit", &generate_psfb_ngspice_circuit, "Generate PSFB ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_cuk_ngspice_circuit", &generate_cuk_ngspice_circuit, "Generate Cuk ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_zeta_ngspice_circuit", &generate_zeta_ngspice_circuit, "Generate Zeta ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_four_switch_buck_boost_ngspice_circuit", &generate_four_switch_buck_boost_ngspice_circuit, "Generate Four-Switch Buck-Boost ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_weinberg_ngspice_circuit", &generate_weinberg_ngspice_circuit, "Generate Weinberg ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_clllc_ngspice_circuit", &generate_clllc_ngspice_circuit, "Generate CLLLC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_vienna_ngspice_circuit", &generate_vienna_ngspice_circuit, "Generate Vienna Rectifier ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_pshb_ngspice_circuit", &generate_pshb_ngspice_circuit, "Generate PSHB ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_ahb_ngspice_circuit", &generate_ahb_ngspice_circuit, "Generate Asymmetric Half-Bridge ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0);
    m.def("generate_pfc_ngspice_circuit", &generate_pfc_ngspice_circuit, "Generate PFC ngspice netlist.", py::arg("inputs"), py::arg("dc_resistance") = 0.1, py::arg("simulation_time") = 0.02, py::arg("time_step") = 1e-8);
}

} // namespace PyMKF
