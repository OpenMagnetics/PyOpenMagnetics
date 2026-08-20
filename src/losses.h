#pragma once

#include "common.h"

namespace PyMKF {

// Core losses
json calculate_core_losses(json coreData, json coilData, json inputsData, json modelsData);
json get_core_losses_model_information(json material);
json calculate_steinmetz_coefficients(json dataJson, json rangesJson);
json calculate_steinmetz_coefficients_with_error(json dataJson, json rangesJson);

// Winding losses
json calculate_winding_losses(json magneticJson, json operatingPointJson, double temperature);
json calculate_ohmic_losses(json coilJson, json operatingPointJson, double temperature);
json calculate_magnetic_field_strength_field(json operatingPointJson, json magneticJson);
json calculate_proximity_effect_losses(json coilJson, double temperature, json windingLossesOutputJson, json windingWindowMagneticStrengthFieldOutputJson);
json calculate_skin_effect_losses(json coilJson, json windingLossesOutputJson, double temperature);
json calculate_skin_effect_losses_per_meter(json wireJson, json currentJson, double temperature, double currentDivider);

// DC resistance and losses
double calculate_dc_resistance_per_meter(json wireJson, double temperature);
double calculate_dc_losses_per_meter(json wireJson, json currentJson, double temperature);
double calculate_skin_ac_factor(json wireJson, json currentJson, double temperature);
double calculate_skin_ac_losses_per_meter(json wireJson, json currentJson, double temperature);
double calculate_skin_ac_resistance_per_meter(json wireJson, json currentJson, double temperature);
double calculate_effective_current_density(json wireJson, json currentJson, double temperature);
double calculate_effective_skin_depth(std::string materialName, json currentJson, double temperature);

// Additional loss functions
json get_available_core_losses_methods(json magneticJson);
json get_core_material_available_losses_methods(json materialJson);
json calculate_filling_factor(json coilJson);
json calculate_ac_resistance_coefficients_per_winding(json magneticJson, double temperature, double frequency);

void register_losses_bindings(py::module& m);

} // namespace PyMKF
