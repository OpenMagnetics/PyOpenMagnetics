#pragma once

#include <pybind11/pybind11.h>

namespace PyMKF {

// Common-mode-choke bindings (calculate_cmc_inputs / calculate_advanced_cmc_inputs), re-pointed at
// the Kirchhoff string API after the converter_models externalisation removed MKF's own
// CommonModeChoke. Split out of converter.cpp (still excluded from the build) so El Choker's CMC
// path works without re-enabling the whole legacy converter surface.
void register_cmc_bindings(pybind11::module& m);

} // namespace PyMKF
