/**
 * @file core.h
 * @brief Core material and shape query functions for PyOpenMagnetics
 *
 * Provides comprehensive functions for querying core materials and shapes,
 * calculating core parameters, and performing inductance/gap calculations.
 *
 * ## Core Materials
 * Supported manufacturers: TDK/EPCOS, Ferroxcube, Fair-Rite, Magnetics Inc, Micrometals
 * Material types: Ferrite (MnZn, NiZn), Iron Powder, Amorphous, Nanocrystalline
 *
 * ## Core Shapes
 * Families: E, EI, EFD, EQ, ER, ETD, EC, PQ, PM, RM, T (toroidal), P, PT, U, UI, LP
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Query materials
 * materials = pom.get_core_material_names()
 * n87 = pom.find_core_material_by_name("N87")
 * steinmetz = pom.get_core_material_steinmetz_coefficients("N87", 100000)
 *
 * # Query shapes
 * shapes = pom.get_core_shape_names(include_toroidal=True)
 * e42 = pom.find_core_shape_by_name("E 42/21/15")
 *
 * # Calculate inductance
 * L = pom.calculate_inductance_from_number_turns_and_gapping(core, coil, op, models)
 * @endcode
 *
 * @see database.h for loading databases
 * @see losses.h for core loss calculations
 */

#pragma once

#include "common.h"

namespace PyMKF {

// ============================================================================
// Core Material Functions
// ============================================================================

/**
 * @brief Get all available core materials from the database
 * @return JSON array of CoreMaterial objects with full specifications
 */
json get_core_materials();

/**
 * @brief Calculate initial permeability under specific conditions
 * @param materialName Material name or JSON object
 * @param temperature Temperature in Celsius
 * @param magneticFieldDcBias DC magnetic field bias in A/m
 * @param frequency Operating frequency in Hz
 * @return Initial relative permeability (dimensionless)
 */
double get_material_permeability(json materialName, double temperature, double magneticFieldDcBias, double frequency);

/**
 * @brief Calculate electrical resistivity for a core material
 * @param materialName Material name or JSON object
 * @param temperature Temperature in Celsius
 * @return Resistivity in Ohm·m
 */
double get_material_resistivity(json materialName, double temperature);

/**
 * @brief Get Steinmetz coefficients for core loss calculation
 *
 * Returns k, alpha, beta for: Pv = k * f^alpha * B^beta
 *
 * @param materialName Material name or JSON object
 * @param frequency Operating frequency in Hz for coefficient selection
 * @return JSON SteinmetzCoreLossesMethodRangeDatum with k, alpha, beta
 */
json get_core_material_steinmetz_coefficients(json materialName, double frequency);

/**
 * @brief Get list of all core material names
 * @return JSON array of material name strings
 */
json get_core_material_names();

/**
 * @brief Get core material names filtered by manufacturer
 * @param manufacturerName Manufacturer name (e.g., "TDK", "Ferroxcube")
 * @return JSON array of material name strings
 */
json get_core_material_names_by_manufacturer(std::string manufacturerName);

/**
 * @brief Find complete core material data by name
 * @param materialName Material name (e.g., "3C95", "N87")
 * @return JSON CoreMaterial object with full specification
 */
json find_core_material_by_name(json materialName);

/**
 * @brief Get material data by name (alias for find_core_material_by_name)
 * @param materialName Material name string
 * @return JSON CoreMaterial object
 */
json get_material_data(std::string materialName);

/**
 * @brief Get list of available core materials, optionally filtered by manufacturer
 * @param manufacturer Manufacturer name filter (empty for all)
 * @return Vector of material name strings
 */
std::vector<std::string> get_available_core_materials(std::string manufacturer);

/**
 * @brief Get list of all core material manufacturers
 * @return Vector of manufacturer name strings
 */
std::vector<std::string> get_available_core_manufacturers();

// ============================================================================
// Core Shape Functions
// ============================================================================

/**
 * @brief Get all available core shapes from the database
 * @return JSON array of CoreShape objects
 */
json get_core_shapes();

/**
 * @brief Get list of unique core shape families
 * @return JSON array of CoreShapeFamily strings
 */
json get_core_shape_families();

/**
 * @brief Get list of core shape names
 * @param includeToroidal Whether to include toroidal shapes
 * @return JSON array of shape name strings
 */
json get_core_shape_names(bool includeToroidal);

/**
 * @brief Find complete core shape data by name
 * @param shapeName Shape name (e.g., "E 42/21/15", "ETD 49/25/16")
 * @return JSON CoreShape object with full dimensional data
 */
json find_core_shape_by_name(json shapeName);

/**
 * @brief Get shape data by name
 * @param shapeName Shape name string
 * @return JSON CoreShape object
 */
json get_shape_data(std::string shapeName);

/**
 * @brief Calculate complete core data from shape specification
 * @param shapeJson JSON CoreShape object
 * @return JSON Core object with processed dimensions
 */
json calculate_shape_data(json shapeJson);

/**
 * @brief Get list of all shape family types
 * @return Vector of family name strings
 */
std::vector<std::string> get_available_shape_families();

/**
 * @brief Get list of all core shape families (alias)
 * @return Vector of family name strings
 */
std::vector<std::string> get_available_core_shape_families();

/**
 * @brief Get list of all available core shape names
 * @return Vector of shape name strings
 */
std::vector<std::string> get_available_core_shapes();

/**
 * @brief Get all pre-configured cores from database
 * @return JSON array of Core objects
 */
json get_available_cores();

// ============================================================================
// Core Calculation Functions
// ============================================================================

/**
 * @brief Process core functional description and compute derived parameters
 *
 * Calculates effective magnetic parameters (Ae, le, Ve), winding window
 * dimensions, column geometry, and geometrical description.
 *
 * @param coreDataJson JSON object with functionalDescription
 * @param includeMaterialData Whether to include full material curves
 * @return JSON Core object with all descriptions populated
 */
json calculate_core_data(json coreDataJson, bool includeMaterialData);

/**
 * @brief Calculate only the processed description for a core
 * @param coreDataJson JSON object with functionalDescription
 * @return JSON CoreProcessedDescription with effectiveParameters
 */
json calculate_core_processed_description(json coreDataJson);

/**
 * @brief Calculate geometrical description for visualization
 * @param coreDataJson JSON object with functionalDescription
 * @return JSON array of CoreGeometricalDescriptionElement objects
 */
json calculate_core_geometrical_description(json coreDataJson);

/**
 * @brief Process and calculate gapping configuration
 * @param coreDataJson JSON object with core and gapping specification
 * @return JSON array of processed CoreGap objects
 */
json calculate_core_gapping(json coreDataJson);

/**
 * @brief Load and process multiple cores from JSON array
 * @param coresJson JSON array of core specifications
 * @return JSON array of processed Core objects
 */
json load_core_data(json coresJson);

/**
 * @brief Get temperature-dependent magnetic parameters
 * @param coreData JSON object with core specification
 * @param temperature Temperature in Celsius
 * @return JSON with Bsat, Hsat, permeability, reluctance, resistivity
 */
json get_core_temperature_dependant_parameters(json coreData, double temperature);

/**
 * @brief Calculate maximum magnetic energy storage capacity
 * @param coreDataJson JSON object with core specification
 * @param operatingPointJson JSON operating point (optional, for DC bias)
 * @return Maximum storable magnetic energy in Joules
 */
double calculate_core_maximum_magnetic_energy(json coreDataJson, json operatingPointJson);

/**
 * @brief Calculate saturation current for a magnetic component
 * @param magneticJson JSON Magnetic object (core + coil)
 * @param temperature Operating temperature in Celsius
 * @return Saturation current in Amperes
 */
double calculate_saturation_current(json magneticJson, double temperature);

/**
 * @brief Calculate core temperature from thermal resistance
 * @param coreJson JSON Core object with thermal resistance data
 * @param totalLosses Total power dissipation in Watts
 * @return Estimated core temperature in Celsius
 */
double calculate_temperature_from_core_thermal_resistance(json coreJson, double totalLosses);

// ============================================================================
// Gap and Reluctance Functions
// ============================================================================

/**
 * @brief Calculate magnetic reluctance of an air gap
 *
 * Models: ZHANG, MUEHLETHALER, PARTRIDGE, EFFECTIVE_AREA, STENGLEIN, BALAKRISHNAN, CLASSIC
 *
 * @param coreGapData JSON CoreGap object with gap geometry
 * @param modelNameString Reluctance model name
 * @return JSON AirGapReluctanceOutput with reluctance and fringing factor
 */
json calculate_gap_reluctance(json coreGapData, std::string modelNameString);

/**
 * @brief Get documentation for available gap reluctance models
 * @return JSON object with model information, errors, and links
 */
json get_gap_reluctance_model_information();

/**
 * @brief Calculate inductance from turns count and gap configuration
 *
 * Uses: L = N² / R_total
 *
 * @param coreData JSON object with core specification
 * @param coilData JSON object with coil specification (for turns)
 * @param operatingPointData JSON operating point for DC bias consideration
 * @param modelsData JSON dict with "reluctance" model selection
 * @return Magnetizing inductance in Henries
 */
double calculate_inductance_from_number_turns_and_gapping(json coreData, json coilData, json operatingPointData, json modelsData);

/**
 * @brief Calculate required turns from gap and target inductance
 *
 * Computes: N = sqrt(L * R_total)
 *
 * @param coreData JSON object with core specification
 * @param inputsData JSON Inputs with magnetizingInductance requirement
 * @param modelsData JSON dict with "reluctance" model selection
 * @return Required number of turns (may be non-integer)
 */
double calculate_number_turns_from_gapping_and_inductance(json coreData, json inputsData, json modelsData);

/**
 * @brief Calculate required gap from turns count and target inductance
 *
 * Iteratively solves for gap length to achieve target inductance.
 *
 * @param coreData JSON object with core specification
 * @param coilData JSON object with coil specification
 * @param inputsData JSON Inputs with magnetizingInductance requirement
 * @param gappingTypeJson Gap type ("SUBTRACTIVE", "ADDITIVE", "DISTRIBUTED")
 * @param decimals Precision in decimal places for gap length
 * @param modelsData JSON dict with "reluctance" model selection
 * @return JSON Core object with updated gapping configuration
 */
json calculate_gapping_from_number_turns_and_inductance(json coreData, json coilData, json inputsData, std::string gappingTypeJson, int decimals, json modelsData);

/**
 * @brief Register core-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_core_bindings(py::module& m);

} // namespace PyMKF
