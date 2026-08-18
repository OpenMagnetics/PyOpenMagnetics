#include "database.h"
#include <sstream>

namespace PyMKF {

// Definition of the masDatabase variable (declared as extern in common.h)
std::map<std::string, OpenMagnetics::Mas> masDatabase;

void load_databases(json databasesJson) {
    OpenMagnetics::load_databases(databasesJson, true);
}

// ABT #815: MKF's thread-safety contract (see the THREAD-SAFETY CONTRACT note
// in MKF's support/Utils.h) was unreachable from Python — a host could not
// force-load the catalogues nor freeze them, so it had no way to use the
// engine from more than one thread and had to serialise every call.
void load_all_databases() {
    OpenMagnetics::load_all_databases();
}

void set_databases_frozen(bool frozen) {
    OpenMagnetics::set_databases_frozen(frozen);
}

bool databases_frozen() {
    return OpenMagnetics::databases_frozen();
}

std::string read_databases(std::string path, bool addInternalData) {
    auto masPath = std::filesystem::path{path};
    json data;
    std::string line;
    {
        data["coreMaterials"] = json();
        std::ifstream coreMaterials(masPath.append("core_materials.ndjson"));
        while (getline (coreMaterials, line)) {
            json jf = json::parse(line);
            data["coreMaterials"][jf["name"]] = jf;
        }
    }
    {
        data["coreShapes"] = json();
        std::ifstream coreMaterials(masPath.append("core_shapes.ndjson"));
        while (getline (coreMaterials, line)) {
            json jf = json::parse(line);
            data["coreShapes"][jf["name"]] = jf;
        }
    }
    {
        data["wires"] = json();
        std::ifstream coreMaterials(masPath.append("wires.ndjson"));
        while (getline (coreMaterials, line)) {
            json jf = json::parse(line);
            data["wires"][jf["name"]] = jf;
        }
    }
    {
        data["bobbins"] = json();
        std::ifstream coreMaterials(masPath.append("bobbins.ndjson"));
        while (getline (coreMaterials, line)) {
            json jf = json::parse(line);
            data["bobbins"][jf["name"]] = jf;
        }
    }
    {
        data["insulationMaterials"] = json();
        std::ifstream coreMaterials(masPath.append("insulation_materials.ndjson"));
        while (getline (coreMaterials, line)) {
            json jf = json::parse(line);
            data["insulationMaterials"][jf["name"]] = jf;
        }
    }
    {
        data["wireMaterials"] = json();
        std::ifstream coreMaterials(masPath.append("wire_materials.ndjson"));
        while (getline (coreMaterials, line)) {
            json jf = json::parse(line);
            data["wireMaterials"][jf["name"]] = jf;
        }
    }
    OpenMagnetics::load_databases(data, true, addInternalData);
    return "0";
}

std::string load_mas(std::string key, json masJson, bool expand) {
    OpenMagnetics::Mas mas(masJson);
    if (expand) {
        mas.set_magnetic(OpenMagnetics::magnetic_autocomplete(mas.get_mutable_magnetic()));
        mas.set_inputs(OpenMagnetics::inputs_autocomplete(mas.get_mutable_inputs(), mas.get_mutable_magnetic()));
    }
    masDatabase[key] = mas;
    return std::to_string(masDatabase.size());
}

std::string load_magnetic(std::string key, json magneticJson, bool expand) {
    OpenMagnetics::Magnetic magnetic(magneticJson);
    if (expand) {
        magnetic = OpenMagnetics::magnetic_autocomplete(magnetic);
    }
    OpenMagnetics::Mas mas;
    mas.set_magnetic(magnetic);
    masDatabase[key] = mas;
    return std::to_string(masDatabase.size());
}

std::string load_magnetics(std::string keys, json magneticJsons, bool expand) {
    json keysJson = json::parse(keys);
    for (size_t magneticIndex = 0; magneticIndex < magneticJsons.size(); magneticIndex++) {
        OpenMagnetics::Magnetic magnetic(magneticJsons[magneticIndex]);
        if (expand) {
            magnetic = OpenMagnetics::magnetic_autocomplete(magnetic);
        }
        OpenMagnetics::Mas mas;
        mas.set_magnetic(magnetic);
        masDatabase[to_string(keysJson[magneticIndex])] = mas;
    }
    return std::to_string(masDatabase.size());
}

json read_mas(std::string key) {
    json result;
    to_json(result, masDatabase[key]);
    return result;
}

size_t load_core_materials(std::string fileToLoad) {
    if (fileToLoad != "") {
        OpenMagnetics::load_core_materials(fileToLoad);
    }
    else {
        OpenMagnetics::load_core_materials();
    }
    return OpenMagnetics::coreMaterialDatabase.size();
}

size_t load_core_shapes(std::string fileToLoad) {
    if (fileToLoad != "") {
        OpenMagnetics::load_core_shapes(true, fileToLoad);
    }
    else {
        OpenMagnetics::load_core_shapes();
    }
    return OpenMagnetics::coreShapeDatabase.size();
}

size_t load_wires(std::string fileToLoad) {
    if (fileToLoad != "") {
        OpenMagnetics::load_wires(fileToLoad);
    }
    else {
        OpenMagnetics::load_wires();
    }
    return OpenMagnetics::wireDatabase.size();
}

void clear_databases() {
    OpenMagnetics::clear_databases();
}

bool is_core_material_database_empty() {
    return OpenMagnetics::coreMaterialDatabase.size() == 0;
}

bool is_core_shape_database_empty() {
    return OpenMagnetics::coreShapeDatabase.size() == 0;
}

bool is_wire_database_empty() {
    return OpenMagnetics::wireDatabase.size() == 0;
}

std::string load_magnetics_from_file(std::string path, bool expand) {
    std::ifstream in(path);
    if (in) {
        std::string line;
        while (getline(in, line)) {
            json jf = json::parse(line);
            OpenMagnetics::Magnetic magnetic(jf);
            if (expand) {
                magnetic = OpenMagnetics::magnetic_autocomplete(magnetic);
            }
            std::string key = magnetic.get_manufacturer_info()->get_reference().value();
            OpenMagnetics::magneticsCache.load(key, magnetic);
        }
    }
    return std::to_string(OpenMagnetics::magneticsCache.size());
}

std::string clear_magnetic_cache() {
    OpenMagnetics::magneticsCache.clear();
    return std::to_string(OpenMagnetics::magneticsCache.size());
}

json load_cores(json fileToLoadJson, bool includeToroids, bool useOnlyCoresInStock) {
    OpenMagnetics::settings.set_use_toroidal_cores(includeToroids);
    OpenMagnetics::settings.set_use_only_cores_in_stock(useOnlyCoresInStock);

    if (!fileToLoadJson.is_null() && fileToLoadJson.is_string()) {
        std::string fileToLoad = fileToLoadJson;
        OpenMagnetics::load_cores(fileToLoad);
    }
    else {
        OpenMagnetics::load_cores();
    }

    json result;
    result["count"] = OpenMagnetics::coreDatabase.size();
    return result;
}

void clear_loaded_cores() {
    OpenMagnetics::clear_loaded_cores();
}

std::string load_magnetics_from_string(std::string jsonText) {
    std::istringstream in(jsonText);
    std::string line;
    while (getline(in, line)) {
        if (line.empty()) continue;
        json jf = json::parse(line);
        OpenMagnetics::Magnetic magnetic(jf);
        magnetic = OpenMagnetics::magnetic_autocomplete(magnetic);
        std::string key = magnetic.get_manufacturer_info()->get_reference().value();
        OpenMagnetics::magneticsCache.load(key, magnetic);
    }
    return std::to_string(OpenMagnetics::magneticsCache.size());
}

void register_database_bindings(py::module& m) {
    m.def("load_databases", &load_databases, "Load all databases from JSON");
    m.def("load_all_databases", &load_all_databases,
        R"pbdoc(
        Force-load every reference catalogue (cores, shapes, materials, wires,
        bobbins, insulation) that is still empty.

        Call this on one thread BEFORE using the engine from several threads:
        the catalogues lazy-load with an unsynchronised "if empty, load" check,
        so a first touch inside a parallel region is a data race. Pair it with
        set_databases_frozen(True).
        )pbdoc");
    m.def("set_databases_frozen", &set_databases_frozen,
        R"pbdoc(
        Freeze (or unfreeze) the reference catalogues and the magnetics cache.

        While frozen, every mutating entry point — load_*, clear_*, and loading
        into the magnetics cache — throws instead of racing, which turns "a
        thread lazily reloaded a catalogue mid-flight" from undefined behaviour
        into a loud, diagnosable error. Freeze after load_all_databases() and
        after loading your part catalogue; unfreeze to change either.
        )pbdoc",
        py::arg("frozen"));
    m.def("databases_frozen", &databases_frozen,
        "True when the catalogues are frozen for parallel use.");
    m.def("read_databases", &read_databases, "Read databases from file path");
    m.def("load_mas", &load_mas, "Load a MAS (Magnetic Agnostic Structure) object");
    m.def("load_magnetic", &load_magnetic, "Load a magnetic component");
    m.def("load_magnetics", &load_magnetics, "Load multiple magnetic components");
    m.def("read_mas", &read_mas, "Read a MAS object by key");
    m.def("load_core_materials", &load_core_materials, "Load core materials into database");
    m.def("load_core_shapes", &load_core_shapes, "Load core shapes into database");
    m.def("load_wires", &load_wires, "Load wires into database");
    m.def("clear_databases", &clear_databases, "Clear all loaded databases");
    m.def("is_core_material_database_empty", &is_core_material_database_empty, "Check if core material database is empty");
    m.def("is_core_shape_database_empty", &is_core_shape_database_empty, "Check if core shape database is empty");
    m.def("is_wire_database_empty", &is_wire_database_empty, "Check if wire database is empty");
    m.def("load_magnetics_from_file", &load_magnetics_from_file, "Load magnetic components from file",
        py::call_guard<py::gil_scoped_release>());
    m.def("clear_magnetic_cache", &clear_magnetic_cache, "Clear cached magnetic calculations");

    m.def("load_cores", &load_cores,
        R"pbdoc(
        Load cores from file or defaults.

        Args:
            file_to_load_json: JSON string with file path, or null for defaults.
            include_toroids: Whether to include toroidal cores.
            use_only_cores_in_stock: Whether to limit to in-stock cores.

        Returns:
            JSON object with count of loaded cores.
        )pbdoc",
        py::arg("file_to_load_json"), py::arg("include_toroids"), py::arg("use_only_cores_in_stock"));

    m.def("clear_loaded_cores", &clear_loaded_cores,
        R"pbdoc(
        Clear all loaded cores from the database.
        )pbdoc");

    m.def("load_magnetics_from_string", &load_magnetics_from_string,
        R"pbdoc(
        Load magnetic components from NDJSON text.

        Args:
            json_text: NDJSON string with one magnetic per line.

        Returns:
            String with count of loaded magnetics.
        )pbdoc",
        py::arg("json_text"),
        py::call_guard<py::gil_scoped_release>());

}

} // namespace PyMKF
