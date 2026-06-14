#pragma once

#include "common.h"

namespace PyMKF {

// Core materials
json get_core_materials();
double get_material_permeability(json materialName, double temperature, double magneticFieldDcBias, double frequency);
double get_material_resistivity(json materialName, double temperature);
json get_core_material_steinmetz_coefficients(json materialName, double frequency);
json get_core_material_names();
json get_core_material_names_by_manufacturer(std::string manufacturerName);
json find_core_material_by_name(json materialName);
json get_material_data(std::string materialName);
std::vector<std::string> get_available_core_materials(std::string manufacturer);
std::vector<std::string> get_available_core_manufacturers();

// Core shapes
json get_core_shapes();
json get_core_shape_families();
json get_core_shape_names(bool includeToroidal);
json find_core_shape_by_name(json shapeName);
json get_shape_data(std::string shapeName);
json calculate_shape_data(json shapeJson);
std::vector<std::string> get_available_shape_families();
std::vector<std::string> get_available_core_shape_families();
std::vector<std::string> get_available_core_shapes();
json get_available_cores();

// Core calculations
json calculate_core_data(json coreDataJson, bool includeMaterialData);
json calculate_core_processed_description(json coreDataJson);
json calculate_core_geometrical_description(json coreDataJson);
json calculate_core_gapping(json coreDataJson);
json load_core_data(json coresJson);
json get_core_temperature_dependant_parameters(json coreData, double temperature);
double calculate_core_maximum_magnetic_energy(json coreDataJson, json operatingPointJson);
double calculate_saturation_current(json magneticJson, double temperature);
double calculate_temperature_from_core_thermal_resistance(json coreJson, double totalLosses);

// Gap and reluctance
json calculate_gap_reluctance(json coreGapData, std::string modelNameString);
json get_gap_reluctance_model_information();
double calculate_inductance_from_number_turns_and_gapping(json coreData, json coilData, json operatingPointData, json modelsData);
double calculate_number_turns_from_gapping_and_inductance(json coreData, json coilData, json inputsData, json modelsData);
double calculate_number_turns_from_gapping_and_inductance_legacy(json coreData, json inputsData, json modelsData);
json calculate_gapping_from_number_turns_and_inductance(json coreData, json coilData, json inputsData, std::string gappingTypeJson, int decimals, json modelsData);

// Shape queries by family/manufacturer
json get_available_core_shapes_by_family(std::string familyString);
json get_available_core_shapes_by_manufacturer(std::string manufacturer);
json get_shape_family_dimensions(std::string familyString, std::string familySubtype);
json get_shape_family_subtypes(std::string familyString);
std::vector<std::string> get_available_core_filters();
std::vector<double> get_maximum_dimensions(json magneticJson);
json calculate_core_data_from_shape(json shapeJson);
json calculate_complex_permeability(json materialJson, double frequency);

void register_core_bindings(py::module& m);

} // namespace PyMKF
