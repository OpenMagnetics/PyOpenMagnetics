/**
 * @file winding.h
 * @brief Winding placement engine functions for PyOpenMagnetics
 *
 * Provides comprehensive functions for placing wires in magnetic component
 * windings, organizing them into sections, layers, and individual turns.
 * Supports various winding patterns including interleaved and sectored windings.
 *
 * ## Winding Process
 * 1. wind_by_sections(): Divide winding window into sections
 * 2. wind_by_layers(): Organize sections into layers
 * 3. wind_by_turns(): Place individual turns within layers
 * 4. delimit_and_compact(): Optimize turn positions
 *
 * Or use wind() for the complete process in one call.
 *
 * ## Winding Patterns
 * - Contiguous: All turns of one winding together
 * - Interleaved: Alternating primary/secondary sections
 * - Sectored: Multiple sections with insulation between
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * coil = {
 *     "bobbin": bobbin_data,
 *     "functionalDescription": [
 *         {"name": "Primary", "numberTurns": 20, "wire": wire1},
 *         {"name": "Secondary", "numberTurns": 5, "wire": wire2}
 *     ]
 * }
 *
 * # Wind with interleaved pattern (P-S-P-S)
 * result = pom.wind(coil, 2, [0.5, 0.5], [0, 1], [[0.001, 0.001]])
 * @endcode
 *
 * @see bobbin.h for bobbin specifications
 * @see wire.h for wire specifications
 * @see losses.h for winding loss calculations
 */

#pragma once

#include "common.h"

namespace PyMKF {

// ============================================================================
// Winding Functions
// ============================================================================

/**
 * @brief Wind coils on a magnetic core (complete process)
 *
 * @param coilJson JSON object with bobbin and winding functional description
 * @param repetitions Number of times to repeat the winding pattern
 * @param proportionPerWindingJson Proportion of window for each winding
 * @param patternJson Winding order pattern (e.g., [0, 1] for P-S-P-S)
 * @param marginPairsJson Margin tape pairs [[left, right], ...]
 * @return JSON Coil object with complete winding description
 */
json wind(json coilJson, size_t repetitions, json proportionPerWindingJson, json patternJson, json marginPairsJson);

/**
 * @brief Wind planar (PCB) coils with layer stack-up
 *
 * @param coilJson JSON Coil specification
 * @param stackUpJson Layer stack-up array [winding_index per layer]
 * @param borderToWireDistance Clearance from board edge in meters
 * @param wireToWireDistanceJson Spacing between traces per layer
 * @param insulationThicknessJson Insulation between layer pairs
 * @param coreToLayerDistance Gap between core and first layer
 * @return JSON Coil object with planar winding arrangement
 */
json wind_planar(json coilJson, json stackUpJson, double borderToWireDistance, json wireToWireDistanceJson, json insulationThicknessJson, double coreToLayerDistance);

/**
 * @brief Wind coil organized by sections only
 *
 * @param coilJson JSON Coil specification
 * @param repetitions Pattern repetition count
 * @param proportionPerWindingJson Window proportion per winding
 * @param patternJson Winding order pattern
 * @param insulationThickness Inter-section insulation in meters
 * @return JSON Coil with sectionsDescription populated
 */
json wind_by_sections(json coilJson, size_t repetitions, json proportionPerWindingJson, json patternJson, double insulationThickness);

/**
 * @brief Wind coil with layer-level detail from section description
 *
 * @param coilJson JSON Coil with sectionsDescription
 * @param insulationLayersJson Insulation layer specs between windings
 * @param insulationThickness Default insulation thickness in meters
 * @return JSON Coil with layersDescription populated
 */
json wind_by_layers(json coilJson, json insulationLayersJson, double insulationThickness);

/**
 * @brief Wind coil with turn-level detail from layer description
 * @param coilJson JSON Coil with layersDescription
 * @return JSON Coil with turnsDescription populated
 */
json wind_by_turns(json coilJson);

/**
 * @brief Delimit and compact winding layout
 *
 * Optimizes turn positions within the winding window to minimize space usage.
 *
 * @param coilJson JSON Coil with complete winding description
 * @return JSON Coil with optimized turn positions
 */
json delimit_and_compact(json coilJson);

// ============================================================================
// Layer and Section Functions
// ============================================================================

/**
 * @brief Get all layers belonging to a specific winding
 * @param coilJson JSON Coil with layersDescription
 * @param windingIndex Zero-based winding index
 * @return JSON array of Layer objects for that winding
 */
json get_layers_by_winding_index(json coilJson, int windingIndex);

/**
 * @brief Get all layers within a named section
 * @param coilJson JSON Coil with layersDescription
 * @param sectionName Name of the section
 * @return JSON array of Layer objects in that section
 */
json get_layers_by_section(json coilJson, json sectionName);

/**
 * @brief Get only conduction sections (excluding insulation sections)
 * @param coilJson JSON Coil with sectionsDescription
 * @return JSON array of Section objects with type "conduction"
 */
json get_sections_description_conduction(json coilJson);

/**
 * @brief Check if all sections and layers fit within the winding window
 * @param coilJson JSON Coil with winding description
 * @return true if everything fits, false otherwise
 */
bool are_sections_and_layers_fitting(json coilJson);

/**
 * @brief Add margin tape to a section
 * @param coilJson JSON Coil specification
 * @param sectionIndex Zero-based section index
 * @param top_or_left_margin Top/left margin in meters
 * @param bottom_or_right_margin Bottom/right margin in meters
 * @return Updated JSON Coil with margin added
 */
json add_margin_to_section_by_index(json coilJson, int sectionIndex, double top_or_left_margin, double bottom_or_right_margin);

// ============================================================================
// Winding Orientation and Alignment
// ============================================================================

/**
 * @brief Get list of available winding orientation options
 * @return Vector of orientation strings: "contiguous", "overlapping"
 */
std::vector<std::string> get_available_winding_orientations();

/**
 * @brief Get list of available coil alignment options
 * @return Vector of alignment strings: "inner or top", "outer or bottom", "spread", "centered"
 */
std::vector<std::string> get_available_coil_alignments();

// ============================================================================
// Number of Turns
// ============================================================================

/**
 * @brief Calculate optimal number of turns for all windings
 *
 * Given primary turns and design requirements (turns ratios),
 * calculates the turns for all windings.
 *
 * @param numberTurnsPrimary Number of primary turns
 * @param designRequirementsJson JSON DesignRequirements with turnsRatios
 * @return Vector of integer turns for each winding
 */
std::vector<int> calculate_number_turns(int numberTurnsPrimary, json designRequirementsJson);

// ============================================================================
// Insulation Functions
// ============================================================================

/**
 * @brief Get all available insulation materials
 * @return JSON array of InsulationMaterial objects
 */
json get_insulation_materials();

/**
 * @brief Get list of all insulation material names
 * @return JSON array of material name strings
 */
json get_insulation_material_names();

/**
 * @brief Find insulation material data by name
 * @param insulationMaterialName Insulation material name
 * @return JSON InsulationMaterial object
 */
json find_insulation_material_by_name(json insulationMaterialName);

/**
 * @brief Calculate insulation requirements per safety standards
 *
 * Computes creepage, clearance, and dielectric requirements based on
 * IEC 60664-1, IEC 61558-1, IEC 62368-1, or IEC 60335-1 standards.
 *
 * @param inputsJson JSON Inputs with insulation requirements
 * @return JSON object with creepageDistance, clearance, withstandVoltage, etc.
 */
json calculate_insulation(json inputsJson);

/**
 * @brief Get the insulation material used in a specific layer
 * @param coilJson JSON Coil specification
 * @param layerName Name of the insulation layer
 * @return JSON InsulationMaterial object
 */
json get_insulation_layer_insulation_material(json coilJson, std::string layerName);

/**
 * @brief Get isolation side designation from winding index
 * @param index Winding index (0 = primary, 1+ = secondaries)
 * @return JSON IsolationSide string
 */
json get_isolation_side_from_index(size_t index);

/**
 * @brief Register winding-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_winding_bindings(py::module& m);

} // namespace PyMKF
