#pragma once

#include "common.h"

namespace PyMKF {

// Winding functions
json wind(json coilJson, size_t repetitions, json proportionPerWindingJson, json patternJson, json marginPairsJson);
json wind_planar(json coilJson, json stackUpJson, double borderToWireDistance, json wireToWireDistanceJson, json insulationThicknessJson, double coreToLayerDistance);
json wind_by_sections(json coilJson, size_t repetitions, json proportionPerWindingJson, json patternJson, double insulationThickness);
json wind_by_layers(json coilJson, json insulationLayersJson, double insulationThickness);
json wind_by_turns(json coilJson);
json delimit_and_compact(json coilJson);

// Layer and section functions
json get_layers_by_winding_index(json coilJson, int windingIndex);
json get_layers_by_section(json coilJson, json sectionName);
json get_sections_description_conduction(json coilJson);
bool are_sections_and_layers_fitting(json coilJson);
json add_margin_to_section_by_index(json coilJson, int sectionIndex, double top_or_left_margin, double bottom_or_right_margin);

// Winding orientation and alignment
std::vector<std::string> get_available_winding_orientations();
std::vector<std::string> get_available_coil_alignments();

// Number of turns
std::vector<int> calculate_number_turns(int numberTurnsPrimary, json designRequirementsJson);

// Insulation
json get_insulation_materials();
json get_insulation_material_names();
json find_insulation_material_by_name(json insulationMaterialName);
json calculate_insulation(json inputsJson);
json get_insulation_layer_insulation_material(json coilJson, std::string layerName);
json get_isolation_side_from_index(size_t index);

// Insulation helpers
json set_interlayer_insulation(json coilJson, double layerThickness);
json set_intersection_insulation(json coilJson, double layerThickness, int numberInsulationLayers);
json get_solid_insulation_requirements_for_wires(json inputsJson, json patternJson, int repetitions);

// Wire estimation
json guess_round_wire_from_dc_resistance(json coilJson, json dcResistancesJson, double maxError);

void register_winding_bindings(py::module& m);

} // namespace PyMKF
