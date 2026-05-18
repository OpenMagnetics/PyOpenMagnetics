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

// 2026-05 additions: full coverage of MKF's 24 converter topologies.
json process_cuk(json cukJson);
json process_sepic(json sepicJson);
json process_zeta(json zetaJson);
json process_four_switch_buck_boost(json converterJson);
json process_asymmetric_half_bridge(json converterJson);
json process_weinberg(json converterJson);
json process_vienna(json converterJson);
json process_clllc(json converterJson);
json process_src(json converterJson);

void register_converter_bindings(py::module& m);

} // namespace PyMKF
