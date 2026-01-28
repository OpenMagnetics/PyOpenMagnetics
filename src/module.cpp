/**
 * @file module.cpp
 * @brief Main pybind11 module entry point for PyOpenMagnetics
 *
 * This file creates the Python module 'PyOpenMagnetics' and registers all
 * binding namespaces. It serves as the main entry point when the module
 * is imported in Python.
 *
 * ## Module Structure
 *
 * The PyOpenMagnetics module exposes 183 functions organized into 11 categories:
 *
 * | Category     | Count | Description                           |
 * |-------------|-------|---------------------------------------|
 * | Database    | 15    | Data loading & caching                |
 * | Core        | 42    | Materials, shapes, calculations       |
 * | Wire        | 32    | Wire database & selection             |
 * | Bobbin      | 8     | Bobbin lookup & fitting               |
 * | Winding     | 23    | Coil placement & insulation           |
 * | Advisers    | 4     | Design recommendation                 |
 * | Losses      | 22    | Core & winding loss models            |
 * | Simulation  | 16    | Full EM simulation & matrices         |
 * | Plotting    | 6     | SVG visualization                     |
 * | Settings    | 6     | Configuration & constants             |
 * | Utils       | 9     | Signal processing                     |
 *
 * ## Quick Start
 *
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Load databases
 * pom.load_core_materials()
 * pom.load_core_shapes()
 * pom.load_wires()
 *
 * # Design a magnetic component
 * inputs = {"designRequirements": {...}, "operatingPoints": [...]}
 * processed = pom.process_inputs(inputs)  # CRITICAL: must call first!
 * magnetics = pom.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
 *
 * # Simulate and analyze
 * result = pom.simulate(processed, magnetics[0], {"coreLosses": "IGSE"})
 * @endcode
 *
 * ## Build Information
 *
 * Built with pybind11 for Python/C++ interoperability.
 * Requires C++23 compatible compiler.
 *
 * @see common.h for shared declarations
 * @see https://github.com/OpenMagnetics for project repository
 *
 * @author OpenMagnetics Contributors
 * @copyright MIT License
 */

#include "common.h"
#include "database.h"
#include "core.h"
#include "wire.h"
#include "bobbin.h"
#include "winding.h"
#include "advisers.h"
#include "losses.h"
#include "simulation.h"
#include "plotting.h"
#include "settings.h"
#include "utils.h"

/**
 * @brief PyOpenMagnetics Python module definition
 *
 * PYBIND11_MODULE macro creates the module entry point.
 * All binding registration functions are called here to expose
 * C++ functions to Python.
 *
 * @param PyOpenMagnetics Module name as seen in Python
 * @param m Module handle for registering functions
 */
PYBIND11_MODULE(PyOpenMagnetics, m) {
    m.doc() = R"pbdoc(
        PyOpenMagnetics - Python bindings for magnetic component design

        OpenMagnetics Python module provides comprehensive tools for designing
        transformers, inductors, and chokes for power electronics applications.

        Key Features:
        - 183 functions for magnetic component design
        - Support for 1000+ core shapes and materials
        - Multiple loss models (Steinmetz, iGSE, MSE, etc.)
        - Design recommendation engine
        - SVG visualization output

        Quick Start:
            >>> import PyOpenMagnetics as pom
            >>> pom.load_core_materials()
            >>> pom.load_core_shapes()
            >>> materials = pom.get_core_material_names()

        IMPORTANT: Always call process_inputs() before using adviser functions!
    )pbdoc";

    // Register all module bindings in dependency order
    PyMKF::register_database_bindings(m);   // Database loading (no deps)
    PyMKF::register_core_bindings(m);       // Core materials & shapes
    PyMKF::register_wire_bindings(m);       // Wire database
    PyMKF::register_bobbin_bindings(m);     // Bobbin management
    PyMKF::register_winding_bindings(m);    // Coil winding engine
    PyMKF::register_adviser_bindings(m);    // Design recommendation
    PyMKF::register_losses_bindings(m);     // Loss calculations
    PyMKF::register_simulation_bindings(m); // Full EM simulation
    PyMKF::register_plotting_bindings(m);   // SVG visualization
    PyMKF::register_settings_bindings(m);   // Configuration
    PyMKF::register_utils_bindings(m);      // Utility functions
}
