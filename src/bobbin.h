/**
 * @file bobbin.h
 * @brief Bobbin/coil former management functions for PyOpenMagnetics
 *
 * Provides functions for querying bobbin databases, creating bobbins from
 * core specifications, and validating winding fit.
 *
 * ## Bobbin Types
 * - Standard bobbins: Pre-made formers matching common core shapes
 * - Custom bobbins: Created from core dimensions with specified wall thickness
 * - Quick bobbins: Auto-generated with default parameters
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Query bobbins
 * bobbins = pom.get_bobbin_names()
 * bobbin = pom.find_bobbin_by_name("ETD 49 bobbin")
 *
 * # Create bobbin from core
 * core = pom.calculate_core_data(core_spec, False)
 * bobbin = pom.create_basic_bobbin(core, False)
 *
 * # Or with specific wall thickness
 * bobbin = pom.create_basic_bobbin_by_thickness(core, 0.002)  # 2mm walls
 *
 * # Check if wire fits
 * fits = pom.check_if_fits(bobbin, wire_diameter, True)
 * @endcode
 *
 * @see core.h for core specifications
 * @see winding.h for placing wires in bobbins
 */

#pragma once

#include "common.h"

namespace PyMKF {

/**
 * @brief Get all available bobbins from the database
 * @return JSON array of Bobbin objects
 */
json get_bobbins();

/**
 * @brief Get list of all bobbin names
 * @return JSON array of bobbin name strings
 */
json get_bobbin_names();

/**
 * @brief Find complete bobbin data by name
 * @param bobbinName Bobbin name (e.g., "ETD 49 bobbin")
 * @return JSON Bobbin object with full specification
 */
json find_bobbin_by_name(json bobbinName);

/**
 * @brief Create a basic bobbin from core data
 *
 * Generates a bobbin that fits the core's winding window with
 * default wall thickness and margins.
 *
 * @param coreDataJson JSON object with core specification
 * @param nullDimensions If true, set dimensions to null for later calculation
 * @return JSON Bobbin object
 */
json create_basic_bobbin(json coreDataJson, bool nullDimensions);

/**
 * @brief Create a bobbin with specified wall thickness
 *
 * @param coreDataJson JSON object with core specification
 * @param thickness Wall thickness in meters
 * @return JSON Bobbin object with specified wall thickness
 */
json create_basic_bobbin_by_thickness(json coreDataJson, double thickness);

/**
 * @brief Calculate bobbin specifications from magnetic assembly
 *
 * Extracts and processes bobbin data from a complete magnetic object.
 * Creates a quick bobbin if the magnetic has a "Dummy" bobbin reference.
 *
 * @param magneticJson JSON Magnetic object containing coil with bobbin
 * @return JSON Bobbin object with computed properties
 */
json calculate_bobbin_data(json magneticJson);

/**
 * @brief Process bobbin geometry and calculate derived parameters
 * @param bobbinJson JSON Bobbin object
 * @return JSON Bobbin object with processed geometry
 */
json process_bobbin(json bobbinJson);

/**
 * @brief Check if a dimension fits in the bobbin's winding window
 *
 * Validates whether a wire or other element of given dimension
 * will fit in the available winding space.
 *
 * @param bobbinJson JSON Bobbin object
 * @param dimension Dimension to check in meters
 * @param isHorizontalOrRadial True for horizontal/radial, false for vertical/axial
 * @return true if the dimension fits, false otherwise
 */
bool check_if_fits(json bobbinJson, double dimension, bool isHorizontalOrRadial);

/**
 * @brief Register bobbin-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_bobbin_bindings(py::module& m);

} // namespace PyMKF
