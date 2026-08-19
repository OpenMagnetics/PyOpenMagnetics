#pragma once

#include "common.h"

namespace PyMKF {

void load_databases(json databasesJson);
// MKF's parallel-region contract (ABT #815).
void load_all_databases();
void set_databases_frozen(bool frozen);
bool databases_frozen();
std::string read_databases(std::string path, bool addInternalData);
std::string load_mas(std::string key, json masJson, bool expand);
std::string load_magnetic(std::string key, json magneticJson, bool expand);
std::string load_magnetics(std::string keys, json magneticJsons, bool expand);
json read_mas(std::string key);

size_t load_core_materials(std::string fileToLoad);
size_t load_core_shapes(std::string fileToLoad);
size_t load_wires(std::string fileToLoad);
void clear_databases();
bool is_core_material_database_empty();
bool is_core_shape_database_empty();
bool is_wire_database_empty();

std::string load_magnetics_from_file(std::string path, bool expand);
json load_magnetics_from_file_report(std::string path, bool expand);
std::string clear_magnetic_cache();

// Additional database functions
json load_cores(json fileToLoadJson, bool includeToroids, bool useOnlyCoresInStock);
void clear_loaded_cores();
std::string load_magnetics_from_string(std::string jsonText);
json load_magnetics_from_string_report(std::string jsonText);

void register_database_bindings(py::module& m);

} // namespace PyMKF
