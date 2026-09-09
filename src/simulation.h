#pragma once

#include "common.h"

namespace PyMKF {

// Simulation
json simulate(json inputsJson, json magneticJson, json modelsData);

// Export
std::string export_magnetic_as_subcircuit(json magneticJson);

// Autocomplete
json mas_autocomplete(json masJson, json configuration);
json magnetic_autocomplete(json magneticJson, json configuration);

// Input processing
json process_inputs(json inputsJson);
json extract_operating_point(json fileJson, size_t numberWindings, double frequency, double desiredMagnetizingInductance, json mapColumnNamesJson);
json extract_map_column_names(json fileJson, size_t numberWindings, double frequency);
json extract_column_names(json fileJson);

// Inductance calculations
json calculate_inductance_matrix(json magneticJson, double frequency, json modelsData);
json calculate_leakage_inductance(json magneticJson, double frequency, size_t sourceIndex);

// Resistance calculations
json calculate_dc_resistance_per_winding(json coilJson, double temperature);
json calculate_resistance_matrix(json magneticJson, double temperature, double frequency);

// Capacitance calculations
json calculate_stray_capacitance(json coilJson, json operatingPointJson, json modelsData);
json calculate_maxwell_capacitance_matrix(json coilJson, json capacitanceAmongWindingsJson);
json calculate_capacitance_matrix(json coilJson, json modelsData);
json calculate_capacitance_models_between_windings(double energy, double voltageDrop, double relativeTurnsRatio);

// Sweep functions
json sweep_impedance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title, bool fast_capacitance);
json sweep_differential_mode_impedance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title);
json sweep_q_factor_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title);
json sweep_winding_resistance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, size_t windingIndex, double temperature, std::string mode, std::string title);
json sweep_resistance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title);
json sweep_magnetizing_inductance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title);
json sweep_magnetizing_inductance_over_temperature(json magneticJson, double start, double stop, size_t numberElements, double frequency, std::string mode, std::string title);
json sweep_magnetizing_inductance_over_dc_bias(json magneticJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title);
json sweep_core_losses_over_frequency(json magneticJson, json operatingPointJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title);
json sweep_winding_losses_over_frequency(json magneticJson, json operatingPointJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title);

// Matrix calculations
json calculate_coupling_coefficient_matrix(json magneticJson, double frequency, json modelsData);
json calculate_leakage_inductance_matrix(json magneticJson, double frequency, json modelsData);

// Export
json export_magnetic_as_symbol(json magneticJson, json inputsJson);

void register_simulation_bindings(py::module& m);

} // namespace PyMKF
