/**
 * @file database.h
 * @brief Database loading and caching functions for PyOpenMagnetics
 *
 * Provides functions to load and manage magnetic component databases including
 * core materials, core shapes, wires, bobbins, and insulation materials.
 * Also provides MAS object caching for efficient reuse of magnetic designs.
 *
 * ## Database Files (NDJSON format)
 * - core_materials.ndjson: Ferrite, iron powder, and other core materials
 * - core_shapes.ndjson: E, ETD, PQ, RM, toroidal, and other core shapes
 * - wires.ndjson: Round, litz, rectangular, and foil wire specifications
 * - bobbins.ndjson: Bobbin/coil former specifications
 * - insulation_materials.ndjson: Insulation tape and coating materials
 *
 * ## Usage Example
 * @code{.py}
 * import PyOpenMagnetics as pom
 *
 * # Load all databases
 * pom.load_core_materials()
 * pom.load_core_shapes()
 * pom.load_wires()
 *
 * # Check if loaded
 * if not pom.is_core_material_database_empty():
 *     print("Materials loaded")
 * @endcode
 *
 * @see core.h for material/shape query functions
 * @see wire.h for wire query functions
 */

#pragma once

#include "common.h"

namespace PyMKF {

/**
 * @brief Load all component databases from a JSON object
 * @param databasesJson JSON object containing all database data
 */
void load_databases(json databasesJson);

/**
 * @brief Read databases from NDJSON files in a directory
 * @param path Path to directory containing database files
 * @param addInternalData Whether to include internal computed data
 * @return "0" on success, error message on failure
 */
std::string read_databases(std::string path, bool addInternalData);

/**
 * @brief Load and cache a MAS (Magnetic Agnostic Structure) object
 * @param key Unique identifier for caching
 * @param masJson JSON representation of the MAS object
 * @param expand Whether to autocomplete missing fields
 * @return Number of cached objects as string, or error message
 */
std::string load_mas(std::string key, json masJson, bool expand);

/**
 * @brief Load and cache a Magnetic component
 * @param key Unique identifier for caching
 * @param magneticJson JSON representation of the Magnetic object
 * @param expand Whether to autocomplete missing fields
 * @return Number of cached objects as string, or error message
 */
std::string load_magnetic(std::string key, json magneticJson, bool expand);

/**
 * @brief Load and cache multiple Magnetic components
 * @param keys JSON array of unique identifiers
 * @param magneticJsons JSON array of Magnetic objects
 * @param expand Whether to autocomplete missing fields
 * @return Number of cached objects as string, or error message
 */
std::string load_magnetics(std::string keys, json magneticJsons, bool expand);

/**
 * @brief Retrieve a cached MAS object by key
 * @param key Unique identifier used when loading
 * @return JSON representation of the MAS object
 */
json read_mas(std::string key);

/**
 * @brief Load core materials database
 * @param fileToLoad Optional path to custom database file (empty for default)
 * @return Number of materials loaded
 */
size_t load_core_materials(std::string fileToLoad);

/**
 * @brief Load core shapes database
 * @param fileToLoad Optional path to custom database file (empty for default)
 * @return Number of shapes loaded
 */
size_t load_core_shapes(std::string fileToLoad);

/**
 * @brief Load wires database
 * @param fileToLoad Optional path to custom database file (empty for default)
 * @return Number of wires loaded
 */
size_t load_wires(std::string fileToLoad);

/**
 * @brief Clear all loaded databases from memory
 */
void clear_databases();

/**
 * @brief Check if core material database is empty
 * @return true if no materials are loaded
 */
bool is_core_material_database_empty();

/**
 * @brief Check if core shape database is empty
 * @return true if no shapes are loaded
 */
bool is_core_shape_database_empty();

/**
 * @brief Check if wire database is empty
 * @return true if no wires are loaded
 */
bool is_wire_database_empty();

/**
 * @brief Load magnetic components from an NDJSON file into cache
 * @param path Path to NDJSON file with magnetic components
 * @param expand Whether to autocomplete missing fields
 * @return Number of cached magnetics as string, or error message
 */
std::string load_magnetics_from_file(std::string path, bool expand);

/**
 * @brief Clear the magnetic component cache
 * @return Number of remaining cached items (should be 0)
 */
std::string clear_magnetic_cache();

/**
 * @brief Register database-related Python bindings
 * @param m Reference to the pybind11 module
 */
void register_database_bindings(py::module& m);

} // namespace PyMKF
