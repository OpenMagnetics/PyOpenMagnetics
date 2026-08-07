#include "common.h"
#include "database.h"
#include "core.h"
#include "wire.h"
#include "bobbin.h"
#include "winding.h"
#include "advisers.h"
#include "crossref.h"
#include "converter.h"  // converter surface re-pointed at Kirchhoff api (converter.cpp shims)
#include "cmc.h"  // CMC bindings re-pointed at Kirchhoff api::design_cmc (el-choker's path)
#include "losses.h"
#include "simulation.h"
#include "plotting.h"
#include "settings.h"
#include "utils.h"
#include "logging.h"

namespace PyMKF {

// Get the directory containing the PyOpenMagnetics module
std::string get_module_path() {
    auto module = py::module::import("PyOpenMagnetics");
    return module.attr("__file__").cast<std::string>();
}

} // namespace PyMKF

PYBIND11_MODULE(PyOpenMagnetics, m) {
    m.doc() = "OpenMagnetics Python bindings for magnetic component design";

    // ABT #595: every C++ exception escaping a binding surfaces as PyOpenMagnetics.EngineError
    // (a RuntimeError subclass). The bindings no longer catch-and-stringify into success-shaped
    // return values — errors are Python exceptions, full stop. Registered before the bindings so
    // it runs ahead of pybind11's built-in std::exception -> RuntimeError translator; pybind11's
    // own exceptions (error_already_set, stop_iteration, ...) are re-thrown for the built-in
    // chain to handle.
    static py::exception<std::exception> engineError(m, "EngineError", PyExc_RuntimeError);
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) std::rethrow_exception(p);
        }
        catch (const py::error_already_set&) { throw; }
        catch (const py::builtin_exception&) { throw; }
        catch (const std::exception& e) { PyErr_SetString(engineError.ptr(), e.what()); }
    });

    // Register all module bindings
    PyMKF::register_database_bindings(m);
    PyMKF::register_core_bindings(m);
    PyMKF::register_wire_bindings(m);
    PyMKF::register_bobbin_bindings(m);
    PyMKF::register_winding_bindings(m);
    PyMKF::register_adviser_bindings(m);
    PyMKF::register_crossref_bindings(m);  // core / core-material cross-referencers
    PyMKF::register_converter_bindings(m);  // converter surface via Kirchhoff
    PyMKF::register_cmc_bindings(m);  // CMC via Kirchhoff (calculate_cmc_inputs + advanced)
    PyMKF::register_losses_bindings(m);
    PyMKF::register_simulation_bindings(m);
    PyMKF::register_plotting_bindings(m);
    PyMKF::register_settings_bindings(m);
    PyMKF::register_utils_bindings(m);
    PyMKF::register_logging_bindings(m);
}