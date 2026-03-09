/**
 * @file utils.h
 * @brief Utility functions for PyOpenMagnetics
 *
 * Provides helper functions for signal processing, waveform analysis,
 * power calculations, and data type conversions.
 *
 * ## Waveform Processing
 * - calculate_basic_processed_data(): Extract RMS, peak, offset
 * - calculate_harmonics(): FFT analysis for harmonic content
 * - calculate_sampled_waveform(): Uniform resampling
 *
 * ## Power Calculations
 * - calculate_instantaneous_power(): Point-by-point V×I
 * - calculate_rms_power(): Vrms × Irms
 *
 * ## Transformer Reflections
 * - calculate_reflected_secondary(): Primary to secondary side
 * - calculate_reflected_primary(): Secondary to primary side
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Process a waveform
 * waveform = {"data": [0, 1, 0, -1, 0], "time": [0, 0.25, 0.5, 0.75, 1.0]}
 * processed = pom.calculate_basic_processed_data(waveform)
 * print(f"RMS: {processed['rms']}, Peak: {processed['peak']}")
 *
 * # Calculate harmonics
 * harmonics = pom.calculate_harmonics(waveform, 100000)  # 100 kHz fundamental
 *
 * # Reflect excitation through transformer
 * secondary = pom.calculate_reflected_secondary(primary_excitation, 10)  # 10:1 ratio
 * @endcode
 *
 * @see simulation.h for process_inputs() which uses these utilities
 */

#pragma once
#include "common.h"

namespace PyMKF {

// ============================================================================
// Dimension Utilities
// ============================================================================

/**
 * @brief Resolve a dimension specification with tolerances
 *
 * Extracts a single nominal value from dimension data that may contain
 * nominal, minimum, and maximum values.
 *
 * @param dimensionWithToleranceJson JSON DimensionWithTolerance object
 * @return Resolved dimension value as double
 */
double resolve_dimension_with_tolerance(json dimensionWithToleranceJson);

// ============================================================================
// Waveform Processing Functions
// ============================================================================

/**
 * @brief Calculate basic processed data from a waveform
 *
 * Extracts peak-to-peak, RMS, offset, peak, and other basic metrics.
 *
 * @param waveformJson JSON Waveform object with data and time arrays
 * @return JSON Processed object with computed characteristics
 */
json calculate_basic_processed_data(json waveformJson);

/**
 * @brief Calculate harmonic content of a waveform (FFT analysis)
 *
 * @param waveformJson JSON Waveform object with data and time arrays
 * @param frequency Fundamental frequency in Hz
 * @return JSON Harmonics object with amplitudes and frequencies
 */
json calculate_harmonics(json waveformJson, double frequency);

/**
 * @brief Resample a waveform at uniform intervals
 *
 * Interpolates waveform data to create uniformly sampled points
 * suitable for FFT analysis.
 *
 * @param waveformJson JSON Waveform object
 * @param frequency Frequency for determining sample period
 * @return JSON Waveform object with uniform sampling
 */
json calculate_sampled_waveform(json waveformJson, double frequency);

/**
 * @brief Calculate complete processed data from a signal descriptor
 *
 * Computes RMS, peak, offset, effective frequency, and other metrics.
 *
 * @param signalDescriptorJson JSON SignalDescriptor object
 * @param sampledWaveformJson JSON Waveform with uniform samples
 * @param includeDcComponent Whether to include DC in calculations
 * @return JSON Processed object with complete analysis
 */
json calculate_processed_data(json signalDescriptorJson, json sampledWaveformJson, bool includeDcComponent);

// ============================================================================
// Power Calculation Functions
// ============================================================================

/**
 * @brief Calculate instantaneous power from excitation
 *
 * Computes point-by-point product of voltage and current waveforms.
 *
 * @param excitationJson JSON OperatingPointExcitation with voltage and current
 * @return Instantaneous power value in Watts
 */
double calculate_instantaneous_power(json excitationJson);

/**
 * @brief Calculate RMS (apparent) power from excitation
 *
 * Computes Vrms × Irms product.
 *
 * @param excitationJson JSON OperatingPointExcitation with voltage and current
 * @return RMS power value in Watts (apparent power)
 */
double calculate_rms_power(json excitationJson);

// ============================================================================
// Transformer Reflection Functions
// ============================================================================

/**
 * @brief Calculate reflected secondary winding excitation
 *
 * Transforms primary winding excitation to secondary side using turns ratio.
 * V_secondary = V_primary / n
 * I_secondary = I_primary × n
 *
 * @param primaryExcitationJson JSON OperatingPointExcitation for primary
 * @param turnRatio Primary to secondary turns ratio (Np/Ns)
 * @return JSON OperatingPointExcitation for secondary side
 */
json calculate_reflected_secondary(json primaryExcitationJson, double turnRatio);

/**
 * @brief Calculate reflected primary winding excitation
 *
 * Transforms secondary winding excitation to primary side using turns ratio.
 * V_primary = V_secondary × n
 * I_primary = I_secondary / n
 *
 * @param secondaryExcitationJson JSON OperatingPointExcitation for secondary
 * @param turnRatio Primary to secondary turns ratio (Np/Ns)
 * @return JSON OperatingPointExcitation for primary side
 */
json calculate_reflected_primary(json secondaryExcitationJson, double turnRatio);

// ============================================================================
// Array Conversion Functions
// ============================================================================

/**
 * @brief Convert C++ vector of vectors to Python nested list
 * @param arrayOfArrays C++ std::vector<std::vector<double>>
 * @return Python list of lists
 */
py::list list_of_list_to_python_list(std::vector<std::vector<double>> arrayOfArrays);

/**
 * @brief Convert Python list to C++ vector
 * @param pythonList Python list of numeric values
 * @return C++ std::vector<double>
 */
std::vector<double> python_list_to_vector(py::list pythonList);

/**
 * @brief Register utility-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_utils_bindings(py::module& m);

} // namespace PyMKF
