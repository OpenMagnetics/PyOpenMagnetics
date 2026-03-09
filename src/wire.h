/**
 * @file wire.h
 * @brief Wire database and calculation functions for PyOpenMagnetics
 *
 * Provides comprehensive functions for querying wire databases, calculating
 * wire dimensions with insulation, and selecting appropriate wires for designs.
 *
 * ## Wire Types
 * - Round: Solid round magnet wire with enamel coating
 * - Litz: Multi-strand twisted wire for reduced AC losses
 * - Rectangular: Flat/strip wire for high current applications
 * - Foil: Ultra-thin conductor for planar magnetics
 *
 * ## Wire Standards
 * - IEC 60317: International standard for enamelled round wire
 * - NEMA MW 1000: North American magnet wire standard
 * - JIS C 3202: Japanese industrial standard
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Query wires
 * wires = pom.get_wire_names()
 * wire = pom.find_wire_by_name("Round 0.5 - Grade 1")
 *
 * # Get wire dimensions
 * outer_diam = pom.get_wire_outer_diameter_enamelled_round(0.5e-3, 1, "IEC 60317")
 *
 * # Find equivalent wire for different application
 * litz_equiv = pom.get_equivalent_wire(wire, "litz", 100000)
 * @endcode
 *
 * @see winding.h for wire placement in coils
 * @see losses.h for wire loss calculations
 */

#pragma once

#include "common.h"

namespace PyMKF {

// ============================================================================
// Wire Retrieval Functions
// ============================================================================

/**
 * @brief Get all available wires from the database
 * @return JSON array of Wire objects with full specifications
 */
json get_wires();

/**
 * @brief Get list of all wire names
 * @return JSON array of wire name strings
 */
json get_wire_names();

/**
 * @brief Get all available wire conductor materials
 * @return JSON array of WireMaterial objects (copper, aluminum, etc.)
 */
json get_wire_materials();

/**
 * @brief Get list of all wire material names
 * @return JSON array of material name strings
 */
json get_wire_material_names();

/**
 * @brief Find complete wire data by name
 * @param wireName Wire name (e.g., "Round 0.5 - Grade 1")
 * @return JSON Wire object with full specification
 */
json find_wire_by_name(json wireName);

/**
 * @brief Find wire conductor material data by name
 * @param wireMaterialName Material name (e.g., "copper", "aluminum")
 * @return JSON WireMaterial object
 */
json find_wire_material_by_name(json wireMaterialName);

/**
 * @brief Find wire by dimension, type, and standard
 * @param dimension Target dimension in meters (diameter for round wire)
 * @param wireTypeJson Wire type ("round", "litz", "rectangular", "foil")
 * @param wireStandardJson Standard ("IEC 60317", "NEMA MW 1000", etc.)
 * @return JSON Wire object matching criteria
 */
json find_wire_by_dimension(double dimension, json wireTypeJson, json wireStandardJson);

// ============================================================================
// Wire Data Functions
// ============================================================================

/**
 * @brief Get complete wire data from winding specification
 * @param windingDataJson JSON Winding object with wire field
 * @return JSON Wire object with complete specification
 */
json get_wire_data(json windingDataJson);

/**
 * @brief Get wire data by name
 * @param name Wire name string
 * @return JSON Wire object
 */
json get_wire_data_by_name(std::string name);

/**
 * @brief Get wire data by standard designation
 * @param standardName Standard wire size (e.g., "AWG 24", "0.50 mm")
 * @return JSON Wire object
 */
json get_wire_data_by_standard_name(std::string standardName);

/**
 * @brief Get strand wire data by standard name (for litz strands)
 * @param standardName Strand size designation
 * @return JSON Wire object for individual strand
 */
json get_strand_by_standard_name(std::string standardName);

/**
 * @brief Get bare conductor diameter by standard name
 * @param standardName Wire size designation
 * @return Conducting diameter in meters
 */
double get_wire_conducting_diameter_by_standard_name(std::string standardName);

// ============================================================================
// Wire Dimension Functions
// ============================================================================

/**
 * @brief Get outer width of rectangular wire including insulation
 * @param conductingWidth Conductor width in meters
 * @param grade Insulation grade (1, 2, 3)
 * @param wireStandardJson Wire standard
 * @return Outer width in meters
 */
double get_wire_outer_width_rectangular(double conductingWidth, int grade, json wireStandardJson);

/**
 * @brief Get outer height of rectangular wire including insulation
 * @param conductingHeight Conductor height in meters
 * @param grade Insulation grade (1, 2, 3)
 * @param wireStandardJson Wire standard
 * @return Outer height in meters
 */
double get_wire_outer_height_rectangular(double conductingHeight, int grade, json wireStandardJson);

/**
 * @brief Get outer diameter of bare litz bundle (no serving)
 * @param conductingDiameter Strand conductor diameter in meters
 * @param numberConductors Number of strands in bundle
 * @param grade Strand insulation grade
 * @param wireStandardJson Wire standard
 * @return Bundle diameter in meters
 */
double get_wire_outer_diameter_bare_litz(double conductingDiameter, int numberConductors, int grade, json wireStandardJson);

/**
 * @brief Get outer diameter of litz wire with serving
 * @param conductingDiameter Strand conductor diameter in meters
 * @param numberConductors Number of strands in bundle
 * @param grade Strand insulation grade
 * @param numberLayers Number of serving layers
 * @param wireStandardJson Wire standard
 * @return Served diameter in meters
 */
double get_wire_outer_diameter_served_litz(double conductingDiameter, int numberConductors, int grade, int numberLayers, json wireStandardJson);

/**
 * @brief Get outer diameter of fully insulated litz wire
 * @param conductingDiameter Strand conductor diameter in meters
 * @param numberConductors Number of strands in bundle
 * @param numberLayers Number of insulation layers
 * @param thicknessLayers Thickness per insulation layer in meters
 * @param grade Strand insulation grade
 * @param wireStandardJson Wire standard
 * @return Insulated diameter in meters
 */
double get_wire_outer_diameter_insulated_litz(double conductingDiameter, int numberConductors, int numberLayers, double thicknessLayers, int grade, json wireStandardJson);

/**
 * @brief Get outer diameter of enamelled round wire
 * @param conductingDiameter Conductor diameter in meters
 * @param grade Insulation grade (1, 2, 3)
 * @param wireStandardJson Wire standard
 * @return Outer diameter in meters
 */
double get_wire_outer_diameter_enamelled_round(double conductingDiameter, int grade, json wireStandardJson);

/**
 * @brief Get outer diameter of insulated round wire
 * @param conductingDiameter Conductor diameter in meters
 * @param numberLayers Number of insulation layers
 * @param thicknessLayers Thickness per layer in meters
 * @param wireStandardJson Wire standard
 * @return Outer diameter in meters
 */
double get_wire_outer_diameter_insulated_round(double conductingDiameter, int numberLayers, double thicknessLayers, json wireStandardJson);

/**
 * @brief Get outer dimensions of any wire type
 * @param wireJson JSON Wire object
 * @return Vector [width, height] or [diameter] in meters
 */
std::vector<double> get_outer_dimensions(json wireJson);

// ============================================================================
// Wire Utility Functions
// ============================================================================

/**
 * @brief Get equivalent wire for comparison or substitution
 * @param oldWireJson JSON Wire object to find equivalent for
 * @param newWireTypeJson Target wire type
 * @param effectivefrequency Operating frequency in Hz
 * @return JSON Wire object representing equivalent
 */
json get_equivalent_wire(json oldWireJson, json newWireTypeJson, double effectivefrequency);

/**
 * @brief Get coating/insulation data for a wire
 * @param wireJson JSON Wire object
 * @return JSON WireCoating object
 */
json get_coating(json wireJson);

/**
 * @brief Get human-readable coating label
 * @param wireJson JSON Wire object
 * @return Coating label string
 */
json get_coating_label(json wireJson);

/**
 * @brief Get wire coating specification by label
 * @param label Coating label string
 * @return JSON WireCoating object
 */
json get_wire_coating_by_label(std::string label);

/**
 * @brief Get available coating labels for a wire type
 * @param wireTypeJson Wire type
 * @return Vector of available coating label strings
 */
std::vector<std::string> get_coating_labels_by_type(json wireTypeJson);

/**
 * @brief Get thickness of wire coating/insulation
 * @param wireJson JSON Wire object
 * @return Coating thickness in meters
 */
double get_coating_thickness(json wireJson);

/**
 * @brief Get relative permittivity of coating
 * @param wireJson JSON Wire object
 * @return Relative permittivity (dimensionless)
 */
double get_coating_relative_permittivity(json wireJson);

/**
 * @brief Get insulation material of wire coating
 * @param wireJson JSON Wire object
 * @return JSON InsulationMaterial object
 */
json get_coating_insulation_material(json wireJson);

// ============================================================================
// Wire Availability Functions
// ============================================================================

/**
 * @brief Get list of all available wire names
 * @return Vector of wire name strings
 */
std::vector<std::string> get_available_wires();

/**
 * @brief Get list of unique wire diameters for a standard
 * @param wireStandardJson Wire standard to query
 * @return Vector of standard size designation strings
 */
std::vector<std::string> get_unique_wire_diameters(json wireStandardJson);

/**
 * @brief Get list of available wire types
 * @return Vector of type strings: "round", "litz", "rectangular", "foil"
 */
std::vector<std::string> get_available_wire_types();

/**
 * @brief Get list of available wire standards
 * @return Vector of standard strings: "IEC 60317", "NEMA MW 1000", etc.
 */
std::vector<std::string> get_available_wire_standards();

/**
 * @brief Register wire-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_wire_bindings(py::module& m);

} // namespace PyMKF
