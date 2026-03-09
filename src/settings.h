/**
 * @file settings.h
 * @brief Configuration and defaults functions for PyOpenMagnetics
 *
 * Provides functions to query and modify library settings, retrieve
 * physical constants, and access default values for models and parameters.
 *
 * ## Settings Categories
 * - Coil winding options (margin tape, insulated wire, etc.)
 * - Visualization/painter settings (colors, resolution, scale)
 * - Magnetic field calculation options
 * - Core/material database options
 *
 * ## Key Constants
 * - vacuumPermeability: μ₀ = 4π × 10⁻⁷ H/m
 * - vacuumPermittivity: ε₀ = 8.854 × 10⁻¹² F/m
 * - residualGap: Minimum gap for machining tolerance
 * - minimumNonResidualGap: Minimum intentional gap
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Get physical constants
 * constants = pom.get_constants()
 * print(f"μ₀ = {constants['vacuumPermeability']}")
 *
 * # Get default model selections
 * defaults = pom.get_default_models()
 * print(f"Default core loss model: {defaults['coreLosses']}")
 *
 * # Modify settings
 * settings = pom.get_settings()
 * settings["useOnlyCoresInStock"] = True
 * settings["painterNumberPointsX"] = 100
 * pom.set_settings(settings)
 *
 * # Reset to defaults
 * pom.reset_settings()
 * @endcode
 *
 * @see plotting.h for visualization functions
 */

#pragma once

#include "common.h"

namespace PyMKF {

/**
 * @brief Get physical and system constants
 *
 * @return Python dict with constant names and values:
 *         - vacuumPermeability: μ₀ in H/m
 *         - vacuumPermittivity: ε₀ in F/m
 *         - residualGap: Residual gap in meters
 *         - minimumNonResidualGap: Minimum gap in meters
 *         - spacerProtudingPercentage: Spacer protrusion factor
 *         - coilPainterScale: Visualization scale factor
 *         - minimumDistributedFringingFactor: Min fringing
 *         - maximumDistributedFringingFactor: Max fringing
 *         - initialGapLengthForSearching: Initial gap search value
 *         - roshenMagneticFieldStrengthStep: Roshen model step
 *         - foilToSectionMargin: Foil winding margin
 *         - planarToSectionMargin: Planar winding margin
 */
py::dict get_constants();

/**
 * @brief Get default values for parameters and models
 *
 * @return Python dict with defaults:
 *         - coreLossesModelDefault: Default core loss model
 *         - coreTemperatureModelDefault: Default temperature model
 *         - reluctanceModelDefault: Default reluctance model
 *         - magneticFieldStrengthModelDefault: Default H-field model
 *         - maximumProportionMagneticFluxDensitySaturation: B_max factor
 *         - coreAdviserFrequencyReference: Adviser reference frequency
 *         - coreAdviserMagneticFluxDensityReference: Reference B-field
 *         - maximumCurrentDensity: Max current density limit
 *         - ambientTemperature: Default ambient temperature
 *         - measurementFrequency: Default measurement frequency
 *         - defaultInsulationMaterial: Default insulation type
 */
py::dict get_defaults();

/**
 * @brief Get current library settings
 *
 * @return JSON object with all configurable settings:
 *         - coilAllowMarginTape: Allow margin tape in windings
 *         - coilAllowInsulatedWire: Allow insulated wire
 *         - coilFillSectionsWithMarginTape: Fill with tape
 *         - coilWindEvenIfNotFit: Wind even if doesn't fit
 *         - coilDelimitAndCompact: Compact winding layout
 *         - coilTryRewind: Retry winding on failure
 *         - useOnlyCoresInStock: Limit to in-stock cores
 *         - painterNumberPointsX/Y: Field plot resolution
 *         - painterMode: Visualization mode
 *         - painterColorFerrite/Bobbin/Copper/etc.: Colors
 *         - magneticFieldNumberPointsX/Y: Field calc resolution
 *         - magneticFieldIncludeFringing: Include fringing effects
 */
json get_settings();

/**
 * @brief Update library settings
 *
 * @param settingsJson JSON object with settings to update
 *                     Only included keys will be modified
 *
 * @throws std::runtime_error if settings are invalid
 */
void set_settings(json settingsJson);

/**
 * @brief Reset all settings to default values
 *
 * Restores all library settings to their initial defaults.
 * Useful for ensuring consistent behavior between tests.
 */
void reset_settings();

/**
 * @brief Get names of default calculation models
 *
 * @return JSON object mapping model types to default names:
 *         - coreLosses: Default core loss model name
 *         - coreTemperature: Default temperature model name
 *         - reluctance: Default reluctance model name
 *         - magneticFieldStrength: Default H-field model name
 *         - magneticFieldStrengthFringingEffect: Default fringing model
 */
json get_default_models();

/**
 * @brief Register settings-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_settings_bindings(py::module& m);

} // namespace PyMKF
