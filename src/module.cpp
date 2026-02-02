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
#include "logging.h"

PYBIND11_MODULE(PyOpenMagnetics, m) {
    m.doc() = "OpenMagnetics Python bindings for magnetic component design";

    // Register all module bindings
    PyMKF::register_database_bindings(m);
    PyMKF::register_core_bindings(m);
    PyMKF::register_wire_bindings(m);
    PyMKF::register_bobbin_bindings(m);
    PyMKF::register_winding_bindings(m);
    PyMKF::register_adviser_bindings(m);
    PyMKF::register_losses_bindings(m);
    PyMKF::register_simulation_bindings(m);
    PyMKF::register_plotting_bindings(m);
    PyMKF::register_settings_bindings(m);
    PyMKF::register_utils_bindings(m);
    PyMKF::register_logging_bindings(m);
}