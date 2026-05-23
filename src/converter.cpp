#include "converter.h"

// Include all converter model headers
#include "converter_models/Flyback.h"
#include "converter_models/Buck.h"
#include "converter_models/Boost.h"
#include "converter_models/SingleSwitchForward.h"
#include "converter_models/TwoSwitchForward.h"
#include "converter_models/ActiveClampForward.h"
#include "converter_models/PushPull.h"
#include "converter_models/Llc.h"
#include "converter_models/Cllc.h"
#include "converter_models/Dab.h"
#include "converter_models/PhaseShiftedFullBridge.h"
#include "converter_models/PhaseShiftedHalfBridge.h"
#include "converter_models/IsolatedBuck.h"
#include "converter_models/IsolatedBuckBoost.h"
#include "converter_models/CurrentTransformer.h"
#include "converter_models/PowerFactorCorrection.h"
#include "converter_models/Cuk.h"
#include "converter_models/Sepic.h"
#include "converter_models/Zeta.h"
#include "converter_models/FourSwitchBuckBoost.h"
#include "converter_models/AsymmetricHalfBridge.h"
#include "converter_models/Weinberg.h"
#include "converter_models/Vienna.h"
#include "converter_models/Clllc.h"
#include "converter_models/Src.h"
#include "constructive_models/MasMigration.h"

#include <set>
#include <unordered_map>

namespace PyMKF {

// ------------------------------------------------------------------
// Topology name normalization.
//
// dispatch_converter() below uses legacy short forms ("flyback", "buck",
// ...). External callers may pass:
//   * the same short form (canonical internal),
//   * the MAS 1.0 camelCase enum value ("flybackConverter", ...),
//   * or the pre-1.0 Title Case label ("Flyback Converter", ...).
//
// Normalize all three to the internal short form so process_converter()
// and design_magnetics_from_converter() transparently accept any of them.
// ------------------------------------------------------------------
static std::string normalize_topology_name(const std::string& s) {
    static const std::set<std::string> short_forms = {
        "flyback", "advanced_flyback",
        "buck", "advanced_buck",
        "boost", "advanced_boost",
        "single_switch_forward",
        "two_switch_forward",
        "active_clamp_forward",
        "push_pull",
        "llc", "advanced_llc",
        "cllc", "advanced_cllc",
        "dab", "advanced_dab",
        "phase_shifted_full_bridge", "psfb",
        "phase_shifted_half_bridge", "pshb",
        "isolated_buck",
        "isolated_buck_boost",
        "current_transformer",
        "power_factor_correction", "pfc",
        "cuk", "advanced_cuk",
        "sepic", "advanced_sepic",
        "zeta", "advanced_zeta",
        "four_switch_buck_boost", "advanced_four_switch_buck_boost",
        "asymmetric_half_bridge", "advanced_asymmetric_half_bridge",
        "weinberg", "advanced_weinberg",
        "vienna", "advanced_vienna",
        "clllc", "advanced_clllc",
        "src", "advanced_src"
    };
    if (short_forms.count(s)) return s;

    static const std::unordered_map<std::string, std::string> aliases = {
        // MAS 1.0 camelCase (canonical for designRequirements.topology)
        {"flybackConverter",                 "flyback"},
        {"buckConverter",                    "buck"},
        {"boostConverter",                   "boost"},
        {"singleSwitchForwardConverter",     "single_switch_forward"},
        {"twoSwitchForwardConverter",        "two_switch_forward"},
        {"activeClampForwardConverter",      "active_clamp_forward"},
        {"pushPullConverter",                "push_pull"},
        {"llcResonantConverter",             "llc"},
        {"llcConverter",                     "llc"},
        {"cllcResonantConverter",            "cllc"},
        {"cllcConverter",                    "cllc"},
        {"dualActiveBridgeConverter",        "dab"},
        {"phaseShiftedFullBridgeConverter",  "phase_shifted_full_bridge"},
        {"phaseShiftedHalfBridgeConverter",  "phase_shifted_half_bridge"},
        {"isolatedBuckConverter",            "isolated_buck"},
        {"isolatedBuckBoostConverter",       "isolated_buck_boost"},
        {"currentTransformer",               "current_transformer"},
        {"powerFactorCorrection",            "power_factor_correction"},
        {"cukConverter",                      "cuk"},
        {"sepicConverter",                    "sepic"},
        {"zetaConverter",                     "zeta"},
        {"fourSwitchBuckBoostConverter",      "four_switch_buck_boost"},
        {"asymmetricHalfBridgeConverter",     "asymmetric_half_bridge"},
        {"weinbergConverter",                 "weinberg"},
        {"viennaRectifierConverter",          "vienna"},
        {"clllcResonantConverter",            "clllc"},
        {"seriesResonantConverter",           "src"},

        // Pre-1.0 Title Case labels
        {"Flyback Converter",                 "flyback"},
        {"Buck Converter",                    "buck"},
        {"Boost Converter",                   "boost"},
        {"Single-Switch Forward Converter",   "single_switch_forward"},
        {"Two-Switch Forward Converter",      "two_switch_forward"},
        {"Active-Clamp Forward Converter",    "active_clamp_forward"},
        {"Push-Pull Converter",               "push_pull"},
        {"LLC Resonant Converter",            "llc"},
        {"LLC Converter",                     "llc"},
        {"CLLC Resonant Converter",           "cllc"},
        {"Dual Active Bridge Converter",      "dab"},
        {"Phase-Shifted Full Bridge Converter", "phase_shifted_full_bridge"},
        {"Phase-Shifted Half Bridge Converter", "phase_shifted_half_bridge"},
        {"Isolated Buck Converter",           "isolated_buck"},
        {"Isolated Buck-Boost Converter",     "isolated_buck_boost"},
        {"Current Transformer",               "current_transformer"},
        {"Power Factor Correction",           "power_factor_correction"},
        {"Cuk Converter",                     "cuk"},
        {"SEPIC Converter",                   "sepic"},
        {"Sepic Converter",                   "sepic"},
        {"Zeta Converter",                    "zeta"},
        {"Four-Switch Buck-Boost Converter",  "four_switch_buck_boost"},
        {"Asymmetric Half-Bridge Converter",  "asymmetric_half_bridge"},
        {"Weinberg Converter",                "weinberg"},
        {"Vienna Rectifier Converter",        "vienna"},
        {"Vienna Rectifier",                  "vienna"},
        {"CLLLC Resonant Converter",          "clllc"},
        {"Series Resonant Converter",         "src"},
        {"SRC",                               "src"}
    };

    auto it = aliases.find(s);
    if (it != aliases.end()) return it->second;

    // Pass through unchanged; dispatch_converter() will throw if it is
    // truly unknown. We never silently substitute an unrelated topology.
    return s;
}

OpenMagnetics::Inputs process_flyback_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedFlyback converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        // Get design parameters directly from AdvancedFlyback
        std::vector<double> turnsRatios = converter.get_desired_turns_ratios();
        double inductance = converter.get_desired_inductance();
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        
        // Build DesignRequirements manually like AdvancedFlyback::process() does
        OpenMagnetics::DesignRequirements designReqs;
        designReqs.get_mutable_turns_ratios().clear();
        for (auto turnsRatio : turnsRatios) {
            OpenMagnetics::DimensionWithTolerance turnsRatioWithTolerance;
            turnsRatioWithTolerance.set_nominal(turnsRatio);
            designReqs.get_mutable_turns_ratios().push_back(turnsRatioWithTolerance);
        }
        OpenMagnetics::DimensionWithTolerance inductanceWithTolerance;
        inductanceWithTolerance.set_nominal(inductance);
        designReqs.set_magnetizing_inductance(inductanceWithTolerance);
        designReqs.set_topology(MAS::Topologies::FLYBACK_CONVERTER);
        
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::FLYBACK_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_buck_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedBuck converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::BUCK_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::BUCK_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_boost_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedBoost converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::BOOST_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::BOOST_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_single_switch_forward_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedSingleSwitchForward converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::SINGLE_SWITCH_FORWARD_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::SINGLE_SWITCH_FORWARD_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_two_switch_forward_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedTwoSwitchForward converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::TWO_SWITCH_FORWARD_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::TWO_SWITCH_FORWARD_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_active_clamp_forward_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedActiveClampForward converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ACTIVE_CLAMP_FORWARD_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ACTIVE_CLAMP_FORWARD_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_push_pull_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedPushPull converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::PUSH_PULL_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::PUSH_PULL_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_llc_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedLlc converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::LLC_RESONANT_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::LLC_RESONANT_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_cllc_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedCllcConverter converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        return result;
    } else {
        return converter.process();
    }
}

OpenMagnetics::Inputs process_dab_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedDab converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        return result;
    } else {
        return converter.process();
    }
}

OpenMagnetics::Inputs process_psfb_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedPsfb converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        return result;
    } else {
        return converter.process();
    }
}

OpenMagnetics::Inputs process_pshb_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedPshb converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        return result;
    } else {
        return converter.process();
    }
}

OpenMagnetics::Inputs process_isolated_buck_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedIsolatedBuck converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ISOLATED_BUCK_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ISOLATED_BUCK_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_isolated_buck_boost_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedIsolatedBuckBoost converter(converterJson);
    converter._assertErrors = true;
    
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ISOLATED_BUCK_BOOST_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ISOLATED_BUCK_BOOST_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_current_transformer_internal(const json& converterJson) {
    OpenMagnetics::CurrentTransformer converter(converterJson);
    converter._assertErrors = true;
    
    double turnsRatio = converterJson.contains("turnsRatio") ? converterJson["turnsRatio"].get<double>() : 100.0;
    double secondaryResistance = converterJson.contains("secondaryResistance") ? converterJson["secondaryResistance"].get<double>() : 0.0;
    OpenMagnetics::Inputs result = converter.process(turnsRatio, secondaryResistance);
    result.get_mutable_design_requirements().set_topology(MAS::Topologies::CURRENT_TRANSFORMER);
    return result;
}

OpenMagnetics::Inputs process_pfc_internal(const json& converterJson) {
    OpenMagnetics::PowerFactorCorrection converter(converterJson);
    converter._assertErrors = true;
    return converter.process();
}

// ─────────────────────────────────────────────────────────────────────
// 9 new topology bindings (2026-05): Cuk, Sepic, Zeta,
// FourSwitchBuckBoost, AsymmetricHalfBridge, Weinberg, Vienna, Clllc,
// Src. All have first-class implementations in MKF's converter_models/
// — they were just not wired through PyMKF until now.
//
// Pattern groups:
//   * Single-inductor non-isolated (Cuk, Sepic, Zeta, FSBB) follow the
//     Buck/Boost pattern: AdvancedXxx::process() + simulate via inductance.
//   * Isolated with vector turns ratios (AsymHB, Clllc) follow the LLC
//     pattern.
//   * Weinberg has scalar turns ratio (single-secondary topology) — its
//     ngspice dispatch lives separately below.
//   * Vienna and Src have AdvancedXxx classes that only override
//     process_design_requirements(); the inherited Topology::process()
//     handles them. They follow the PFC pattern (no useNgspice branch).
// ─────────────────────────────────────────────────────────────────────

OpenMagnetics::Inputs process_cuk_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedCuk converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::CUK_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::CUK_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_sepic_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedSepic converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::SEPIC_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::SEPIC_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_zeta_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedZeta converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ZETA_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ZETA_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_four_switch_buck_boost_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedFourSwitchBuckBoost converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::FOUR_SWITCH_BUCK_BOOST_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::FOUR_SWITCH_BUCK_BOOST_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_asymmetric_half_bridge_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedAsymmetricHalfBridge converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ASYMMETRIC_HALF_BRIDGE_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::ASYMMETRIC_HALF_BRIDGE_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_weinberg_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedWeinberg converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        if (turnsRatios.empty()) {
            throw std::runtime_error("Weinberg converter requires at least one turns ratio");
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios[0], inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::WEINBERG_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::WEINBERG_CONVERTER);
        return result;
    }
}

OpenMagnetics::Inputs process_clllc_internal(const json& converterJson, bool useNgspice) {
    OpenMagnetics::AdvancedClllc converter(converterJson);
    converter._assertErrors = true;
    if (useNgspice) {
        auto designReqs = converter.process_design_requirements();
        std::vector<double> turnsRatios;
        for (const auto& tr : designReqs.get_turns_ratios()) {
            turnsRatios.push_back(OpenMagnetics::resolve_dimensional_values(tr));
        }
        double inductance = OpenMagnetics::resolve_dimensional_values(designReqs.get_magnetizing_inductance());
        auto operatingPoints = converter.simulate_and_extract_operating_points(turnsRatios, inductance);
        OpenMagnetics::Inputs result;
        result.set_design_requirements(designReqs);
        result.set_operating_points(operatingPoints);
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::CLLLC_RESONANT_CONVERTER);
        return result;
    } else {
        OpenMagnetics::Inputs result = converter.process();
        result.get_mutable_design_requirements().set_topology(MAS::Topologies::CLLLC_RESONANT_CONVERTER);
        return result;
    }
}

// Vienna and Src follow the PFC pattern: AdvancedXxx overrides only
// process_design_requirements(); we invoke the inherited Topology::process()
// via the simple base class on the AdvancedXxx instance. useNgspice has
// no separate path here — process() already handles operating-point
// simulation through the topology pipeline.
OpenMagnetics::Inputs process_vienna_internal(const json& converterJson, bool useNgspice) {
    (void)useNgspice;
    OpenMagnetics::AdvancedVienna converter(converterJson);
    converter._assertErrors = true;
    OpenMagnetics::Inputs result = converter.process();
    result.get_mutable_design_requirements().set_topology(MAS::Topologies::VIENNA_RECTIFIER_CONVERTER);
    return result;
}

OpenMagnetics::Inputs process_src_internal(const json& converterJson, bool useNgspice) {
    (void)useNgspice;
    OpenMagnetics::AdvancedSrc converter(converterJson);
    converter._assertErrors = true;
    OpenMagnetics::Inputs result = converter.process();
    result.get_mutable_design_requirements().set_topology(MAS::Topologies::SERIES_RESONANT_CONVERTER);
    return result;
}

OpenMagnetics::Inputs dispatch_converter(const std::string& topologyName, const json& converterJson, bool useNgspice) {
    if (topologyName == "flyback" || topologyName == "advanced_flyback") {
        return process_flyback_internal(converterJson, useNgspice);
    }
    else if (topologyName == "buck" || topologyName == "advanced_buck") {
        return process_buck_internal(converterJson, useNgspice);
    }
    else if (topologyName == "boost" || topologyName == "advanced_boost") {
        return process_boost_internal(converterJson, useNgspice);
    }
    else if (topologyName == "single_switch_forward") {
        return process_single_switch_forward_internal(converterJson, useNgspice);
    }
    else if (topologyName == "two_switch_forward") {
        return process_two_switch_forward_internal(converterJson, useNgspice);
    }
    else if (topologyName == "active_clamp_forward") {
        return process_active_clamp_forward_internal(converterJson, useNgspice);
    }
    else if (topologyName == "push_pull") {
        return process_push_pull_internal(converterJson, useNgspice);
    }
    else if (topologyName == "llc" || topologyName == "advanced_llc") {
        return process_llc_internal(converterJson, useNgspice);
    }
    else if (topologyName == "cllc" || topologyName == "advanced_cllc") {
        return process_cllc_internal(converterJson, useNgspice);
    }
    else if (topologyName == "dab" || topologyName == "advanced_dab") {
        return process_dab_internal(converterJson, useNgspice);
    }
    else if (topologyName == "phase_shifted_full_bridge" || topologyName == "psfb") {
        return process_psfb_internal(converterJson, useNgspice);
    }
    else if (topologyName == "phase_shifted_half_bridge" || topologyName == "pshb") {
        return process_pshb_internal(converterJson, useNgspice);
    }
    else if (topologyName == "isolated_buck") {
        return process_isolated_buck_internal(converterJson, useNgspice);
    }
    else if (topologyName == "isolated_buck_boost") {
        return process_isolated_buck_boost_internal(converterJson, useNgspice);
    }
    else if (topologyName == "current_transformer") {
        return process_current_transformer_internal(converterJson);
    }
    else if (topologyName == "power_factor_correction" || topologyName == "pfc") {
        return process_pfc_internal(converterJson);
    }
    else if (topologyName == "cuk" || topologyName == "advanced_cuk") {
        return process_cuk_internal(converterJson, useNgspice);
    }
    else if (topologyName == "sepic" || topologyName == "advanced_sepic") {
        return process_sepic_internal(converterJson, useNgspice);
    }
    else if (topologyName == "zeta" || topologyName == "advanced_zeta") {
        return process_zeta_internal(converterJson, useNgspice);
    }
    else if (topologyName == "four_switch_buck_boost" || topologyName == "advanced_four_switch_buck_boost") {
        return process_four_switch_buck_boost_internal(converterJson, useNgspice);
    }
    else if (topologyName == "asymmetric_half_bridge" || topologyName == "advanced_asymmetric_half_bridge") {
        return process_asymmetric_half_bridge_internal(converterJson, useNgspice);
    }
    else if (topologyName == "weinberg" || topologyName == "advanced_weinberg") {
        return process_weinberg_internal(converterJson, useNgspice);
    }
    else if (topologyName == "vienna" || topologyName == "advanced_vienna") {
        return process_vienna_internal(converterJson, useNgspice);
    }
    else if (topologyName == "clllc" || topologyName == "advanced_clllc") {
        return process_clllc_internal(converterJson, useNgspice);
    }
    else if (topologyName == "src" || topologyName == "advanced_src") {
        return process_src_internal(converterJson, useNgspice);
    }
    else {
        throw std::invalid_argument("Unknown topology: " + topologyName);
    }
}

json process_converter_internal(const std::string& topologyName, const json& converterJson, bool useNgspice) {
    try {
        OpenMagnetics::Inputs inputs = dispatch_converter(topologyName, converterJson, useNgspice);
        json result;
        to_json(result, inputs);
        return result;
    }
    catch (const std::exception& e) {
        json error;
        error["error"] = "Exception: " + std::string(e.what());
        return error;
    }
}

json process_converter(const std::string& topologyName, json converterJson, bool useNgspice) {
    // Normalize topology name (accept MAS 1.0 camelCase, pre-1.0 Title Case,
    // and the internal short form) and migrate any pre-1.0 enum strings
    // embedded in the converter JSON (e.g. flyback "mode": "Continuous
    // Conduction Mode" -> "continuousConductionMode") in-place.
    std::string normalized = normalize_topology_name(topologyName);
    OpenMagnetics::compat::migrate_pre_1_0(converterJson);
    return process_converter_internal(normalized, converterJson, useNgspice);
}

// Simplified design_magnetics_from_converter using MKF template method
json design_magnetics_from_converter(
    const std::string& topologyNameRaw,
    json converterJson, 
    int maxResults, 
    json coreModeJson, 
    bool useNgspice, 
    json weightsJson) {
    
    (void)useNgspice;  // Template method always uses ngspice

    // Accept MAS 1.0 camelCase, pre-1.0 Title Case, or internal short form.
    const std::string topologyName = normalize_topology_name(topologyNameRaw);
    OpenMagnetics::compat::migrate_pre_1_0(converterJson);

    try {
        OpenMagnetics::CoreAdviser::CoreAdviserModes coreMode;
        from_json(coreModeJson, coreMode);
        
        std::map<OpenMagnetics::MagneticFilters, double> weights;
        if (!weightsJson.is_null()) {
            for (auto& [key, value] : weightsJson.items()) {
                OpenMagnetics::MagneticFilters filter;
                OpenMagnetics::from_json(key, filter);
                weights[filter] = value;
            }
        }
        
        OpenMagnetics::MagneticAdviser magneticAdviser;
        magneticAdviser.set_core_mode(coreMode);
        
        std::vector<std::pair<OpenMagnetics::Mas, double>> masMagnetics;
        
        // Use MKF template method - handles all converters automatically
        if (topologyName == "flyback" || topologyName == "advanced_flyback") {
            OpenMagnetics::Flyback converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty() 
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "buck" || topologyName == "advanced_buck") {
            OpenMagnetics::Buck converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "boost" || topologyName == "advanced_boost") {
            OpenMagnetics::Boost converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "single_switch_forward") {
            OpenMagnetics::SingleSwitchForward converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "two_switch_forward") {
            OpenMagnetics::TwoSwitchForward converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "active_clamp_forward") {
            OpenMagnetics::ActiveClampForward converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "push_pull") {
            OpenMagnetics::PushPull converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "isolated_buck") {
            OpenMagnetics::IsolatedBuck converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "isolated_buck_boost") {
            OpenMagnetics::IsolatedBuckBoost converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "llc" || topologyName == "advanced_llc") {
            OpenMagnetics::Llc converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "cuk" || topologyName == "advanced_cuk") {
            OpenMagnetics::Cuk converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "sepic" || topologyName == "advanced_sepic") {
            OpenMagnetics::Sepic converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "zeta" || topologyName == "advanced_zeta") {
            OpenMagnetics::Zeta converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "four_switch_buck_boost" || topologyName == "advanced_four_switch_buck_boost") {
            OpenMagnetics::FourSwitchBuckBoost converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "asymmetric_half_bridge" || topologyName == "advanced_asymmetric_half_bridge") {
            OpenMagnetics::AsymmetricHalfBridge converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "weinberg" || topologyName == "advanced_weinberg") {
            OpenMagnetics::Weinberg converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "vienna" || topologyName == "advanced_vienna") {
            OpenMagnetics::Vienna converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "clllc" || topologyName == "advanced_clllc") {
            OpenMagnetics::Clllc converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else if (topologyName == "src" || topologyName == "advanced_src") {
            OpenMagnetics::Src converter(converterJson);
            converter._assertErrors = true;
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic_from_converter(converter, maxResults)
                : magneticAdviser.get_advised_magnetic_from_converter(converter, weights, maxResults);
        }
        else {
            // Fall back to old approach for other topologies
            json inputsJson = process_converter_internal(topologyName, converterJson, useNgspice);
            if (inputsJson.contains("error")) return inputsJson;
            
            OpenMagnetics::Inputs inputs(inputsJson);
            masMagnetics = weights.empty()
                ? magneticAdviser.get_advised_magnetic(inputs, maxResults)
                : magneticAdviser.get_advised_magnetic(inputs, weights, maxResults);
        }
        
        // Build results (same as before)
        auto scoringsPerFilter = magneticAdviser.get_scorings();
        
        json results = json();
        results["data"] = json::array();
        for (size_t i = 0; i < masMagnetics.size(); ++i) {
            auto& masMagnetic = masMagnetics[i].first;
            double scoring = masMagnetics[i].second;
            std::string name = masMagnetic.get_magnetic().get_manufacturer_info().value().get_reference().value();
            json result;
            json masJson;
            to_json(masJson, masMagnetic);
            result["mas"] = masJson;
            result["scoring"] = scoring;
            if (scoringsPerFilter.count(name)) {
                json filterScorings;
                for (auto& filterPair : scoringsPerFilter[name]) {
                    auto filter = filterPair.first;
                    double filterScore = filterPair.second;
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
    catch (const std::exception& e) {
        json error;
        error["error"] = "Exception: " + std::string(e.what());
        return error;
    }
}


json process_flyback(json flybackJson) {
    return process_converter("flyback", flybackJson, true);
}

json process_buck(json buckJson) {
    return process_converter("buck", buckJson, true);
}

json process_boost(json boostJson) {
    return process_converter("boost", boostJson, true);
}

json process_single_switch_forward(json forwardJson) {
    return process_converter("single_switch_forward", forwardJson, true);
}

json process_two_switch_forward(json forwardJson) {
    return process_converter("two_switch_forward", forwardJson, true);
}

json process_active_clamp_forward(json forwardJson) {
    return process_converter("active_clamp_forward", forwardJson, true);
}

json process_push_pull(json pushPullJson) {
    return process_converter("push_pull", pushPullJson, true);
}

json process_isolated_buck(json isolatedBuckJson) {
    return process_converter("isolated_buck", isolatedBuckJson, true);
}

json process_isolated_buck_boost(json isolatedBuckBoostJson) {
    return process_converter("isolated_buck_boost", isolatedBuckBoostJson, true);
}

json process_current_transformer(json ctJson, double turnsRatio, double secondaryResistance) {
    ctJson["turnsRatio"] = turnsRatio;
    ctJson["secondaryResistance"] = secondaryResistance;
    return process_converter("current_transformer", ctJson, true);
}

json process_cuk(json cukJson) { return process_converter("cuk", cukJson, true); }
json process_sepic(json sepicJson) { return process_converter("sepic", sepicJson, true); }
json process_zeta(json zetaJson) { return process_converter("zeta", zetaJson, true); }
json process_four_switch_buck_boost(json j) { return process_converter("four_switch_buck_boost", j, true); }
json process_asymmetric_half_bridge(json j) { return process_converter("asymmetric_half_bridge", j, true); }
json process_weinberg(json j) { return process_converter("weinberg", j, true); }
json process_vienna(json j) { return process_converter("vienna", j, true); }
json process_clllc(json j) { return process_converter("clllc", j, true); }
json process_src(json j) { return process_converter("src", j, true); }

// ─────────────────────────────────────────────────────────────────────
// get_extra_components_inputs (MKF 2026-04-29 API)
//
// Returns a JSON list describing the design requirements / operating
// points of any extra components a topology brings along besides its
// main magnetic — resonant tank caps for LLC, snubber nets, auxiliary
// inductors, etc. The downstream caller can pipe each entry into a
// component-search (TAS) or a fresh PyOM design call.
//
// Each list entry is one of:
//   { "kind": "magnetic",  "inputs": { ...MAS::Inputs JSON... } }
//   { "kind": "capacitor", "inputs": { ...CAS::Inputs JSON... } }
//
// Arguments:
//   topology_name      — same key set as dispatch_converter (e.g. "llc",
//                        "psfb", "active_clamp_forward").
//   converter_json     — the converter spec used to construct the simple
//                        topology class (NOT the AdvancedXxx version).
//   mode               — "IDEAL" or "REAL". IDEAL returns archetypal
//                        requirements without parasitics; REAL refines
//                        with the main magnetic's actual leakage,
//                        winding resistance, etc.
//   magnetic_json      — optional MAS::Magnetic JSON, required by some
//                        topologies in REAL mode. Pass null in IDEAL.
// ─────────────────────────────────────────────────────────────────────

namespace {

// Construct the simple topology subclass (NOT AdvancedXxx), run the
// design pipeline (process() / process_design_requirements()) so the
// internal resonant-tank / extra-component values are populated, and
// then invoke get_extra_components_inputs on it. The simple classes
// own the design physics, so they're what the new API was designed
// against. Some topologies require process() to have run first; we
// invoke it via the SFINAE-detected member that exists on each.
template <typename TopologyT>
std::vector<std::variant<OpenMagnetics::Inputs, CAS::Inputs>>
collect_extra_components(const json& converterJson,
                         OpenMagnetics::ExtraComponentsMode mode,
                         std::optional<OpenMagnetics::Magnetic> magnetic) {
    TopologyT topology(converterJson);
    topology._assertErrors = true;
    // Run process() — the Topology base class entry point that wires
    // process_design_requirements() + process_operating_points() and
    // populates the internal Lr / Cr / inductance ratio that
    // get_extra_components_inputs() reads. The Inputs return value is
    // discarded; we only care about the side effects on `topology`.
    topology.process();
    return topology.get_extra_components_inputs(mode, magnetic);
}

std::vector<std::variant<OpenMagnetics::Inputs, CAS::Inputs>>
dispatch_extra_components(const std::string& topologyName,
                          const json& converterJson,
                          OpenMagnetics::ExtraComponentsMode mode,
                          std::optional<OpenMagnetics::Magnetic> magnetic) {
    if (topologyName == "flyback")
        return collect_extra_components<OpenMagnetics::Flyback>(converterJson, mode, magnetic);
    if (topologyName == "buck")
        return collect_extra_components<OpenMagnetics::Buck>(converterJson, mode, magnetic);
    if (topologyName == "boost")
        return collect_extra_components<OpenMagnetics::Boost>(converterJson, mode, magnetic);
    if (topologyName == "single_switch_forward")
        return collect_extra_components<OpenMagnetics::SingleSwitchForward>(converterJson, mode, magnetic);
    if (topologyName == "two_switch_forward")
        return collect_extra_components<OpenMagnetics::TwoSwitchForward>(converterJson, mode, magnetic);
    if (topologyName == "active_clamp_forward")
        return collect_extra_components<OpenMagnetics::ActiveClampForward>(converterJson, mode, magnetic);
    if (topologyName == "push_pull")
        return collect_extra_components<OpenMagnetics::PushPull>(converterJson, mode, magnetic);
    if (topologyName == "llc")
        return collect_extra_components<OpenMagnetics::Llc>(converterJson, mode, magnetic);
    if (topologyName == "dab")
        return collect_extra_components<OpenMagnetics::Dab>(converterJson, mode, magnetic);
    if (topologyName == "phase_shifted_full_bridge" || topologyName == "psfb")
        return collect_extra_components<OpenMagnetics::Psfb>(converterJson, mode, magnetic);
    if (topologyName == "phase_shifted_half_bridge" || topologyName == "pshb")
        return collect_extra_components<OpenMagnetics::Pshb>(converterJson, mode, magnetic);
    if (topologyName == "cllc")
        return collect_extra_components<OpenMagnetics::CllcConverter>(converterJson, mode, magnetic);
    if (topologyName == "isolated_buck")
        return collect_extra_components<OpenMagnetics::IsolatedBuck>(converterJson, mode, magnetic);
    if (topologyName == "isolated_buck_boost")
        return collect_extra_components<OpenMagnetics::IsolatedBuckBoost>(converterJson, mode, magnetic);
    if (topologyName == "cuk" || topologyName == "advanced_cuk")
        return collect_extra_components<OpenMagnetics::Cuk>(converterJson, mode, magnetic);
    if (topologyName == "sepic" || topologyName == "advanced_sepic")
        return collect_extra_components<OpenMagnetics::Sepic>(converterJson, mode, magnetic);
    if (topologyName == "zeta" || topologyName == "advanced_zeta")
        return collect_extra_components<OpenMagnetics::Zeta>(converterJson, mode, magnetic);
    if (topologyName == "four_switch_buck_boost" || topologyName == "advanced_four_switch_buck_boost")
        return collect_extra_components<OpenMagnetics::FourSwitchBuckBoost>(converterJson, mode, magnetic);
    if (topologyName == "asymmetric_half_bridge" || topologyName == "advanced_asymmetric_half_bridge")
        return collect_extra_components<OpenMagnetics::AsymmetricHalfBridge>(converterJson, mode, magnetic);
    if (topologyName == "weinberg" || topologyName == "advanced_weinberg")
        return collect_extra_components<OpenMagnetics::Weinberg>(converterJson, mode, magnetic);
    if (topologyName == "clllc" || topologyName == "advanced_clllc")
        return collect_extra_components<OpenMagnetics::Clllc>(converterJson, mode, magnetic);
    if (topologyName == "src" || topologyName == "advanced_src")
        return collect_extra_components<OpenMagnetics::Src>(converterJson, mode, magnetic);
    // Vienna intentionally omitted: AdvancedVienna's MKF class does not
    // expose get_extra_components_inputs() — the rectifier brings no
    // detached design-requirement components beyond the boost inductor.
    throw std::invalid_argument(
        "get_extra_components_inputs: topology '" + topologyName +
        "' has no extra-components dispatch (or hasn't been wired in PyMKF)."
    );
}

}  // namespace

// ─────────────────────────────────────────────────────────────────────
// generate_ngspice_circuit (MKF native SPICE generator)
//
// Returns the canonical ngspice deck for a converter at a given operating
// point, sized from the magnetic that was designed in Phase 3. This
// replaces hand-rolled netlist templates on the Proteus side: MKF owns
// the topology wiring (rectifier polarity, gate-drive timing, dead-time,
// snubbers, K-coupling) so the simulation always validates the actual
// designed magnetic.
//
// Args mirror the C++ method: turns_ratios (Np:Ns vector), magnetizing
// inductance, optional vin / operating-point indices. The simple
// topology class is constructed and process()'d first so internal state
// (Lr / Cr for LLC, etc.) is populated before deck generation.
// ─────────────────────────────────────────────────────────────────────
namespace {
// Apply optional bridge simulation mode override on a topology instance.
// Must be called BEFORE topology.process() because process() consults the
// mode when computing dead time and other timing parameters.
//
// modeStr accepts:
//   "" | "default" | "pulse" | "behavioral_pulse" → no-op (BEHAVIORAL_PULSE
//       stays as default; safe for non-bridge topologies because
//       set_bridge_simulation_mode throws if you try to force PULSE on a
//       non-bridge topology).
//   "switch" | "voltage_controlled_switch" → set VOLTAGE_CONTROLLED_SWITCH,
//       producing a real SW1/body-diode/snubber bridge instead of a single
//       dependent V-source. Required when downstream tooling needs to size
//       the bridge MOSFETs (e.g. Heaviside's TAS decomposer).
//   anything else → returns false so the caller can raise a clear error.
template <typename TopologyT>
bool apply_bridge_simulation_mode(TopologyT& topology, const std::string& modeStr) {
    if (modeStr.empty() || modeStr == "default" ||
        modeStr == "pulse" || modeStr == "behavioral_pulse") {
        return true;
    }
    if (modeStr == "switch" || modeStr == "voltage_controlled_switch") {
        topology.set_bridge_simulation_mode(
            OpenMagnetics::BridgeSimulationMode::VOLTAGE_CONTROLLED_SWITCH);
        return true;
    }
    return false;
}

// Apply a partial SpiceSimulationConfig override from a JSON dict. Missing
// keys keep the per-topology default. Unknown keys are silently ignored so
// that callers built against an older binding still work after new fields
// are added.
//
// Must be called BEFORE topology.process() because the config is read by
// the netlist emitters in generate_ngspice_circuit (which runs after
// process()).
template <typename TopologyT>
void apply_spice_simulation_config(TopologyT& topology, const json& cfgJson) {
    if (cfgJson.is_null()) return;
    if (!cfgJson.is_object()) {
        throw std::runtime_error(
            "generate_ngspice_circuit: spice_config must be a JSON object");
    }
    if (cfgJson.empty()) return;

    OpenMagnetics::SpiceSimulationConfig cfg = topology.spice_config();
    auto take_d = [&](const char* k, double& dst) {
        auto it = cfgJson.find(k);
        if (it != cfgJson.end() && it->is_number()) dst = it->get<double>();
    };
    auto take_i = [&](const char* k, int& dst) {
        auto it = cfgJson.find(k);
        if (it != cfgJson.end() && it->is_number_integer()) dst = it->get<int>();
    };
    auto take_s = [&](const char* k, std::string& dst) {
        auto it = cfgJson.find(k);
        if (it != cfgJson.end() && it->is_string()) dst = it->get<std::string>();
    };
    take_d("pwmHigh",                        cfg.pwmHigh);
    take_d("pwmRise",                        cfg.pwmRise);
    take_d("pwmFall",                        cfg.pwmFall);
    take_d("swModelVT",                      cfg.swModelVT);
    take_d("swModelVH",                      cfg.swModelVH);
    take_d("swModelRON",                     cfg.swModelRON);
    take_d("swModelROFF",                    cfg.swModelROFF);
    take_d("snubR",                          cfg.snubR);
    take_d("snubC",                          cfg.snubC);
    take_d("snubRReal",                      cfg.snubRReal);
    take_d("diodeIS",                        cfg.diodeIS);
    take_d("diodeRS",                        cfg.diodeRS);
    take_d("outputCapacitance",              cfg.outputCapacitance);
    take_d("outputCapInitialChargeFraction", cfg.outputCapInitialChargeFraction);
    take_i("samplesPerPeriod",               cfg.samplesPerPeriod);
    take_d("relTol",                         cfg.relTol);
    take_d("absTol",                         cfg.absTol);
    take_d("vnTol",                          cfg.vnTol);
    take_i("itl1",                           cfg.itl1);
    take_i("itl4",                           cfg.itl4);
    take_s("method",                         cfg.method);
    take_d("trTol",                          cfg.trTol);
    topology.set_spice_config(std::move(cfg));
}

// Isolated topologies (transformer): pass turns ratios + magnetizing inductance.
template <typename TopologyT>
std::string generate_spice_isolated(const json& converterJson,
                                     const std::vector<double>& turnsRatios,
                                     double magnetizingInductance,
                                     size_t vinIdx, size_t opIdx,
                                     const std::string& bridgeMode,
                                     const json& spiceConfig) {
    TopologyT topology(converterJson);
    topology._assertErrors = true;
    if (!apply_bridge_simulation_mode(topology, bridgeMode)) {
        throw std::runtime_error(
            "generate_ngspice_circuit: unknown bridge_simulation_mode '" +
            bridgeMode + "' — expected '', 'pulse', or 'switch'");
    }
    apply_spice_simulation_config(topology, spiceConfig);
    topology.process();
    return topology.generate_ngspice_circuit(turnsRatios, magnetizingInductance, vinIdx, opIdx);
}

// Non-isolated topologies (single inductor): just pass the inductance.
template <typename TopologyT>
std::string generate_spice_inductor(const json& converterJson,
                                     double inductance,
                                     size_t vinIdx, size_t opIdx,
                                     const std::string& bridgeMode,
                                     const json& spiceConfig) {
    TopologyT topology(converterJson);
    topology._assertErrors = true;
    if (!apply_bridge_simulation_mode(topology, bridgeMode)) {
        throw std::runtime_error(
            "generate_ngspice_circuit: unknown bridge_simulation_mode '" +
            bridgeMode + "' — expected '', 'pulse', or 'switch'");
    }
    apply_spice_simulation_config(topology, spiceConfig);
    topology.process();
    return topology.generate_ngspice_circuit(inductance, vinIdx, opIdx);
}

// Isolated topologies with a single secondary winding (Weinberg): the
// generate_ngspice_circuit signature takes a scalar turns ratio rather
// than a vector. We pass turnsRatios[0] if available, otherwise 1.0.
template <typename TopologyT>
std::string generate_spice_isolated_scalar(const json& converterJson,
                                            const std::vector<double>& turnsRatios,
                                            double magnetizingInductance,
                                            size_t vinIdx, size_t opIdx,
                                            const std::string& bridgeMode,
                                            const json& spiceConfig) {
    TopologyT topology(converterJson);
    topology._assertErrors = true;
    if (!apply_bridge_simulation_mode(topology, bridgeMode)) {
        throw std::runtime_error(
            "generate_ngspice_circuit: unknown bridge_simulation_mode '" +
            bridgeMode + "' — expected '', 'pulse', or 'switch'");
    }
    apply_spice_simulation_config(topology, spiceConfig);
    topology.process();
    double turnsRatio = turnsRatios.empty() ? 1.0 : turnsRatios[0];
    return topology.generate_ngspice_circuit(turnsRatio, magnetizingInductance, vinIdx, opIdx);
}

}  // namespace

json generate_ngspice_circuit(const std::string& topologyName,
                              json converterJson,
                              std::vector<double> turnsRatios,
                              double magnetizingInductance,
                              size_t vinIdx,
                              size_t opIdx,
                              std::string bridgeMode,
                              json spiceConfig) {
    try {
        std::string spice;
        // Non-isolated single-inductor topologies — magnetizingInductance
        // arg is interpreted as the main inductor value.
        if (topologyName == "buck")
            spice = generate_spice_inductor<OpenMagnetics::Buck>(converterJson, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "boost")
            spice = generate_spice_inductor<OpenMagnetics::Boost>(converterJson, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        // Isolated topologies — turnsRatios + magnetizing inductance.
        else if (topologyName == "flyback") spice = generate_spice_isolated<OpenMagnetics::Flyback>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "single_switch_forward") spice = generate_spice_isolated<OpenMagnetics::SingleSwitchForward>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "two_switch_forward")    spice = generate_spice_isolated<OpenMagnetics::TwoSwitchForward>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "active_clamp_forward")  spice = generate_spice_isolated<OpenMagnetics::ActiveClampForward>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "push_pull") spice = generate_spice_isolated<OpenMagnetics::PushPull>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "llc")       spice = generate_spice_isolated<OpenMagnetics::Llc>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        // CLLC has a distinct signature: generate_ngspice_circuit takes
        // (double turnsRatio, const CllcResonantParameters&, ...) instead
        // of the uniform (vector<double> turnsRatios, double Lm, ...)
        // shape, because CLLC needs the full resonant-parameter set
        // (Lr1, Cr1, Lr2, Cr2, Lm) computed by
        // CllcConverter::calculate_resonant_parameters() — a single
        // magnetizing inductance scalar would not determine the tank.
        else if (topologyName == "cllc" || topologyName == "advanced_cllc") {
            OpenMagnetics::AdvancedCllcConverter topology(converterJson);
            topology._assertErrors = true;
            if (!apply_bridge_simulation_mode(topology, bridgeMode)) {
                throw std::runtime_error(
                    "generate_ngspice_circuit: unknown bridge_simulation_mode '" +
                    bridgeMode + "' — expected '', 'pulse', or 'switch'");
            }
            apply_spice_simulation_config(topology, spiceConfig);
            topology.process();
            auto params = topology.calculate_resonant_parameters();
            double turnsRatio = turnsRatios.empty() ? 1.0 : turnsRatios[0];
            spice = topology.generate_ngspice_circuit(turnsRatio, params, vinIdx, opIdx);
        }
        else if (topologyName == "dab")       spice = generate_spice_isolated<OpenMagnetics::Dab>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "phase_shifted_full_bridge" || topologyName == "psfb") spice = generate_spice_isolated<OpenMagnetics::Psfb>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "phase_shifted_half_bridge" || topologyName == "pshb") spice = generate_spice_isolated<OpenMagnetics::Pshb>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "isolated_buck")       spice = generate_spice_isolated<OpenMagnetics::IsolatedBuck>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "isolated_buck_boost") spice = generate_spice_isolated<OpenMagnetics::IsolatedBuckBoost>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        // Single-inductor non-isolated (2026-05): Cuk, Sepic, Zeta, FSBB.
        else if (topologyName == "cuk" || topologyName == "advanced_cuk")
            spice = generate_spice_inductor<OpenMagnetics::Cuk>(converterJson, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "sepic" || topologyName == "advanced_sepic")
            spice = generate_spice_inductor<OpenMagnetics::Sepic>(converterJson, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "zeta" || topologyName == "advanced_zeta")
            spice = generate_spice_inductor<OpenMagnetics::Zeta>(converterJson, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "four_switch_buck_boost" || topologyName == "advanced_four_switch_buck_boost")
            spice = generate_spice_inductor<OpenMagnetics::FourSwitchBuckBoost>(converterJson, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        // Isolated with vector turns ratios (2026-05): AsymHB, Clllc, Src, Vienna.
        else if (topologyName == "asymmetric_half_bridge" || topologyName == "advanced_asymmetric_half_bridge")
            spice = generate_spice_isolated<OpenMagnetics::AsymmetricHalfBridge>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "clllc" || topologyName == "advanced_clllc")
            spice = generate_spice_isolated<OpenMagnetics::Clllc>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "src" || topologyName == "advanced_src")
            spice = generate_spice_isolated<OpenMagnetics::Src>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        else if (topologyName == "vienna" || topologyName == "advanced_vienna")
            spice = generate_spice_isolated<OpenMagnetics::Vienna>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        // Isolated with scalar turns ratio (single secondary): Weinberg.
        else if (topologyName == "weinberg" || topologyName == "advanced_weinberg")
            spice = generate_spice_isolated_scalar<OpenMagnetics::Weinberg>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx, bridgeMode, spiceConfig);
        // PFC has a distinct method signature — (inductance, dcResistance,
        // simulationTime, timeStep) — because its deck simulates over a
        // line cycle rather than a switching cycle. Use the method's
        // defaults for dcResistance/simulationTime/timeStep; vinIdx/opIdx
        // are not meaningful for PFC (line voltage drives the operating
        // point).
        else if (topologyName == "power_factor_correction"
              || topologyName == "advanced_power_factor_correction"
              || topologyName == "pfc") {
            OpenMagnetics::PowerFactorCorrection topology(converterJson);
            topology._assertErrors = true;
            apply_spice_simulation_config(topology, spiceConfig);
            topology.process();
            spice = topology.generate_ngspice_circuit(magnetizingInductance);
        }
        else return json{{"error", "generate_ngspice_circuit: unknown topology '" + topologyName + "'"}};
        return json{{"netlist", spice}};
    } catch (const std::exception& exc) {
        return json{{"error", std::string("generate_ngspice_circuit: ") + exc.what()}};
    }
}

json get_extra_components_inputs(const std::string& topologyName,
                                 json converterJson,
                                 const std::string& modeStr,
                                 json magneticJson) {
    try {
        OpenMagnetics::ExtraComponentsMode mode;
        if (modeStr == "IDEAL" || modeStr == "ideal")
            mode = OpenMagnetics::ExtraComponentsMode::IDEAL;
        else if (modeStr == "REAL" || modeStr == "real")
            mode = OpenMagnetics::ExtraComponentsMode::REAL;
        else
            return json{{"error", "mode must be 'IDEAL' or 'REAL', got: " + modeStr}};

        std::optional<OpenMagnetics::Magnetic> magnetic;
        if (!magneticJson.is_null()) {
            magnetic = OpenMagnetics::Magnetic(magneticJson);
        }

        auto components = dispatch_extra_components(topologyName, converterJson, mode, magnetic);

        json out = json::array();
        for (const auto& comp : components) {
            json entry;
            std::visit([&entry](const auto& inputs) {
                using T = std::decay_t<decltype(inputs)>;
                json inputsJson;
                to_json(inputsJson, inputs);
                if constexpr (std::is_same_v<T, OpenMagnetics::Inputs>) {
                    entry["kind"] = "magnetic";
                } else {
                    // CAS::Inputs
                    entry["kind"] = "capacitor";
                }
                entry["inputs"] = inputsJson;
            }, comp);
            out.push_back(entry);
        }
        return out;
    } catch (const std::exception& exc) {
        return json{{"error", std::string("get_extra_components_inputs: ") + exc.what()}};
    }
}

void register_converter_bindings(py::module& m) {
    m.def("process_converter", &process_converter,
        "Process a converter topology specification to Inputs.",
        py::arg("topology_name"), py::arg("converter_json"), py::arg("use_ngspice") = true);
    
    m.def("design_magnetics_from_converter", &design_magnetics_from_converter,
        "Design magnetic components from a converter specification.",
        py::arg("topology_name"), py::arg("converter_json"), 
        py::arg("max_results") = 1, py::arg("core_mode_json") = "available cores",
        py::arg("use_ngspice") = true, py::arg("weights_json") = nullptr);
    
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

    // 2026-05 additions: full coverage of MKF's 24 converter topologies.
    m.def("process_cuk", &process_cuk, "Process Cuk converter.", py::arg("cuk"));
    m.def("process_sepic", &process_sepic, "Process SEPIC converter.", py::arg("sepic"));
    m.def("process_zeta", &process_zeta, "Process Zeta converter.", py::arg("zeta"));
    m.def("process_four_switch_buck_boost", &process_four_switch_buck_boost,
        "Process Four-Switch Buck-Boost converter.", py::arg("converter"));
    m.def("process_asymmetric_half_bridge", &process_asymmetric_half_bridge,
        "Process Asymmetric Half-Bridge converter.", py::arg("converter"));
    m.def("process_weinberg", &process_weinberg, "Process Weinberg converter.", py::arg("converter"));
    m.def("process_vienna", &process_vienna, "Process Vienna Rectifier converter.", py::arg("converter"));
    m.def("process_clllc", &process_clllc, "Process CLLLC Resonant converter.", py::arg("converter"));
    m.def("process_src", &process_src, "Process Series Resonant converter (SRC).", py::arg("converter"));

    m.def("generate_ngspice_circuit", &generate_ngspice_circuit,
        "Return the canonical ngspice SPICE deck for the topology at a "
        "given operating point, sized from the magnetic design (turns "
        "ratios + magnetizing inductance). Wrapper around each Topology "
        "subclass's generate_ngspice_circuit method; processes the "
        "topology first so internal state (Lr/Cr for LLC, etc.) is "
        "populated. Returns {'netlist': '<spice>'} or {'error': '...'}.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("turns_ratios"), py::arg("magnetizing_inductance"),
        py::arg("vin_index") = 0, py::arg("op_index") = 0,
        py::arg("bridge_simulation_mode") = std::string(""),
        py::arg("spice_config") = nlohmann::json::object());

    m.def("get_extra_components_inputs", &get_extra_components_inputs,
        "Return the design requirements for extra components a topology brings "
        "alongside its main magnetic — resonant tank Lr/Cr for LLC, snubber "
        "components for PSFB, etc. Each entry is {kind: 'magnetic'|'capacitor', "
        "inputs: <MAS or CAS Inputs JSON>}. Mode 'IDEAL' returns archetypal "
        "requirements; 'REAL' refines using the supplied main magnetic's "
        "leakage / DCR / etc.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("mode") = "IDEAL", py::arg("magnetic_json") = nullptr);
}

} // namespace PyMKF
