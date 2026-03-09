/**
 * @file simulation.h
 * @brief Simulation and matrix calculation functions for PyOpenMagnetics
 *
 * Provides functions for complete magnetic simulation, circuit export,
 * input processing, and electrical matrix calculations.
 *
 * ## Key Functions
 * - simulate(): Full electromagnetic simulation
 * - process_inputs(): CRITICAL - must call before using advisers
 * - calculate_inductance_matrix(): Self and mutual inductances
 * - calculate_resistance_matrix(): AC resistance matrix
 * - calculate_stray_capacitance(): Parasitic capacitances
 *
 * ## Circuit Export
 * Supports export to SPICE-compatible subcircuit format for circuit simulation.
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # CRITICAL: Always process inputs first!
 * inputs = {"designRequirements": {...}, "operatingPoints": [...]}
 * processed = pom.process_inputs(inputs)
 *
 * # Run full simulation
 * models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
 * result = pom.simulate(processed, magnetic, models)
 *
 * # Get inductance matrix
 * L_matrix = pom.calculate_inductance_matrix(magnetic, 100000, models)
 *
 * # Export for circuit simulation
 * subcircuit = pom.export_magnetic_as_subcircuit(magnetic)
 * @endcode
 *
 * @warning Always call process_inputs() before adviser functions!
 *
 * @see advisers.h for design recommendation functions
 * @see losses.h for loss calculations
 */

#pragma once

#include "common.h"

namespace PyMKF {

// ============================================================================
// Simulation Functions
// ============================================================================

/**
 * @brief Run complete magnetic simulation
 *
 * Performs full electromagnetic simulation including inductance calculation,
 * field distribution, and performance metrics.
 *
 * @param inputsJson JSON object with operating points and conditions
 * @param magneticJson JSON object with magnetic component specification
 * @param modelsData JSON object specifying models to use
 * @return JSON Mas object with simulation results in outputs
 */
json simulate(json inputsJson, json magneticJson, json modelsData);

// ============================================================================
// Export Functions
// ============================================================================

/**
 * @brief Export magnetic as SPICE-compatible subcircuit
 *
 * Generates subcircuit netlist representation for circuit simulation
 * tools like LTspice, ngspice, etc.
 *
 * @param magneticJson JSON object with magnetic component specification
 * @return JSON string containing the subcircuit definition
 */
ordered_json export_magnetic_as_subcircuit(json magneticJson);

// ============================================================================
// Autocomplete Functions
// ============================================================================

/**
 * @brief Autocomplete a partial Mas structure
 *
 * Fills in missing fields and calculates derived values.
 *
 * @param masJson Partial Mas JSON object to complete
 * @param configuration Configuration options for autocomplete
 * @return Complete Mas JSON object with all fields populated
 */
json mas_autocomplete(json masJson, json configuration);

/**
 * @brief Autocomplete a partial Magnetic specification
 *
 * Fills in missing fields and calculates derived values for core and coil.
 *
 * @param magneticJson Partial Magnetic JSON object to complete
 * @param configuration Configuration options for autocomplete
 * @return Complete Magnetic JSON object with all fields populated
 */
json magnetic_autocomplete(json magneticJson, json configuration);

// ============================================================================
// Input Processing Functions
// ============================================================================

/**
 * @brief Process raw input data and calculate derived quantities
 *
 * @warning CRITICAL: Must call this before using adviser functions!
 *
 * Calculates:
 * - Harmonic content of waveforms (FFT analysis)
 * - Processed waveform data (RMS, peak, offset)
 * - Reconstructs waveforms from processed data if needed
 *
 * @param inputsJson Raw input JSON object with operating points
 * @return Processed inputs JSON with harmonics and processed data
 */
json process_inputs(json inputsJson);

/**
 * @brief Extract operating point from circuit simulation data
 *
 * @param fileJson JSON object with simulation file data
 * @param numberWindings Number of windings in the magnetic
 * @param frequency Operating frequency in Hz
 * @param desiredMagnetizingInductance Target inductance value
 * @param mapColumnNamesJson Mapping of column names to signals
 * @return JSON OperatingPoint object
 */
json extract_operating_point(json fileJson, size_t numberWindings, double frequency, double desiredMagnetizingInductance, json mapColumnNamesJson);

/**
 * @brief Extract column name mapping from circuit simulation file
 *
 * @param fileJson JSON object with simulation file data
 * @param numberWindings Number of windings to map
 * @param frequency Operating frequency for signal identification
 * @return JSON array mapping signal types to column names
 */
json extract_map_column_names(json fileJson, size_t numberWindings, double frequency);

/**
 * @brief Extract all column names from a circuit simulation file
 * @param fileJson JSON object with simulation file data
 * @return JSON array of column name strings
 */
json extract_column_names(json fileJson);

// ============================================================================
// Inductance Functions
// ============================================================================

/**
 * @brief Calculate complete inductance matrix
 *
 * Computes self inductances (diagonal) and mutual inductances (off-diagonal)
 * at the specified frequency.
 *
 * @param magneticJson JSON object with magnetic component specification
 * @param frequency Operating frequency in Hz
 * @param modelsData JSON object specifying reluctance model
 * @return JSON object with inductance matrix
 */
json calculate_inductance_matrix(json magneticJson, double frequency, json modelsData);

/**
 * @brief Calculate leakage inductance between windings
 *
 * @param magneticJson JSON object with magnetic component specification
 * @param frequency Operating frequency in Hz
 * @param sourceIndex Index of the source winding (0-based)
 * @return JSON object with leakage inductance values
 */
json calculate_leakage_inductance(json magneticJson, double frequency, size_t sourceIndex);

// ============================================================================
// Resistance Functions
// ============================================================================

/**
 * @brief Calculate DC resistance for each winding
 *
 * @param coilJson JSON object with coil specification
 * @param temperature Temperature in Celsius
 * @return JSON array with DC resistance per winding in Ohms
 */
json calculate_dc_resistance_per_winding(json coilJson, double temperature);

/**
 * @brief Calculate frequency-dependent resistance matrix
 *
 * Uses the Spreen (1990) method with inductance ratio scaling.
 *
 * @param magneticJson JSON object with magnetic component specification
 * @param temperature Temperature in Celsius
 * @param frequency Operating frequency in Hz
 * @return JSON object with resistance matrix
 */
json calculate_resistance_matrix(json magneticJson, double temperature, double frequency);

// ============================================================================
// Capacitance Functions
// ============================================================================

/**
 * @brief Calculate stray capacitance for a coil
 *
 * Computes turn-to-turn and winding-to-winding capacitances.
 *
 * @param coilJson JSON object with coil specification
 * @param operatingPointJson JSON object with operating conditions
 * @param modelsData JSON object specifying capacitance model
 * @return JSON object with capacitance values and Maxwell matrix
 */
json calculate_stray_capacitance(json coilJson, json operatingPointJson, json modelsData);

/**
 * @brief Calculate Maxwell capacitance matrix
 *
 * Converts inter-winding capacitance values to Maxwell format.
 *
 * @param coilJson JSON object with coil specification
 * @param capacitanceAmongWindingsJson JSON object with capacitance between windings
 * @return JSON array containing the Maxwell capacitance matrix
 */
json calculate_maxwell_capacitance_matrix(json coilJson, json capacitanceAmongWindingsJson);

/**
 * @brief Register simulation-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_simulation_bindings(py::module& m);

} // namespace PyMKF
