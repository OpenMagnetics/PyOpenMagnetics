/**
 * @file common.h
 * @brief Common includes and shared declarations for PyOpenMagnetics bindings
 *
 * This header provides the foundation for all PyOpenMagnetics Python bindings.
 * It includes necessary pybind11 headers, JSON libraries, and the OpenMagnetics
 * MAS (Magnetic Agnostic Structure) library.
 *
 * @note This file must be included before any other PyMKF headers.
 *
 * ## Dependencies
 * - pybind11: Python/C++ binding library
 * - nlohmann/json: JSON serialization
 * - magic_enum: Enum reflection
 * - OpenMagnetics MAS: Core magnetic design library
 *
 * @author OpenMagnetics Contributors
 * @copyright MIT License
 */

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

/**
 * @namespace PyMKF
 * @brief PyOpenMagnetics Python bindings namespace
 *
 * Contains all functions and declarations for the PyOpenMagnetics Python module.
 * Functions in this namespace are exposed to Python via pybind11.
 */
namespace PyMKF {

/**
 * @brief Global in-memory cache for MAS (Magnetic Agnostic Structure) objects
 *
 * This map stores loaded MAS objects keyed by string identifiers.
 * Used for caching magnetic designs between Python calls.
 *
 * @note Defined in module.cpp, declared extern here for shared access.
 *
 * @see load_mas(), read_mas()
 */
extern std::map<std::string, OpenMagnetics::Mas> masDatabase;

} // namespace PyMKF
