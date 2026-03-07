#pragma once

#include "common.h"

namespace PyMKF {

// Main generic converter processor
json process_converter(const std::string& topologyName, json converterJson, bool useNgspice = true);

// Combined endpoint: converter -> magnetic designs
json design_magnetics_from_converter(
    const std::string& topologyName, 
    json converterJson, 
    int maxResults, 
    json coreModeJson, 
    bool useNgspice = true, 
    json weightsJson = nullptr);

// Per-topology thin wrappers (from .pyi stubs)
json process_flyback(json flybackJson);
json process_buck(json buckJson);
json process_boost(json boostJson);
json process_single_switch_forward(json forwardJson);
json process_two_switch_forward(json forwardJson);
json process_active_clamp_forward(json forwardJson);
json process_push_pull(json pushPullJson);
json process_isolated_buck(json isolatedBuckJson);
json process_isolated_buck_boost(json isolatedBuckBoostJson);
json process_current_transformer(json ctJson, double turnsRatio, double secondaryResistance = 0.0);

void register_converter_bindings(py::module& m);

} // namespace PyMKF
