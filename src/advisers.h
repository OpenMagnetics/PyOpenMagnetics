/**
 * @file advisers.h
 * @brief Design recommendation functions for PyOpenMagnetics
 *
 * Provides intelligent design recommendation functions that analyze requirements
 * and return optimal core and magnetic component selections.
 *
 * ## Advisor Workflow
 * 1. Prepare inputs with design requirements and operating points
 * 2. Call process_inputs() to add harmonics data (CRITICAL)
 * 3. Call adviser functions to get ranked recommendations
 *
 * ## Core Modes
 * - AVAILABLE_CORES: Use only cores with stock availability
 * - STANDARD_CORES: Use all standard cores regardless of stock
 *
 * ## Optimization Weights
 * - COST: Minimize component cost
 * - EFFICIENCY: Maximize power efficiency
 * - DIMENSIONS: Minimize physical size
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Prepare inputs
 * inputs = {"designRequirements": {...}, "operatingPoints": [...]}
 * processed = pom.process_inputs(inputs)  # CRITICAL: must call first!
 *
 * # Get core recommendations
 * weights = {"COST": 1, "EFFICIENCY": 1, "DIMENSIONS": 0.5}
 * cores = pom.calculate_advised_cores(processed, weights, 10, "AVAILABLE_CORES")
 *
 * # Get complete magnetic designs
 * magnetics = pom.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
 * @endcode
 *
 * @warning Always call process_inputs() before using adviser functions!
 *
 * @see simulation.h for process_inputs() function
 * @see core.h for core query functions
 */

#pragma once

#include "common.h"

namespace PyMKF {

/**
 * @brief Get recommended cores for given design requirements
 *
 * Analyzes the input requirements and returns a ranked list of suitable cores
 * based on the specified weights for cost, efficiency, and dimensions.
 *
 * @param inputsJson JSON object with design requirements and operating points
 *                   (should be processed using process_inputs() first)
 * @param weightsJson JSON object with filter weights:
 *                    {"COST": 0-1, "EFFICIENCY": 0-1, "DIMENSIONS": 0-1}
 * @param maximumNumberResults Maximum number of core recommendations to return
 * @param coreModeJson Core selection mode: "AVAILABLE_CORES" or "STANDARD_CORES"
 * @return JSON array of recommended cores sorted by score (best first)
 */
json calculate_advised_cores(json inputsJson, json weightsJson, int maximumNumberResults, json coreModeJson);

/**
 * @brief Get recommended complete magnetic designs
 *
 * Performs full magnetic design optimization including core selection,
 * winding configuration, and all parameters. Returns complete Mas
 * (Magnetic Assembly Specification) objects ready for manufacturing.
 *
 * @param inputsJson JSON object with design requirements and operating points
 *                   (should be processed using process_inputs() first)
 * @param maximumNumberResults Maximum number of magnetic recommendations
 * @param coreModeJson Core selection mode: "AVAILABLE_CORES" or "STANDARD_CORES"
 * @return JSON array of complete Mas objects sorted by score (best first)
 */
json calculate_advised_magnetics(json inputsJson, int maximumNumberResults, json coreModeJson);

/**
 * @brief Get recommended magnetics from a custom component catalog
 *
 * Evaluates magnetic components from a user-provided catalog against
 * the design requirements and returns ranked recommendations.
 *
 * @param inputsJson JSON object with design requirements and operating points
 * @param catalogJson JSON array of Magnetic objects to evaluate
 * @param maximumNumberResults Maximum number of recommendations to return
 * @return JSON object with "data" array containing ranked results
 *         Each result has "mas" (Mas object) and "scoring" (float score)
 */
json calculate_advised_magnetics_from_catalog(json inputsJson, json catalogJson, int maximumNumberResults);

/**
 * @brief Get recommended magnetics from previously cached designs
 *
 * Evaluates cached magnetic designs against the requirements using
 * a custom filter flow for advanced filtering operations.
 *
 * @param inputsJson JSON object with design requirements and operating points
 * @param filterFlowJson JSON array of MagneticFilterOperation objects
 *                       defining the filtering pipeline
 * @param maximumNumberResults Maximum number of recommendations to return
 * @return JSON object with "data" array, or error string if cache is empty
 *
 * @note Cache must be populated using load_magnetics_from_file() first
 */
json calculate_advised_magnetics_from_cache(json inputsJson, json filterFlowJson, int maximumNumberResults);

/**
 * @brief Register adviser-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_adviser_bindings(py::module& m);

} // namespace PyMKF
