/**
 * @file plotting.h
 * @brief SVG visualization functions for PyOpenMagnetics
 *
 * Provides functions for generating 2D cross-section visualizations of
 * magnetic components as SVG graphics.
 *
 * ## Plot Types
 * - plot_core(): Core cross-section only
 * - plot_magnetic(): Complete assembly (core + bobbin + coil)
 * - plot_magnetic_field(): H-field distribution with arrows
 * - plot_electric_field(): E-field (voltage gradient) distribution
 * - plot_wire(): Wire cross-section with strands (for litz)
 * - plot_bobbin(): Core with bobbin/coil former
 *
 * ## Output Format
 * All functions return JSON with:
 * - success: Boolean indicating operation status
 * - svg: SVG string content for rendering/saving
 * - error: Error message if success is false
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Plot complete magnetic assembly
 * result = pom.plot_magnetic(magnetic)
 * if result["success"]:
 *     with open("magnetic.svg", "w") as f:
 *         f.write(result["svg"])
 *
 * # Plot magnetic field distribution
 * result = pom.plot_magnetic_field(magnetic, operating_point)
 * if result["success"]:
 *     # Display or save SVG
 *     pass
 *
 * # Plot with custom output path
 * result = pom.plot_core(magnetic, "/path/to/output.svg")
 * @endcode
 *
 * @see settings.h for visualization configuration
 */

#pragma once
#include "common.h"

namespace PyMKF {

/**
 * @brief Generate 2D cross-section of magnetic core as SVG
 *
 * @param magneticJson JSON object with complete magnetic specification
 * @param outputPath Optional file path to save SVG (empty = temp directory)
 * @return JSON object with {success, svg, error}
 */
json plot_core(json magneticJson, std::string outputPath = "");

/**
 * @brief Generate complete magnetic assembly visualization as SVG
 *
 * Shows core, bobbin, and coil turns in cross-section view.
 *
 * @param magneticJson JSON object with complete magnetic specification
 * @param outputPath Optional file path to save SVG (empty = temp directory)
 * @return JSON object with {success, svg, error}
 */
json plot_magnetic(json magneticJson, std::string outputPath = "");

/**
 * @brief Plot magnetic field (H-field) distribution as SVG
 *
 * Generates visualization showing magnetic field strength across
 * the winding window with arrows indicating field direction.
 *
 * @param magneticJson JSON object with complete magnetic specification
 * @param operatingPointJson Operating conditions with excitation currents
 * @param outputPath Optional file path to save SVG (empty = temp directory)
 * @return JSON object with {success, svg, error}
 */
json plot_magnetic_field(json magneticJson, json operatingPointJson, std::string outputPath = "");

/**
 * @brief Plot electric field (E-field) distribution as SVG
 *
 * Generates visualization showing voltage gradient across
 * the winding window.
 *
 * @param magneticJson JSON object with complete magnetic specification
 * @param operatingPointJson Operating conditions with excitation voltages
 * @param outputPath Optional file path to save SVG (empty = temp directory)
 * @return JSON object with {success, svg, error}
 */
json plot_electric_field(json magneticJson, json operatingPointJson, std::string outputPath = "");

/**
 * @brief Generate wire cross-section visualization as SVG
 *
 * Shows wire structure including conductor, insulation layers,
 * and for litz wire, the individual strands arrangement.
 *
 * @param wireDataJson JSON object with wire specification
 * @param outputPath Optional file path to save SVG (empty = temp directory)
 * @return JSON object with {success, svg, error}
 */
json plot_wire(json wireDataJson, std::string outputPath = "");

/**
 * @brief Generate bobbin visualization with core as SVG
 *
 * @param magneticJson JSON object with complete magnetic specification
 * @param outputPath Optional file path to save SVG (empty = temp directory)
 * @return JSON object with {success, svg, error}
 */
json plot_bobbin(json magneticJson, std::string outputPath = "");

/**
 * @brief Register plotting-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_plotting_bindings(py::module& m);

} // namespace PyMKF
