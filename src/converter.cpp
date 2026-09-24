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
//     Inputs when present, else throw — these are WASM-parity endpoints no PyOM consumer calls today;
//     the design surface above is what el-choker et al. use.
//
// Kirchhoff failures (its "Exception: ..." strings — no throw crosses the .so boundary) are re-thrown
// here so they surface as PyOpenMagnetics.EngineError in Python (ABT #595/#596).
//
// Only KirchhoffApi.hpp is included here, so no Kirchhoff MAS:: type ever enters an MKF translation unit
// (the string boundary is the whole point — see cmc.cpp, which does the same for the CMC designer).
// PEAS/src/DimensionJson.hpp is header-only json tooling, not a Kirchhoff type, so it keeps that rule.

#include "converter.h"

#include "pybind11_json/pybind11_json.hpp"
#include "json.hpp"
#include <KirchhoffApi.hpp>
#include <PEAS/src/DimensionJson.hpp>

#include <algorithm>
#include <functional>
#include <limits>
#include <map>
#include <optional>
#include <cctype>
#include <cmath>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace py = pybind11;
using json = nlohmann::json;

namespace PyMKF {

namespace {

constexpr const char* kExceptionPrefix = "Exception: ";
// The deck fidelity for spec-level decks/simulations: the ideal, requirements-origin parts (Kirchhoff's
// default). Kirchhoff requires the object — an empty "{}" was rejected ("Fidelity: object with required
// 'origin' expected"), which broke generate_ngspice_circuit(topology, spec, ...).
constexpr const char* kRequirementsFidelity = R"({"origin": "REQUIREMENTS"})";

// Kirchhoff returns "Exception: ..." on failure (no throw crosses the boundary). Re-throw it so the
// caller gets a real Python exception; otherwise parse the JSON payload.
[[noreturn]] void kh_throw(const std::string& out, const char* fn) {
    throw std::runtime_error(std::string(fn) + ": " +
                             out.substr(std::char_traits<char>::length(kExceptionPrefix)));
}

json kh_json(const std::string& out, const char* fn) {
    if (out.rfind(kExceptionPrefix, 0) == 0) {
        kh_throw(out, fn);
    }
    return json::parse(out);
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────────
// MAS topology-schema spec -> Kirchhoff TAS inputs (ABT #596, rewritten 2026-09-24)
//
// PyOM's converter specs are the MAS topology schemas (MAS/schemas/inputs/topologies/<schema>.json, which $ref
// PEAS for the shared types). EVERY field a topology schema defines is accepted and routed to what Kirchhoff
// reads for that topology — a designRequirements entry, a config knob Kirchhoff's design_<topology> honours
// as the model parameter it names, or a constraint Kirchhoff checks and refuses with a specific message. The
// only fields refused outright are ones not in the topology's schema (plus the documented PyOM "advanced"
// extensions below). Nothing is dropped: each handler records where its field went in the field map, and
// adapt_converter_spec() exposes that map so a test can walk every schema property.
//
// Operating points: Kirchhoff designs from operating point 0. Every further operating point is honoured by a
// second Kirchhoff run on the SAME magnetic — the first design's magnetizing inductance and turns ratios (and
// the resonant tank / series / output inductances it sized) are pinned — and its operating point is appended
// to the returned MAS Inputs.
// ─────────────────────────────────────────────────────────────────────────────────────────────────────────

// PyOM "advanced" extensions (NOT in the MAS topology schemas): pin the magnetic / tank of an already-chosen
// part (della-Pollock design-around-the-magnetic flow). Kept because existing callers rely on them; `config`
// passes Kirchhoff knobs verbatim.
const std::vector<std::string>& advanced_extensions() {
    static const std::vector<std::string> k = {"desiredInductance", "desiredTurnsRatios", "desiredResonantInductance",
                                               "desiredResonantCapacitance", "desiredSeriesInductance", "config"};
    return k;
}

struct Adapted {
    json designRequirements = json::object();
    json config = json::object();
    std::vector<json> operatingPoints;          // TAS operating points (inputVoltage, ambientTemperature, outputs)
    std::vector<json> perOperatingPointConfig;  // op-level knobs (phase shift, duty, power-flow direction, mode)
    std::vector<double> perOperatingPointFrequency;
    json fieldMap = json::object();             // schema field -> destination
};

[[noreturn]] void spec_error(const std::string& topology, const std::string& msg) {
    throw std::invalid_argument("converter spec (" + topology + "): " + msg);
}

// Put `value` under `dst[key]`; an explicit entry that already says something different is a contradiction.
void put(json& dst, const std::string& key, const json& value, const std::string& topology, const std::string& field) {
    if (dst.contains(key) && dst.at(key) != value)
        spec_error(topology, "'" + field + "' = " + value.dump() + " contradicts " + key + " = " + dst.at(key).dump());
    dst[key] = value;
}

std::string normalized(const std::string& raw) {
    std::string m;
    for (char c : raw)
        if (!std::isspace(static_cast<unsigned char>(c)) && c != '_' && c != '-')
            m += static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return m;
}

// Flyback modes (MAS flybackModes + legacy spellings) -> Kirchhoff ccm/dcm/bcm/qrm.
std::string flyback_mode(const std::string& raw) {
    const std::string m = normalized(raw);
    if (m == "ccm" || m == "continuousconductionmode" || m == "continuous") return "ccm";
    if (m == "dcm" || m == "discontinuousconductionmode" || m == "discontinuous") return "dcm";
    if (m == "bcm" || m == "boundarymodeoperation" || m == "boundaryconductionmode" || m == "boundarymode" ||
        m == "criticalconductionmode" || m == "crm" || m == "transitionmode") return "bcm";
    if (m == "qrm" || m == "quasiresonantmode" || m == "quasiresonant") return "qrm";
    throw std::invalid_argument("converter spec (flyback): unknown conduction mode '" + raw + "'");
}

// A dimensionWithTolerance scaled by `k` (every bound present).
json scaled_dimension(const json& d, double k) {
    if (d.is_number()) return d.get<double>() * k;
    json out = json::object();
    for (const char* b : {"minimum", "nominal", "maximum"})
        if (d.contains(b)) out[b] = d.at(b).get<double>() * k;
    return out;
}

// The MAS topology schema each Kirchhoff topology is specified by.
std::string schema_of(const std::string& topology) {
    static const std::unordered_map<std::string, std::string> k = {
        {"flyback", "flyback"}, {"buck", "buck"}, {"boost", "boost"}, {"forward", "forward"},
        {"two_switch_forward", "forward"}, {"acf", "forward"}, {"push_pull", "pushPull"},
        {"isolated_buck", "isolatedBuck"}, {"isolated_buck_boost", "isolatedBuckBoost"}, {"sepic", "sepic"},
        {"cuk", "cuk"}, {"zeta", "zeta"}, {"weinberg", "weinberg"}, {"fsbb", "fourSwitchBuckBoost"},
        {"ahb", "asymmetricHalfBridge"}, {"llc", "llcResonant"}, {"cllc", "cllcResonant"},
        {"clllc", "clllcResonant"}, {"src", "seriesResonant"}, {"dab", "dualActiveBridge"},
        {"psfb", "phaseShiftedFullBridge"}, {"pshb", "phaseShiftedHalfBridge"}, {"pfc", "powerFactorCorrection"},
        {"vienna", "vienna"}, {"cmc", "commonModeChoke"}, {"dmc", "differentialModeChoke"},
        {"current_transformer", "currentTransformer"}};
    auto it = k.find(topology);
    if (it == k.end())
        throw std::invalid_argument("converter spec: unknown topology '" + topology + "' (no MAS topology schema)");
    return it->second;
}

using TopHandler = std::function<void(const json& v, Adapted& a)>;
using OpHandler = std::function<void(const json& v, size_t op, Adapted& a)>;
struct SchemaRules {
    std::map<std::string, TopHandler> top;
    std::map<std::string, OpHandler> op;
};

// Handler factories.
TopHandler to_config(const std::string& topo, const std::string& field, const std::string& key) {
    return [topo, field, key](const json& v, Adapted& a) {
        put(a.config, key, v, topo, field);
        a.fieldMap[field] = "config." + key;
    };
}
TopHandler to_dr(const std::string& field, const std::string& key) {
    return [field, key](const json& v, Adapted& a) {
        a.designRequirements[key] = v;
        a.fieldMap[field] = "designRequirements." + key;
    };
}
OpHandler op_to_config(const std::string& topo, const std::string& field, const std::string& key,
                       std::function<json(const json&)> transform = nullptr) {
    return [topo, field, key, transform](const json& v, size_t op, Adapted& a) {
        put(a.perOperatingPointConfig.at(op), key, transform ? transform(v) : v, topo, field);
        a.fieldMap["operatingPoints[]." + field] = "config." + key + " (per operating point)";
    };
}

SchemaRules rules_for(const std::string& topo) {
    const std::string schema = schema_of(topo);
    SchemaRules r;
    auto cfg = [&](const std::string& field, const std::string& key) { r.top[field] = to_config(topo, field, key); };
    auto cfgSame = [&](const std::string& field) { cfg(field, field); };

    // Fields shared by the DC-DC topology schemas.
    r.top["inputVoltage"] = [](const json& v, Adapted& a) {
        a.designRequirements["inputVoltage"] = v;
        a.fieldMap["inputVoltage"] = "designRequirements.inputVoltage (+ operatingPoints[].inputVoltage = nominal)";
    };
    r.top["efficiency"] = to_dr("efficiency", "efficiency");
    r.top["diodeVoltageDrop"] = [topo](const json& v, Adapted& a) {
        put(a.config, "diodeVoltageDrop", v, topo, "diodeVoltageDrop");
        a.fieldMap["diodeVoltageDrop"] = "config.diodeVoltageDrop (Kirchhoff fixed-drop rectifier model)";
    };
    r.top["maximumSwitchCurrent"] = to_config(topo, "maximumSwitchCurrent", "maximumSwitchCurrent");
    r.top["operatingPoints"] = [](const json&, Adapted& a) { a.fieldMap["operatingPoints"] = "operatingPoints[]"; };
    r.op["outputVoltages"] = [](const json&, size_t, Adapted& a) { a.fieldMap["operatingPoints[].outputVoltages"] = "designRequirements.outputs[].voltage / operatingPoints[].outputs[]"; };
    r.op["outputCurrents"] = [](const json&, size_t, Adapted& a) { a.fieldMap["operatingPoints[].outputCurrents"] = "operatingPoints[].outputs[].power = V·I"; };
    for (const char* t : {"outputVoltagesType", "outputCurrentsType"}) {
        const std::string field = t;
        r.op[field] = [topo, field](const json& v, size_t, Adapted& a) {
            const std::string s = v.get<std::string>();
            if (s != "dc" && s != "average")
                spec_error(topo, field + " '" + s + "': Kirchhoff's converter models take DC (= average) output "
                           "quantities; a '" + s + "' value cannot be converted without the output waveform");
            a.fieldMap["operatingPoints[]." + field] = "constraint: dc/average accepted";
        };
    }
    r.op["switchingFrequency"] = [](const json& v, size_t op, Adapted& a) {
        a.perOperatingPointFrequency.at(op) = v.get<double>();
        a.fieldMap["operatingPoints[].switchingFrequency"] = "designRequirements.switchingFrequency (per operating point)";
    };
    r.op["ambientTemperature"] = [](const json& v, size_t op, Adapted& a) {
        a.operatingPoints.at(op)["ambientTemperature"] = v;
        a.fieldMap["operatingPoints[].ambientTemperature"] = "operatingPoints[].ambientTemperature";
    };

    const std::string ripple = (topo == "buck" || topo == "boost" || topo == "llc" || topo == "src") ? "rippleRatio"
                             : (topo == "sepic" || topo == "zeta" || topo == "cuk" || topo == "weinberg") ? "l1RippleRatio"
                             : "inductorRippleRatio";
    r.top["currentRippleRatio"] = to_config(topo, "currentRippleRatio", ripple);

    if (schema == "flyback") {
        cfgSame("maximumDrainSourceVoltage");
        cfg("maximumDutyCycle", "maxDutyCycle");
        r.op["mode"] = op_to_config(topo, "mode", "mode", [](const json& v) { return json(flyback_mode(v.get<std::string>())); });
    } else if (schema == "forward") {
        cfg("dutyCycle", topo == "acf" ? "operatingDutyCycle" : "maxDutyCycle");
    } else if (schema == "pushPull") {
        cfg("dutyCycle", "maxDutyCycle");
        cfgSame("maximumDrainSourceVoltage");
    } else if (schema == "sepic" || schema == "zeta") {
        r.top["synchronousRectifier"] = [topo](const json& v, Adapted& a) {
            put(a.config, "rectifier", v.get<bool>() ? "synchronous" : "diode", topo, "synchronousRectifier");
            a.fieldMap["synchronousRectifier"] = "config.rectifier";
        };
        cfgSame("coupledInductor");
        cfgSame("couplingCoefficient");
    } else if (schema == "cuk") {
        r.top["synchronous"] = [topo](const json& v, Adapted& a) {
            put(a.config, "rectifier", v.get<bool>() ? "synchronous" : "diode", topo, "synchronous");
            a.fieldMap["synchronous"] = "config.rectifier";
        };
        for (const char* f : {"bidirectional", "isolated", "coupledInductor", "turnsRatio", "couplingCoefficient",
                              "couplingCapacitanceSecondary"}) cfgSame(f);
        r.op["powerFlow"] = op_to_config(topo, "powerFlow", "powerFlowDirection");
    } else if (schema == "fourSwitchBuckBoost") {
        for (const char* f : {"outputVoltageRippleRatio", "controlMode", "transitionMode", "bidirectional", "phaseCount"})
            cfgSame(f);
        cfg("transitionHysteresisRatio", "fsbbTransitionBand");
    } else if (schema == "weinberg") {
        for (const char* f : {"variant", "synchronousRectifier", "couplingCoefficientInput", "couplingCoefficientMain"})
            cfgSame(f);
    } else if (schema == "asymmetricHalfBridge") {
        for (const char* f : {"rectifierType", "useLeakageInductance", "leakageInductance", "outputInductance",
                              "dcBlockingCapacitance", "maximumDutyCycle", "inputVoltageStepRange"}) cfgSame(f);
        r.top["magnetizingInductance"] = [](const json& v, Adapted& a) {
            a.designRequirements["magnetizingInductance"] = json{{"nominal", v}};
            a.fieldMap["magnetizingInductance"] = "designRequirements.magnetizingInductance";
        };
        r.op["dutyCycle"] = op_to_config(topo, "dutyCycle", "operatingDutyCycle");
    } else if (schema == "llcResonant") {
        // Band / resonant frequency: fr = sqrt(resonantBandMin·resonantBandMax) in Kirchhoff's LLC.
        r.top["minSwitchingFrequency"] = to_config(topo, "minSwitchingFrequency", "resonantBandMin");
        r.top["maxSwitchingFrequency"] = to_config(topo, "maxSwitchingFrequency", "resonantBandMax");
        r.top["resonantFrequency"] = [topo](const json& v, Adapted& a) {
            a.fieldMap["resonantFrequency"] = "config.resonantBandMin/Max (fr = sqrt(min·max))";
            a.config["__llcResonantFrequency"] = v;   // resolved against the band after every field is read
        };
        cfgSame("inductanceRatio"); cfgSame("qualityFactor"); cfgSame("bridgeType"); cfgSame("rectifierType");
        cfgSame("integratedResonantInductor");
        r.top["seriesInductance"] = to_dr("seriesInductance", "desiredResonantInductance");
        r.top["resonantCapacitance"] = to_dr("resonantCapacitance", "desiredResonantCapacitance");
        // The operating point's switchingFrequency is the frequency the LLC runs at (inside the band), not fr.
        r.op["switchingFrequency"] = [topo](const json& v, size_t op, Adapted& a) {
            a.perOperatingPointFrequency.at(op) = v.get<double>();
            put(a.perOperatingPointConfig.at(op), "driveAtSwitchingFrequency", true, topo, "switchingFrequency");
            a.fieldMap["operatingPoints[].switchingFrequency"] =
                "designRequirements.switchingFrequency + config.driveAtSwitchingFrequency (operated there)";
        };
    } else if (schema == "cllcResonant") {
        for (const char* f : {"minSwitchingFrequency", "maxSwitchingFrequency", "qualityFactor", "symmetricDesign",
                              "bidirectional", "bridgeType", "integratedResonantInductor1", "integratedResonantInductor2",
                              "resonantInductorRatio", "resonantCapacitorRatio"}) cfgSame(f);
        r.op["powerFlow"] = op_to_config(topo, "powerFlow", "powerFlowDirection");
    } else if (schema == "clllcResonant") {
        r.top["highVoltageBusVoltage"] = [](const json& v, Adapted& a) {
            a.designRequirements["inputVoltage"] = v;
            a.fieldMap["highVoltageBusVoltage"] = "designRequirements.inputVoltage (+ operatingPoints[].inputVoltage)";
        };
        r.top["lowVoltageBusVoltage"] = [](const json& v, Adapted& a) {
            a.config["__lowVoltageBus"] = v;   // becomes outputs[0].voltage; checked against outputVoltages[0]
            a.fieldMap["lowVoltageBusVoltage"] = "designRequirements.outputs[0].voltage";
        };
        for (const char* f : {"minSwitchingFrequency", "maxSwitchingFrequency", "primaryResonantFrequency",
                              "qualityFactor", "tankSymmetryRatio", "bridgeTypePrimary", "bridgeTypeSecondary",
                              "controlStrategy", "integratedResonantInductors", "primarySeriesInductance",
                              "primaryResonantCapacitance"}) cfgSame(f);
        cfg("inductanceRatioK", "inductanceRatio");
        r.op["powerFlowDirection"] = op_to_config(topo, "powerFlowDirection", "powerFlowDirection");
        r.op["phaseShiftDegrees"] = op_to_config(topo, "phaseShiftDegrees", "phaseShiftDegrees");
    } else if (schema == "seriesResonant") {
        for (const char* f : {"minSwitchingFrequency", "maxSwitchingFrequency", "resonantFrequency", "qualityFactor",
                              "bridgeType", "isolated", "useSynchronousRectifier"}) cfgSame(f);
        r.top["rectifierType"] = [topo](const json& v, Adapted& a) {
            static const std::unordered_map<std::string, std::string> k = {
                {"fullBridgeDiode", "fullBridge"}, {"centerTappedDiode", "centerTapped"}, {"currentDoubler", "currentDoubler"}};
            const auto it = k.find(v.get<std::string>());
            if (it == k.end()) spec_error(topo, "unknown rectifierType '" + v.get<std::string>() + "'");
            put(a.config, "rectifierType", it->second, topo, "rectifierType");
            a.fieldMap["rectifierType"] = "config.rectifierType";
        };
        r.top["seriesInductance"] = to_dr("seriesInductance", "desiredResonantInductance");
        r.top["resonantCapacitance"] = to_dr("resonantCapacitance", "desiredResonantCapacitance");
    } else if (schema == "dualActiveBridge" || schema == "phaseShiftedFullBridge" || schema == "phaseShiftedHalfBridge") {
        // seriesInductance 0 = "use the transformer leakage": the series inductance is then realised as T1's
        // leakage (useLeakageInductance), sized by the design; > 0 pins it.
        r.top["seriesInductance"] = [topo](const json& v, Adapted& a) {
            const double l = v.get<double>();
            if (l < 0) spec_error(topo, "seriesInductance must be >= 0");
            if (l > 0) put(a.config, "seriesInductance", l, topo, "seriesInductance");
            else put(a.config, "useLeakageInductance", true, topo, "seriesInductance = 0 (use the leakage)");
            a.fieldMap["seriesInductance"] = l > 0 ? "config.seriesInductance" : "config.useLeakageInductance = true";
        };
        cfgSame("useLeakageInductance");
        if (schema == "dualActiveBridge") {
            cfgSame("perSecondaryLeakage");
            r.op["modulationType"] = op_to_config(topo, "modulationType", "dabModulationType");
            r.op["innerPhaseShift1"] = op_to_config(topo, "innerPhaseShift1", "dabInnerPhaseShift1Deg");
            r.op["innerPhaseShift2"] = op_to_config(topo, "innerPhaseShift2", "dabInnerPhaseShift2Deg");
            r.op["innerPhaseShift3"] = op_to_config(topo, "innerPhaseShift3", "dabPhaseShiftDeg");
        } else {
            cfgSame("outputInductance"); cfgSame("rectifierType"); cfgSame("maximumPhaseShift");
            r.op["phaseShift"] = op_to_config(topo, "phaseShift", "commandedDuty",
                                              [](const json& v) { return json(v.get<double>() / 180.0); });
        }
    } else if (schema == "powerFactorCorrection") {
        r.top.erase("operatingPoints");
        r.top["outputVoltage"] = [](const json& v, Adapted& a) {
            a.config["__pfcOutputVoltage"] = v;
            a.fieldMap["outputVoltage"] = "designRequirements.outputs[0].voltage";
        };
        r.top["outputPower"] = [](const json& v, Adapted& a) {
            a.config["__pfcOutputPower"] = v;
            a.fieldMap["outputPower"] = "operatingPoints[0].outputs[0].power";
        };
        r.top["lineFrequency"] = [](const json& v, Adapted& a) {
            a.designRequirements["lineFrequency"] = json{{"nominal", v}};
            a.fieldMap["lineFrequency"] = "designRequirements.lineFrequency";
        };
        r.top["switchingFrequency"] = [](const json& v, Adapted& a) {
            a.config["__pfcSwitchingFrequency"] = v;
            a.fieldMap["switchingFrequency"] = "designRequirements.switchingFrequency";
        };
        r.top["ambientTemperature"] = [](const json& v, Adapted& a) {
            a.config["__pfcAmbient"] = v;
            a.fieldMap["ambientTemperature"] = "operatingPoints[0].ambientTemperature";
        };
        cfg("currentRippleRatio", "currentRippleFraction");
        r.top["mode"] = [topo](const json& v, Adapted& a) {
            static const std::unordered_map<std::string, std::string> k = {
                {"continuousConductionMode", "ccm"}, {"discontinuousConductionMode", "dcm"},
                {"criticalConductionMode", "crm"}, {"transitionMode", "transition"}};
            const auto it = k.find(v.get<std::string>());
            put(a.config, "mode", it != k.end() ? json(it->second) : v, topo, "mode");
            a.fieldMap["mode"] = "config.mode";
        };
        cfgSame("topologyVariant"); cfgSame("numberOfPhases"); cfgSame("wideBandgapSwitch");
        cfg("bulkCapacitance", "outputCapacitance");
        r.top["maximumCoreTemperatureRise"] = [topo](const json&, Adapted&) {
            spec_error(topo, "maximumCoreTemperatureRise cannot be honoured: the MAS Inputs this call returns have no "
                       "temperature-rise requirement (MAS designRequirements has no such field) and no magnetic is "
                       "designed here to check it against — a MAS schema gap, not a Kirchhoff choice");
        };
    } else if (schema == "vienna") {
        r.top["lineToLineVoltage"] = [](const json& v, Adapted& a) {
            // Kirchhoff's Vienna takes the PHASE (line-to-neutral) rms: V_LN = V_LL/√3.
            a.designRequirements["inputVoltage"] = scaled_dimension(v, 1.0 / std::sqrt(3.0));
            a.fieldMap["lineToLineVoltage"] = "designRequirements.inputVoltage = V_LL/sqrt(3) (phase rms)";
        };
        r.top["lineFrequency"] = [](const json& v, Adapted& a) {
            a.designRequirements["lineFrequency"] = json{{"nominal", v}};
            a.fieldMap["lineFrequency"] = "designRequirements.lineFrequency";
        };
        r.top["outputDcVoltage"] = [](const json& v, Adapted& a) {
            a.config["__viennaOutputDcVoltage"] = v;
            a.fieldMap["outputDcVoltage"] = "designRequirements.outputs[0].voltage (checked against outputVoltages)";
        };
        r.top["switchingFrequency"] = [](const json& v, Adapted& a) {
            a.config["__viennaSwitchingFrequency"] = v;
            a.fieldMap["switchingFrequency"] = "designRequirements.switchingFrequency (checked against the operating points)";
        };
        for (const char* f : {"powerFactor", "viennaVariant", "switchType", "synchronousRectifier", "samplingStrategy"})
            cfgSame(f);
        cfg("phaseCount", "numberOfChannels");
    }
    return r;
}

bool is_chokes_or_ct(const std::string& topo) { return topo == "cmc" || topo == "dmc" || topo == "current_transformer"; }

// Adapt a MAS topology-schema spec. Returns one Kirchhoff TAS-inputs spec per operating point (index 0 is the
// design point) plus the field map.
struct AdaptResult {
    std::vector<json> specs;
    json fieldMap;
};

AdaptResult adapt_spec(const json& spec, const std::string& topo) {
    AdaptResult out;
    if (!spec.is_object()) spec_error(topo, "the spec must be a JSON object");
    if (spec.contains("designRequirements")) {   // already Kirchhoff/TAS-shaped: pass through
        out.specs.push_back(spec);
        return out;
    }
    const std::string schema = schema_of(topo);
    if (is_chokes_or_ct(topo)) {
        // The CMC / DMC / current-transformer designers read their MAS schema fields natively.
        out.specs.push_back(spec);
        for (const auto& [k, v] : spec.items()) { (void)v; out.fieldMap[k] = "Kirchhoff design_" + topo + " (native)"; }
        return out;
    }
    SchemaRules rules = rules_for(topo);
    const auto& ext = advanced_extensions();
    for (const auto& [k, v] : spec.items()) {
        (void)v;
        if (!rules.top.count(k) && std::find(ext.begin(), ext.end(), k) == ext.end())
            spec_error(topo, "field '" + k + "' is not in the MAS " + schema + " schema");
    }
    Adapted a;
    const bool pfc = (schema == "powerFactorCorrection");
    const json ops = pfc ? json::array({json::object()}) : spec.at("operatingPoints");
    if (!ops.is_array() || ops.empty()) spec_error(topo, "operatingPoints must be a non-empty array");
    a.operatingPoints.assign(ops.size(), json::object());
    a.perOperatingPointConfig.assign(ops.size(), json::object());
    a.perOperatingPointFrequency.assign(ops.size(), std::numeric_limits<double>::quiet_NaN());
    if (spec.contains("config")) a.config = spec.at("config");

    for (const auto& [k, v] : spec.items())
        if (rules.top.count(k)) rules.top.at(k)(v, a);
    for (size_t i = 0; i < ops.size(); ++i) {
        for (const auto& [k, v] : ops.at(i).items()) {
            if (!rules.op.count(k))
                spec_error(topo, "operatingPoints[" + std::to_string(i) + "]." + k + " is not in the MAS " + schema +
                           " schema");
            rules.op.at(k)(v, i, a);
        }
    }

    // Advanced extensions.
    if (spec.contains("desiredInductance"))
        a.designRequirements["magnetizingInductance"] = json{{"nominal", spec.at("desiredInductance")}};
    if (spec.contains("desiredTurnsRatios")) a.designRequirements["turnsRatios"] = spec.at("desiredTurnsRatios");
    for (const char* k : {"desiredResonantInductance", "desiredResonantCapacitance", "desiredSeriesInductance"})
        if (spec.contains(k)) a.designRequirements[k] = spec.at(k);

    // Cross-field resolution.
    if (a.config.contains("__llcResonantFrequency")) {
        const double fr = a.config.at("__llcResonantFrequency").get<double>();
        a.config.erase("__llcResonantFrequency");
        const bool hasMin = a.config.contains("resonantBandMin"), hasMax = a.config.contains("resonantBandMax");
        if (hasMin && hasMax) {
            const double centre = std::sqrt(a.config.at("resonantBandMin").get<double>() * a.config.at("resonantBandMax").get<double>());
            if (std::abs(fr - centre) > 1e-6 * centre)
                spec_error(topo, "resonantFrequency " + std::to_string(fr) + " Hz contradicts the band centre sqrt(min·max) = " +
                           std::to_string(centre) + " Hz Kirchhoff designs the LLC tank at");
        } else if (hasMin || hasMax) {
            spec_error(topo, "resonantFrequency with only one of min/maxSwitchingFrequency is ambiguous");
        } else {
            a.config["resonantBandMin"] = fr;
            a.config["resonantBandMax"] = fr;
        }
    }
    if (schema == "llcResonant" && (a.config.contains("resonantBandMin") != a.config.contains("resonantBandMax")))
        spec_error(topo, "needs BOTH minSwitchingFrequency and maxSwitchingFrequency (the resonant band) or neither");

    // Outputs and operating points.
    json drOutputs = json::array();
    if (pfc) {
        for (const char* k : {"__pfcOutputVoltage", "__pfcOutputPower", "__pfcSwitchingFrequency"})
            if (!a.config.contains(k)) spec_error(topo, std::string("missing ") + (k + 5));
        drOutputs.push_back(json{{"name", "output 0"}, {"voltage", {{"nominal", a.config.at("__pfcOutputVoltage")}}}});
        a.operatingPoints[0]["outputs"] = json::array({json{{"power", a.config.at("__pfcOutputPower")}}});
        a.perOperatingPointFrequency[0] = a.config.at("__pfcSwitchingFrequency").get<double>();
        if (a.config.contains("__pfcAmbient")) a.operatingPoints[0]["ambientTemperature"] = a.config.at("__pfcAmbient");
        for (const char* k : {"__pfcOutputVoltage", "__pfcOutputPower", "__pfcSwitchingFrequency", "__pfcAmbient"})
            a.config.erase(k);
    } else {
        for (size_t i = 0; i < ops.size(); ++i) {
            const json& op = ops.at(i);
            if (!op.contains("outputVoltages") || !op.contains("outputCurrents"))
                spec_error(topo, "operatingPoints[" + std::to_string(i) + "] needs outputVoltages and outputCurrents");
            const json& vs = op.at("outputVoltages");
            const json& is = op.at("outputCurrents");
            if (!vs.is_array() || !is.is_array() || vs.empty() || vs.size() != is.size())
                spec_error(topo, "operatingPoints[" + std::to_string(i) + "] needs matching non-empty outputVoltages/outputCurrents");
            json outs = json::array();
            for (size_t k = 0; k < vs.size(); ++k) outs.push_back(json{{"power", vs.at(k).get<double>() * is.at(k).get<double>()}});
            a.operatingPoints[i]["outputs"] = outs;
            if (i == 0)
                for (size_t k = 0; k < vs.size(); ++k)
                    drOutputs.push_back(json{{"name", "output " + std::to_string(k)}, {"voltage", {{"nominal", vs.at(k)}}}});
        }
    }
    if (a.config.contains("__lowVoltageBus")) {
        const json lv = a.config.at("__lowVoltageBus");
        a.config.erase("__lowVoltageBus");
        const double lvNominal = PEAS::resolve_dimensional_values(lv);
        if (std::abs(lvNominal - drOutputs.at(0).at("voltage").at("nominal").get<double>()) > 1e-6 * lvNominal)
            spec_error(topo, "lowVoltageBusVoltage (nominal " + std::to_string(lvNominal) +
                       " V) disagrees with operatingPoints[0].outputVoltages[0]");
        drOutputs.at(0)["voltage"] = lv;
    }
    if (a.config.contains("__viennaOutputDcVoltage")) {
        const double vdc = a.config.at("__viennaOutputDcVoltage").get<double>();
        a.config.erase("__viennaOutputDcVoltage");
        if (std::abs(vdc - drOutputs.at(0).at("voltage").at("nominal").get<double>()) > 1e-6 * vdc)
            spec_error(topo, "outputDcVoltage disagrees with operatingPoints[0].outputVoltages[0]");
    }
    if (a.config.contains("__viennaSwitchingFrequency")) {
        const double fs = a.config.at("__viennaSwitchingFrequency").get<double>();
        a.config.erase("__viennaSwitchingFrequency");
        for (auto& f : a.perOperatingPointFrequency) {
            if (!std::isnan(f) && std::abs(f - fs) > 1e-9 * fs)
                spec_error(topo, "switchingFrequency disagrees with an operating point's switchingFrequency");
            f = fs;
        }
    }
    a.designRequirements["outputs"] = drOutputs;
    if (!a.designRequirements.contains("inputVoltage"))
        spec_error(topo, "needs the input voltage (inputVoltage / highVoltageBusVoltage / lineToLineVoltage)");
    const double vinNominal = PEAS::resolve_dimensional_values(a.designRequirements.at("inputVoltage"));

    for (size_t i = 0; i < ops.size(); ++i) {
        if (std::isnan(a.perOperatingPointFrequency[i]))
            spec_error(topo, "operatingPoints[" + std::to_string(i) + "] has no switchingFrequency" +
                       (schema == "flyback" ? std::string(" — the schema lets a flyback infer it from the conduction "
                        "mode, but MAS docs/inputs.md defines no inference rule and Kirchhoff needs the frequency")
                                            : std::string()));
        json s;
        s["designRequirements"] = a.designRequirements;
        s["designRequirements"]["switchingFrequency"] = json{{"nominal", a.perOperatingPointFrequency[i]}};
        json op = a.operatingPoints[i];
        op["name"] = "operating point " + std::to_string(i);
        op["inputVoltage"] = vinNominal;
        s["operatingPoints"] = json::array({op});
        json config = a.config;
        for (const auto& [k, v] : a.perOperatingPointConfig[i].items()) put(config, k, v, topo, k);
        if (!config.empty()) s["config"] = config;
        out.specs.push_back(std::move(s));
    }
    out.fieldMap = a.fieldMap;
    for (const char* k : {"desiredInductance", "desiredTurnsRatios", "desiredResonantInductance",
                          "desiredResonantCapacitance", "desiredSeriesInductance", "config"})
        if (spec.contains(k)) out.fieldMap[k] = "PyOM advanced extension (not in the MAS schema)";
    return out;
}

// Pin the design of operating point 0 into a later operating point's spec, so every operating point describes
// the SAME magnetic: the main magnetic's magnetizing inductance and turns ratios, and the tank / series / output
// inductances the design sized (read back from the op-0 TAS by component name).
void pin_design(json& spec, const json& tas0, const json& inputs0, const std::string& topo) {
    json& dr = spec["designRequirements"];
    const json& dr0 = inputs0.at("designRequirements");
    const double lm = PEAS::resolve_dimensional_values(dr0.at("magnetizingInductance"));
    dr["magnetizingInductance"] = json{{"nominal", lm}};
    json tr = json::array();
    for (const auto& t : dr0.at("turnsRatios")) tr.push_back(json{{"nominal", PEAS::resolve_dimensional_values(t)}});
    dr["turnsRatios"] = tr;
    // Component values from the TAS.
    auto component_value = [&](const std::string& name) -> std::optional<double> {
        for (const auto& st : tas0.at("topology").at("stages")) {
            if (!st.contains("circuit") || !st.at("circuit").contains("components")) continue;
            for (const auto& c : st.at("circuit").at("components")) {
                if (c.value("name", std::string()) != name || !c.contains("data")) continue;
                const json& d = c.at("data");
                if (d.contains("magnetic") && d.contains("inputs"))
                    return PEAS::resolve_dimensional_values(d.at("inputs").at("designRequirements").at("magnetizingInductance"));
                if (d.contains("capacitor"))
                    return PEAS::resolve_dimensional_values(d.at("inputs").at("designRequirements").at("capacitance"));
            }
        }
        return std::nullopt;
    };
    json& config = spec["config"];
    if (topo == "llc" || topo == "src") {
        if (auto l = component_value("Lr")) dr["desiredResonantInductance"] = *l;
        if (auto c = component_value("Cr")) dr["desiredResonantCapacitance"] = *c;
    } else if (topo == "clllc") {
        if (auto l = component_value("Lr1")) config["primarySeriesInductance"] = *l;
        if (auto c = component_value("Cr1")) config["primaryResonantCapacitance"] = *c;
    } else if (topo == "dab" || topo == "psfb" || topo == "pshb") {
        if (auto l = component_value("Lr")) {
            config["seriesInductance"] = *l;
        } else if (dr0.contains("leakageInductance") && !dr0.at("leakageInductance").empty()) {
            // Lr folded into T1's leakage (useLeakageInductance): the leakage IS the series inductance.
            config["seriesInductance"] = PEAS::resolve_dimensional_values(dr0.at("leakageInductance").at(0));
        } else {
            throw std::runtime_error("pin_design(" + topo + "): operating point 0's design has neither a series "
                                     "inductor Lr nor a leakage requirement to pin");
        }
    }
    if (topo == "psfb" || topo == "pshb" || topo == "ahb")
        if (auto l = component_value("Lout")) config["outputInductance"] = *l;
}

// Map PyOM's legacy long topology names (and the "advanced_" mode prefix, which Kirchhoff derives from
// the spec's desiredInductance instead) onto Kirchhoff's dispatcher names. Kirchhoff registers the SHORT
// names (KirchhoffApi.cpp tas_builders(): forward, acf, fsbb, pfc, psfb, pshb, ahb, ...), so the long
// legacy aliases map down; short names pass through untouched (ABT #596 — the old map pointed the wrong
// way and broke every aliased topology).
std::string kh_topology(const std::string& raw) {
    std::string s = raw;
    if (s.rfind("advanced_", 0) == 0) {
        s = s.substr(std::char_traits<char>::length("advanced_"));
    }
    static const std::unordered_map<std::string, std::string> kMap = {
        {"single_switch_forward", "forward"},
        {"active_clamp_forward", "acf"},
        {"four_switch_buck_boost", "fsbb"},
        {"power_factor_correction", "pfc"},
        {"phase_shifted_full_bridge", "psfb"},
        {"phase_shifted_half_bridge", "pshb"},
        {"asymmetric_half_bridge", "ahb"},
        {"common_mode_choke", "cmc"},
        {"differential_mode_choke", "dmc"},
        {"dual_active_bridge", "dab"},
        {"series_resonant", "src"},
        {"currentTransformer", "current_transformer"},
    };
    auto it = kMap.find(s);
    return it != kMap.end() ? it->second : s;
}

// Design entry: spec -> MAS::Inputs (the legacy process_converter / calculate_<topo>_inputs contract). One
// Kirchhoff design per operating point; the later ones are pinned to operating point 0's magnetic and their
// operating points appended, so the returned Inputs carry every operating point of the spec.
json design_inputs(const std::string& topology, const json& spec, const char* fn) {
    const std::string topo = kh_topology(topology);
    AdaptResult adapted = adapt_spec(spec, topo);
    json inputs0 = kh_json(Kirchhoff::api::design_magnetic_inputs(topo, adapted.specs.at(0).dump()), fn);
    if (adapted.specs.size() == 1) return inputs0;
    const std::string tas0 = Kirchhoff::api::design_tas(topo, adapted.specs.at(0).dump());
    if (tas0.rfind(kExceptionPrefix, 0) == 0) kh_throw(tas0, fn);
    const json tas0json = json::parse(tas0);
    for (size_t i = 1; i < adapted.specs.size(); ++i) {
        json s = adapted.specs.at(i);
        pin_design(s, tas0json, inputs0, topo);
        const json inputsI = kh_json(Kirchhoff::api::design_magnetic_inputs(topo, s.dump()), fn);
        for (auto op : inputsI.at("operatingPoints")) {
            op["name"] = "operating point " + std::to_string(i);
            inputs0["operatingPoints"].push_back(op);
        }
    }
    return inputs0;
}

// The adapted Kirchhoff spec of the design operating point (decks and simulations run that one).
json design_point_spec(const std::string& topology, const json& spec) {
    return adapt_spec(spec, kh_topology(topology)).specs.at(0);
}

// ngspice deck from a converter SPEC: design a TAS then assemble the deck. Returns {"netlist": "<spice>"}.
json ngspice_deck_from_spec(const std::string& topology, const json& spec, const char* fn) {
    const std::string tas = Kirchhoff::api::design_tas(kh_topology(topology),
                                                       design_point_spec(topology, spec).dump());
    if (tas.rfind(kExceptionPrefix, 0) == 0) {
        kh_throw(tas, fn);
    }
    const std::string deck = Kirchhoff::api::generate_ngspice_circuit(tas, kRequirementsFidelity);
    if (deck.rfind(kExceptionPrefix, 0) == 0) {
        kh_throw(deck, fn);
    }
    return json{{"netlist", deck}};
}

// ngspice sim from a converter SPEC: design a TAS then run it. Returns Kirchhoff's per-vector summary.
json ngspice_sim_from_spec(const std::string& topology, const json& spec, const char* fn) {
    const std::string tas = Kirchhoff::api::design_tas(kh_topology(topology),
                                                       design_point_spec(topology, spec).dump());
    if (tas.rfind(kExceptionPrefix, 0) == 0) {
        kh_throw(tas, fn);
    }
    return kh_json(Kirchhoff::api::simulate_ngspice(tas, kRequirementsFidelity), fn);
}

// A built-MAS-Inputs simulate/deck endpoint whose spec is not recoverable: Kirchhoff needs a spec/TAS, not
// a finished Inputs (WASM-parity surface, unused by PyOM consumers).
[[noreturn]] void needs_spec_error(const char* fn) {
    throw std::runtime_error(std::string(fn) +
        ": Kirchhoff builds ngspice decks/sims from a converter SPEC (design_tas), not a finished MAS "
        "Inputs. Call the SPEC-based path (generate_ngspice_circuit(topology, spec, ...) / "
        "process_converter) instead.");
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
    needs_spec_error("get_extra_components_inputs");
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
        kh_throw(out, fn);
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
    needs_spec_error(fn);
}
json deck_from_inputs(const std::string& topology, const json& inputs, const char* fn) {
    if (inputs.contains("converterSpec")) return ngspice_deck_from_spec(topology, inputs.at("converterSpec"), fn);
    if (inputs.contains("spec")) return ngspice_deck_from_spec(topology, inputs.at("spec"), fn);
    needs_spec_error(fn);
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
        py::arg("topology_name"), py::arg("converter_json"), py::arg("use_ngspice") = true,
        py::call_guard<py::gil_scoped_release>());
    m.def("adapt_converter_spec",
        [](const std::string& topologyName, json spec) {
            const std::string topo = kh_topology(topologyName);
            AdaptResult r = adapt_spec(spec, topo);
            return json{{"schema", schema_of(topo)}, {"kirchhoffTopology", topo},
                        {"kirchhoffSpecs", r.specs}, {"fieldMap", r.fieldMap}};
        },
        "Translate a MAS topology-schema converter spec into the Kirchhoff spec(s) it designs from — one per "
        "operating point — and report where every spec field went (fieldMap). Raises EngineError for a field "
        "outside the topology's MAS schema.",
        py::arg("topology_name"), py::arg("spec"));

    m.def("design_magnetics_from_converter", &design_magnetics_from_converter,
        "Design requirements (MAS Inputs) from a converter spec via Kirchhoff; feed the magnetic adviser.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("max_results") = 1, py::arg("core_mode_json") = "available cores",
        py::arg("use_ngspice") = true, py::arg("weights_json") = nullptr, py::arg("fast") = false,
        py::call_guard<py::gil_scoped_release>());

    m.def("process_flyback", &process_flyback, "Process Flyback converter.", py::arg("flyback"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_buck", &process_buck, "Process Buck converter.", py::arg("buck"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_boost", &process_boost, "Process Boost converter.", py::arg("boost"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_single_switch_forward", &process_single_switch_forward, "Process Single-Switch Forward.", py::arg("forward"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_two_switch_forward", &process_two_switch_forward, "Process Two-Switch Forward.", py::arg("forward"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_active_clamp_forward", &process_active_clamp_forward, "Process Active Clamp Forward.", py::arg("forward"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_push_pull", &process_push_pull, "Process Push-Pull converter.", py::arg("push_pull"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_isolated_buck", &process_isolated_buck, "Process Isolated Buck.", py::arg("isolated_buck"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_isolated_buck_boost", &process_isolated_buck_boost, "Process Isolated Buck-Boost.", py::arg("isolated_buck_boost"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_current_transformer", &process_current_transformer, "Process Current Transformer.",
        py::arg("ct"), py::arg("turns_ratio"), py::arg("secondary_resistance") = 0.0,
        py::call_guard<py::gil_scoped_release>());
    m.def("process_cuk", &process_cuk, "Process Cuk converter.", py::arg("cuk"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_sepic", &process_sepic, "Process SEPIC converter.", py::arg("sepic"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_zeta", &process_zeta, "Process Zeta converter.", py::arg("zeta"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_four_switch_buck_boost", &process_four_switch_buck_boost, "Process Four-Switch Buck-Boost converter.", py::arg("converter"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_asymmetric_half_bridge", &process_asymmetric_half_bridge, "Process Asymmetric Half-Bridge converter.", py::arg("converter"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_weinberg", &process_weinberg, "Process Weinberg converter.", py::arg("converter"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_vienna", &process_vienna, "Process Vienna Rectifier converter.", py::arg("converter"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_clllc", &process_clllc, "Process CLLLC Resonant converter.", py::arg("converter"),
        py::call_guard<py::gil_scoped_release>());
    m.def("process_src", &process_src, "Process Series Resonant converter (SRC).", py::arg("converter"),
        py::call_guard<py::gil_scoped_release>());

    m.def("generate_ngspice_circuit", &generate_ngspice_circuit,
        "Return the ngspice SPICE deck for a converter SPEC (Kirchhoff design_tas + generate_ngspice_circuit). "
        "Returns {'netlist': '<spice>'}; raises PyOpenMagnetics.EngineError on failure.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("turns_ratios"), py::arg("magnetizing_inductance"),
        py::arg("vin_index") = 0, py::arg("op_index") = 0,
        py::arg("bridge_simulation_mode") = std::string(""),
        py::arg("spice_config") = nlohmann::json::object(),
        py::call_guard<py::gil_scoped_release>());
    m.def("get_extra_components_inputs", &get_extra_components_inputs,
        "Extra-component design requirements (resonant tank, snubbers). Carried inside Kirchhoff's TAS.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("mode") = "IDEAL", py::arg("magnetic_json") = nullptr,
        py::call_guard<py::gil_scoped_release>());

    #define BIND_CONVERTER_ALIAS(fn) m.def(#fn, &fn, "Topology inputs builder (WASM parity alias).", py::arg("inputs"), py::call_guard<py::gil_scoped_release>())
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
    m.def("calculate_dmc_inputs", &calculate_dmc_inputs, "Build MAS Inputs for a DMC (Kirchhoff design_dmc).", py::arg("dmc_inputs"),
        py::call_guard<py::gil_scoped_release>());
    m.def("verify_dmc_attenuation", &verify_dmc_attenuation, "Verify a DMC + capacitor meets the attenuation spec.",
        py::arg("dmc_inputs"), py::arg("inductance"), py::arg("capacitance") = 0.0,
        py::call_guard<py::gil_scoped_release>());
    m.def("propose_dmc_design", &propose_dmc_design, "Propose a DMC L/C pair satisfying the spec.", py::arg("dmc_inputs"),
        py::call_guard<py::gil_scoped_release>());
    m.def("simulate_dmc_waveforms", &simulate_dmc_waveforms, "Simulate DMC time-domain waveforms.", py::arg("dmc_inputs"), py::arg("inductance"),
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_dmc_ngspice_circuit", &generate_dmc_ngspice_circuit, "DMC ngspice deck/sim.", py::arg("dmc_inputs"),
        py::call_guard<py::gil_scoped_release>());

    // CMC ngspice sims (design lives in cmc.cpp).
    m.def("generate_cmc_ngspice_circuit", &generate_cmc_ngspice_circuit, "CMC ngspice deck/sim.", py::arg("cmc_inputs"),
        py::call_guard<py::gil_scoped_release>());
    m.def("simulate_cmc_lisn_waveforms", &simulate_cmc_lisn_waveforms, "CISPR LISN test sim for a CMC.", py::arg("cmc_inputs"), py::arg("inductance"),
        py::call_guard<py::gil_scoped_release>());
    m.def("simulate_cmc_ideal_waveforms", &simulate_cmc_ideal_waveforms, "CMC operating-point sim (line + switching noise).",
        py::arg("cmc_inputs"), py::arg("inductance"), py::arg("parasitic_capacitance_pF") = 10.0, py::arg("dvdt_V_per_ns") = 50.0,
        py::call_guard<py::gil_scoped_release>());

    // simulate_<topo>_ideal_waveforms
    m.def("simulate_flyback_ideal_waveforms", &simulate_flyback_ideal_waveforms, "Simulate Flyback ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_flyback_with_magnetic", &simulate_flyback_with_magnetic, "Simulate Flyback with a pre-built magnetic.", py::arg("inputs"), py::arg("magnetic"),
        py::call_guard<py::gil_scoped_release>());
    m.def("simulate_buck_ideal_waveforms", &simulate_buck_ideal_waveforms, "Simulate Buck ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_boost_ideal_waveforms", &simulate_boost_ideal_waveforms, "Simulate Boost ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_sepic_ideal_waveforms", &simulate_sepic_ideal_waveforms, "Simulate SEPIC ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_cuk_ideal_waveforms", &simulate_cuk_ideal_waveforms, "Simulate Cuk ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_zeta_ideal_waveforms", &simulate_zeta_ideal_waveforms, "Simulate Zeta ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_four_switch_buck_boost_ideal_waveforms", &simulate_four_switch_buck_boost_ideal_waveforms, "Simulate Four-Switch Buck-Boost ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_forward_ideal_waveforms", &simulate_forward_ideal_waveforms, "Simulate Single-Switch Forward ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_two_switch_forward_ideal_waveforms", &simulate_two_switch_forward_ideal_waveforms, "Simulate Two-Switch Forward ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_active_clamp_forward_ideal_waveforms", &simulate_active_clamp_forward_ideal_waveforms, "Simulate Active-Clamp Forward ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_push_pull_ideal_waveforms", &simulate_push_pull_ideal_waveforms, "Simulate Push-Pull ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_isolated_buck_ideal_waveforms", &simulate_isolated_buck_ideal_waveforms, "Simulate Isolated Buck ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_isolated_buck_boost_ideal_waveforms", &simulate_isolated_buck_boost_ideal_waveforms, "Simulate Isolated Buck-Boost ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_weinberg_ideal_waveforms", &simulate_weinberg_ideal_waveforms, "Simulate Weinberg ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_llc_ideal_waveforms", &simulate_llc_ideal_waveforms, "Simulate LLC ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_cllc_ideal_waveforms", &simulate_cllc_ideal_waveforms, "Simulate CLLC ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_clllc_ideal_waveforms", &simulate_clllc_ideal_waveforms, "Simulate CLLLC ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_src_ideal_waveforms", &simulate_src_ideal_waveforms, "Simulate SRC ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_dab_ideal_waveforms", &simulate_dab_ideal_waveforms, "Simulate DAB ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_psfb_ideal_waveforms", &simulate_psfb_ideal_waveforms, "Simulate PSFB ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_pshb_ideal_waveforms", &simulate_pshb_ideal_waveforms, "Simulate PSHB ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_ahb_ideal_waveforms", &simulate_ahb_ideal_waveforms, "Simulate Asymmetric Half-Bridge ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_vienna_ideal_waveforms", &simulate_vienna_ideal_waveforms, "Simulate Vienna Rectifier ideal waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());
    m.def("simulate_pfc_waveforms", &simulate_pfc_waveforms, "Simulate PFC waveforms.", py::arg("inputs"), py::call_guard<py::gil_scoped_release>());

    // generate_<topo>_ngspice_circuit
    m.def("generate_flyback_ngspice_circuit", &generate_flyback_ngspice_circuit, "Generate Flyback ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_buck_ngspice_circuit", &generate_buck_ngspice_circuit, "Generate Buck ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_boost_ngspice_circuit", &generate_boost_ngspice_circuit, "Generate Boost ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_sepic_ngspice_circuit", &generate_sepic_ngspice_circuit, "Generate SEPIC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_forward_ngspice_circuit", &generate_forward_ngspice_circuit, "Generate Single-Switch Forward ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_two_switch_forward_ngspice_circuit", &generate_two_switch_forward_ngspice_circuit, "Generate Two-Switch Forward ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_active_clamp_forward_ngspice_circuit", &generate_active_clamp_forward_ngspice_circuit, "Generate Active-Clamp Forward ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_push_pull_ngspice_circuit", &generate_push_pull_ngspice_circuit, "Generate Push-Pull ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_isolated_buck_ngspice_circuit", &generate_isolated_buck_ngspice_circuit, "Generate Isolated Buck ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_isolated_buck_boost_ngspice_circuit", &generate_isolated_buck_boost_ngspice_circuit, "Generate Isolated Buck-Boost ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_llc_ngspice_circuit", &generate_llc_ngspice_circuit, "Generate LLC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_cllc_ngspice_circuit", &generate_cllc_ngspice_circuit, "Generate CLLC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_src_ngspice_circuit", &generate_src_ngspice_circuit, "Generate SRC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_dab_ngspice_circuit", &generate_dab_ngspice_circuit, "Generate DAB ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_psfb_ngspice_circuit", &generate_psfb_ngspice_circuit, "Generate PSFB ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_cuk_ngspice_circuit", &generate_cuk_ngspice_circuit, "Generate Cuk ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_zeta_ngspice_circuit", &generate_zeta_ngspice_circuit, "Generate Zeta ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_four_switch_buck_boost_ngspice_circuit", &generate_four_switch_buck_boost_ngspice_circuit, "Generate Four-Switch Buck-Boost ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_weinberg_ngspice_circuit", &generate_weinberg_ngspice_circuit, "Generate Weinberg ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_clllc_ngspice_circuit", &generate_clllc_ngspice_circuit, "Generate CLLLC ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_vienna_ngspice_circuit", &generate_vienna_ngspice_circuit, "Generate Vienna Rectifier ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_pshb_ngspice_circuit", &generate_pshb_ngspice_circuit, "Generate PSHB ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_ahb_ngspice_circuit", &generate_ahb_ngspice_circuit, "Generate Asymmetric Half-Bridge ngspice netlist.", py::arg("inputs"), py::arg("input_voltage_index") = 0, py::arg("operating_point_index") = 0,
        py::call_guard<py::gil_scoped_release>());
    m.def("generate_pfc_ngspice_circuit", &generate_pfc_ngspice_circuit, "Generate PFC ngspice netlist.", py::arg("inputs"), py::arg("dc_resistance") = 0.1, py::arg("simulation_time") = 0.02, py::arg("time_step") = 1e-8,
        py::call_guard<py::gil_scoped_release>());
}

} // namespace PyMKF
