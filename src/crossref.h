#pragma once

#include "common.h"

namespace PyMKF {

// Core cross-referencer: given a reference core (shape + material + gapping) and
// the operating conditions, rank alternatives that could replace it.
json calculate_cross_referenced_core(json referenceCoreJson, json inputsJson,
                                     int64_t referenceNumberTurns, json weightsJson,
                                     int maximumNumberResults);

// Core-material cross-referencer: rank materials that could replace a reference
// material at a given temperature.
json calculate_cross_referenced_core_material(json referenceCoreMaterialJson, double temperature,
                                              json weightsJson, int maximumNumberResults);

void register_crossref_bindings(py::module& m);

} // namespace PyMKF
