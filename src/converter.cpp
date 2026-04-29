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

namespace PyMKF {

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
    return process_converter_internal(topologyName, converterJson, useNgspice);
}

// Simplified design_magnetics_from_converter using MKF template method
json design_magnetics_from_converter(
    const std::string& topologyName, 
    json converterJson, 
    int maxResults, 
    json coreModeJson, 
    bool useNgspice, 
    json weightsJson) {
    
    (void)useNgspice;  // Template method always uses ngspice
    
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
// Isolated topologies (transformer): pass turns ratios + magnetizing inductance.
template <typename TopologyT>
std::string generate_spice_isolated(const json& converterJson,
                                     const std::vector<double>& turnsRatios,
                                     double magnetizingInductance,
                                     size_t vinIdx, size_t opIdx) {
    TopologyT topology(converterJson);
    topology._assertErrors = true;
    topology.process();
    return topology.generate_ngspice_circuit(turnsRatios, magnetizingInductance, vinIdx, opIdx);
}

// Non-isolated topologies (single inductor): just pass the inductance.
template <typename TopologyT>
std::string generate_spice_inductor(const json& converterJson,
                                     double inductance,
                                     size_t vinIdx, size_t opIdx) {
    TopologyT topology(converterJson);
    topology._assertErrors = true;
    topology.process();
    return topology.generate_ngspice_circuit(inductance, vinIdx, opIdx);
}

}  // namespace

json generate_ngspice_circuit(const std::string& topologyName,
                              json converterJson,
                              std::vector<double> turnsRatios,
                              double magnetizingInductance,
                              size_t vinIdx,
                              size_t opIdx) {
    try {
        std::string spice;
        // Non-isolated single-inductor topologies — magnetizingInductance
        // arg is interpreted as the main inductor value.
        if (topologyName == "buck")
            spice = generate_spice_inductor<OpenMagnetics::Buck>(converterJson, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "boost")
            spice = generate_spice_inductor<OpenMagnetics::Boost>(converterJson, magnetizingInductance, vinIdx, opIdx);
        // Isolated topologies — turnsRatios + magnetizing inductance.
        else if (topologyName == "flyback") spice = generate_spice_isolated<OpenMagnetics::Flyback>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "single_switch_forward") spice = generate_spice_isolated<OpenMagnetics::SingleSwitchForward>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "two_switch_forward")    spice = generate_spice_isolated<OpenMagnetics::TwoSwitchForward>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "active_clamp_forward")  spice = generate_spice_isolated<OpenMagnetics::ActiveClampForward>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "push_pull") spice = generate_spice_isolated<OpenMagnetics::PushPull>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "llc")       spice = generate_spice_isolated<OpenMagnetics::Llc>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        // CLLC is intentionally not wired here yet — its
        // generate_ngspice_circuit signature takes (double turnsRatio,
        // CllcResonantParameters&, ...), which doesn't fit the uniform
        // (vector<double> turnsRatios, double Lm, ...) shape used by every
        // other topology. Add a separate dispatch path when we need it.
        else if (topologyName == "dab")       spice = generate_spice_isolated<OpenMagnetics::Dab>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "phase_shifted_full_bridge" || topologyName == "psfb") spice = generate_spice_isolated<OpenMagnetics::Psfb>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "phase_shifted_half_bridge" || topologyName == "pshb") spice = generate_spice_isolated<OpenMagnetics::Pshb>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "isolated_buck")       spice = generate_spice_isolated<OpenMagnetics::IsolatedBuck>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
        else if (topologyName == "isolated_buck_boost") spice = generate_spice_isolated<OpenMagnetics::IsolatedBuckBoost>(converterJson, turnsRatios, magnetizingInductance, vinIdx, opIdx);
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

    m.def("generate_ngspice_circuit", &generate_ngspice_circuit,
        "Return the canonical ngspice SPICE deck for the topology at a "
        "given operating point, sized from the magnetic design (turns "
        "ratios + magnetizing inductance). Wrapper around each Topology "
        "subclass's generate_ngspice_circuit method; processes the "
        "topology first so internal state (Lr/Cr for LLC, etc.) is "
        "populated. Returns {'netlist': '<spice>'} or {'error': '...'}.",
        py::arg("topology_name"), py::arg("converter_json"),
        py::arg("turns_ratios"), py::arg("magnetizing_inductance"),
        py::arg("vin_index") = 0, py::arg("op_index") = 0);

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
