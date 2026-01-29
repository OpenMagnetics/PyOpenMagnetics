/**
 * @file losses.h
 * @brief Loss calculation functions for PyOpenMagnetics
 *
 * Provides comprehensive functions for calculating core losses and winding
 * losses in magnetic components. Supports multiple loss models and provides
 * detailed breakdown of loss components.
 *
 * ## Core Loss Models
 * - STEINMETZ: Original Steinmetz equation (sinusoidal only)
 * - IGSE: Improved Generalized Steinmetz Equation (arbitrary waveforms)
 * - MSE: Modified Steinmetz Equation
 * - BARG: Barg model for high-flux materials
 * - ROSHEN: Roshen model with DC bias support
 * - ALBACH: Albach frequency-domain model
 * - PROPRIETARY: Manufacturer-specific models
 *
 * ## Winding Loss Components
 * - Ohmic losses: DC I²R losses
 * - Skin effect: Current crowding at high frequency
 * - Proximity effect: Eddy currents from nearby conductors
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
 *
 * # Calculate core losses
 * core_loss = pom.calculate_core_losses(core, coil, inputs, models)
 * print(f"Core loss: {core_loss['coreLosses']:.2f} W")
 * print(f"B_peak: {core_loss['magneticFluxDensityPeak']*1000:.1f} mT")
 *
 * # Calculate winding losses
 * winding_loss = pom.calculate_winding_losses(magnetic, op, 85)
 * print(f"Winding loss: {winding_loss['windingLosses']:.2f} W")
 * @endcode
 *
 * @see core.h for core specifications
 * @see winding.h for coil specifications
 */

#pragma once

#include "common.h"

namespace PyMKF {

// ============================================================================
// Core Loss Functions
// ============================================================================

/**
 * @brief Calculate core losses for a magnetic component
 *
 * @param coreData JSON object with core specification
 * @param coilData JSON object with coil specification
 * @param inputsData JSON object with operating points
 * @param modelsData JSON dict specifying models:
 *                   {"coreLosses": "IGSE", "reluctance": "ZHANG", "coreTemperature": "..."}
 * @return JSON object with coreLosses, magneticFluxDensityPeak, temperature, etc.
 */
json calculate_core_losses(json coreData, json coilData, json inputsData, json modelsData);

/**
 * @brief Get documentation for available core loss models
 * @param material JSON object with material data for model availability
 * @return JSON object with model information, errors, and links
 */
json get_core_losses_model_information(json material);

/**
 * @brief Get documentation for core temperature models
 * @return JSON object with model information, errors, and links
 */
json get_core_temperature_model_information();

/**
 * @brief Fit Steinmetz coefficients from measured loss data
 *
 * @param dataJson JSON array of VolumetricLossesPoint measurements
 * @param rangesJson JSON array of [min_freq, max_freq] tuples
 * @return JSON array of SteinmetzCoreLossesMethodRangeDatum with k, alpha, beta
 */
json calculate_steinmetz_coefficients(json dataJson, json rangesJson);

/**
 * @brief Fit Steinmetz coefficients with error estimation
 *
 * @param dataJson JSON array of VolumetricLossesPoint measurements
 * @param rangesJson JSON array of frequency range tuples
 * @return JSON object with coefficientsPerRange and errorPerRange
 */
json calculate_steinmetz_coefficients_with_error(json dataJson, json rangesJson);

// ============================================================================
// Winding Loss Functions
// ============================================================================

/**
 * @brief Calculate total winding losses including all AC effects
 *
 * Computes DC ohmic, skin effect, and proximity effect losses.
 *
 * @param magneticJson JSON object with complete magnetic specification
 * @param operatingPointJson JSON object with excitation conditions
 * @param temperature Winding temperature in Celsius
 * @return JSON WindingLossesOutput with total and component losses
 */
json calculate_winding_losses(json magneticJson, json operatingPointJson, double temperature);

/**
 * @brief Calculate DC ohmic losses only
 * @param coilJson JSON object with coil specification
 * @param operatingPointJson JSON object with current excitation
 * @param temperature Wire temperature in Celsius
 * @return JSON WindingLossesOutput with ohmicLosses field
 */
json calculate_ohmic_losses(json coilJson, json operatingPointJson, double temperature);

/**
 * @brief Calculate magnetic field strength distribution in winding window
 *
 * Used for proximity effect calculations and field visualization.
 *
 * @param operatingPointJson JSON object with excitation conditions
 * @param magneticJson JSON object with magnetic specification
 * @return JSON WindingWindowMagneticStrengthFieldOutput with field data
 */
json calculate_magnetic_field_strength_field(json operatingPointJson, json magneticJson);

/**
 * @brief Calculate proximity effect losses from pre-computed field
 *
 * @param coilJson JSON object with coil specification
 * @param temperature Wire temperature in Celsius
 * @param windingLossesOutputJson Previous WindingLossesOutput for accumulation
 * @param windingWindowMagneticStrengthFieldOutputJson Field data from calculate_magnetic_field_strength_field()
 * @return Updated JSON WindingLossesOutput with proximity losses added
 */
json calculate_proximity_effect_losses(json coilJson, double temperature, json windingLossesOutputJson, json windingWindowMagneticStrengthFieldOutputJson);

/**
 * @brief Calculate skin effect losses in coil windings
 *
 * @param coilJson JSON object with coil specification
 * @param windingLossesOutputJson Previous WindingLossesOutput
 * @param temperature Wire temperature in Celsius
 * @return Updated JSON WindingLossesOutput with skin losses added
 */
json calculate_skin_effect_losses(json coilJson, json windingLossesOutputJson, double temperature);

/**
 * @brief Calculate skin effect losses per meter of wire
 *
 * @param wireJson JSON object with wire specification
 * @param currentJson JSON SignalDescriptor with current waveform
 * @param temperature Wire temperature in Celsius
 * @param currentDivider Current sharing factor (1.0 for single conductor)
 * @return JSON object with skin effect loss power per meter in W/m
 */
json calculate_skin_effect_losses_per_meter(json wireJson, json currentJson, double temperature, double currentDivider);

// ============================================================================
// DC Resistance and Per-Meter Loss Functions
// ============================================================================

/**
 * @brief Calculate DC resistance per meter of wire
 * @param wireJson JSON object with wire specification
 * @param temperature Wire temperature in Celsius
 * @return DC resistance in Ohms per meter
 */
double calculate_dc_resistance_per_meter(json wireJson, double temperature);

/**
 * @brief Calculate DC ohmic losses per meter of wire
 * @param wireJson JSON object with wire specification
 * @param currentJson JSON SignalDescriptor with current waveform
 * @param temperature Wire temperature in Celsius
 * @return DC power loss in Watts per meter
 */
double calculate_dc_losses_per_meter(json wireJson, json currentJson, double temperature);

/**
 * @brief Calculate skin effect AC resistance factor (Fr = Rac/Rdc)
 *
 * Fr = 1.0 means no skin effect; Fr > 1.0 indicates skin effect losses.
 *
 * @param wireJson JSON object with wire specification
 * @param currentJson JSON SignalDescriptor with current waveform
 * @param temperature Wire temperature in Celsius
 * @return AC factor (dimensionless ratio >= 1.0)
 */
double calculate_skin_ac_factor(json wireJson, json currentJson, double temperature);

/**
 * @brief Calculate AC skin effect losses per meter (excluding DC)
 * @param wireJson JSON object with wire specification
 * @param currentJson JSON SignalDescriptor with current waveform
 * @param temperature Wire temperature in Celsius
 * @return AC skin effect power loss in Watts per meter
 */
double calculate_skin_ac_losses_per_meter(json wireJson, json currentJson, double temperature);

/**
 * @brief Calculate total AC resistance per meter including skin effect
 *
 * Rac = Rdc * Fr where Fr is the skin effect AC factor.
 *
 * @param wireJson JSON object with wire specification
 * @param currentJson JSON SignalDescriptor with current waveform
 * @param temperature Wire temperature in Celsius
 * @return Total AC resistance in Ohms per meter
 */
double calculate_skin_ac_resistance_per_meter(json wireJson, json currentJson, double temperature);

/**
 * @brief Calculate effective current density in wire conductor
 *
 * Accounts for frequency-dependent current distribution.
 *
 * @param wireJson JSON object with wire specification
 * @param currentJson JSON SignalDescriptor with current waveform
 * @param temperature Wire temperature in Celsius
 * @return Effective current density in A/m²
 */
double calculate_effective_current_density(json wireJson, json currentJson, double temperature);

/**
 * @brief Calculate effective skin depth for a conductor material
 *
 * delta = sqrt(2*rho / (omega*mu))
 *
 * @param materialName Name of conductor material (e.g., "copper")
 * @param currentJson JSON SignalDescriptor with effective frequency
 * @param temperature Conductor temperature in Celsius
 * @return Skin depth in meters, or -1 if frequency not available
 */
double calculate_effective_skin_depth(std::string materialName, json currentJson, double temperature);

/**
 * @brief Register losses-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_losses_bindings(py::module& m);

} // namespace PyMKF
