#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "pybind11_json/pybind11_json.hpp"
#include <magic_enum.hpp>
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
#include "support/Painter.h"
#include "support/Utils.h"

using namespace MAS;
using json = nlohmann::json;
using ordered_json = nlohmann::ordered_json;

namespace py = pybind11;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace PyMKF {

// Global database declaration - defined in module.cpp
extern std::map<std::string, OpenMagnetics::Mas> masDatabase;

} // namespace PyMKF
