#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "pybind11_json/pybind11_json.hpp"
#include <magic_enum.hpp>
#include <algorithm>
#include <stdexcept>
#include "json.hpp"

#include <MAS.hpp>
#include "advisers/MagneticAdviser.h"
#include "constructive_models/Bobbin.h"
#include "constructive_models/Coil.h"
#include "constructive_models/Core.h"
#include "constructive_models/Insulation.h"
#include "constructive_models/Magnetic.h"
#include "constructive_models/Mas.h"
#include "constructive_models/NumberTurns.h"
#include "constructive_models/Wire.h"
#include "physical_models/InitialPermeability.h"
#include "physical_models/MagneticEnergy.h"
#include "physical_models/Reluctance.h"
#include "physical_models/Temperature.h"
#include "physical_models/ThermalResistance.h"
#include "physical_models/MagnetizingInductance.h"
#include "physical_models/CoreLosses.h"
#include "physical_models/Resistivity.h"
#include "physical_models/CoreTemperature.h"
#include "physical_models/LeakageInductance.h"
#include "physical_models/Inductance.h"
#include "physical_models/StrayCapacitance.h"
#include "physical_models/WindingOhmicLosses.h"
#include "physical_models/WindingSkinEffectLosses.h"
#include "physical_models/WindingLosses.h"
#include "processors/Inputs.h"
#include "processors/MagneticSimulator.h"
#include "processors/CircuitSimulatorInterface.h"
#include "processors/Sweeper.h"
#include "support/Painter.h"
#include "support/Utils.h"

using namespace MAS;
using json = nlohmann::json;
using ordered_json = nlohmann::ordered_json;

namespace py = pybind11;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace PyMKF {

// THE MODELS DICT NAMES THE GAP-RELUCTANCE MODEL UNDER TWO SPELLINGS, AND BOTH ARE REAL.
// Every Python entry point here has always read "reluctance", settings.cpp publishes that key as
// the default, and it stays the documented name. MKF's own C++ spells the same choice
// "gapReluctance" -- CoreCrossReferencer, MagneticAdviser, MagneticFilter, MagneticFilterLosses
// and CoreAdviserPipeline all use that -- so anyone moving between the two layers reaches for it
// naturally. It used to be accepted and silently dropped: the key was never looked at, the call
// fell back to defaults.reluctanceModelDefault, and a sweep over all nine models returned nine
// identical numbers, which reads as "the model does not matter for this core" rather than "the
// argument was ignored" (heimdall ABT #952 -- it cost a full pass of a real investigation).
//
// Accept both, "reluctance" first so the documented key wins if a caller somehow sets both.
// Unknown KEYS are still ignored on purpose: one dict legitimately carries several subsystems'
// choices ("coreLosses" alongside this one), so a strict reader would break valid callers.
// An unknown model NAME does throw, and now says so -- magic_enum's .value() on an empty
// optional threw a bare "bad optional access" that named neither the key nor the offending value.
inline bool find_reluctance_model(const std::map<std::string, std::string>& models,
                                  OpenMagnetics::ReluctanceModels& reluctanceModelName) {
    for (const char* key : {"reluctance", "gapReluctance"}) {
        auto entry = models.find(key);
        if (entry == models.end()) {
            continue;
        }
        std::string modelNameJsonUpper = entry->second;
        std::transform(modelNameJsonUpper.begin(), modelNameJsonUpper.end(),
                       modelNameJsonUpper.begin(), ::toupper);
        auto parsed = magic_enum::enum_cast<OpenMagnetics::ReluctanceModels>(modelNameJsonUpper);
        if (!parsed.has_value()) {
            std::string known;
            for (auto name : magic_enum::enum_names<OpenMagnetics::ReluctanceModels>()) {
                known += (known.empty() ? "" : ", ") + std::string(name);
            }
            throw std::runtime_error("Unknown reluctance model '" + entry->second + "' given as '"
                                     + std::string(key) + "'. Known models: " + known);
        }
        reluctanceModelName = parsed.value();
        return true;
    }
    return false;
}

inline bool find_reluctance_model(const json& modelsData,
                                  OpenMagnetics::ReluctanceModels& reluctanceModelName) {
    if (modelsData.is_null() || !modelsData.is_object()) {
        return false;
    }
    std::map<std::string, std::string> models;
    for (auto& [key, value] : modelsData.items()) {
        if (value.is_string()) {
            models[key] = value.get<std::string>();
        }
    }
    return find_reluctance_model(models, reluctanceModelName);
}

// Global database declaration - defined in module.cpp
extern std::map<std::string, OpenMagnetics::Mas> masDatabase;

// Get the directory containing the PyOpenMagnetics module
std::string get_module_path();

} // namespace PyMKF
