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

// ABT #823: everything below exists because loading a 236-record NDJSON catalogue
// died with the bare string "bad optional access". Nothing named the file, the line,
// the part or the field, so the only way to find the offending record was to bisect
// the file by hand — and because records were written into the cache as they were
// read, the first 77 stayed loaded, so a caller that did not treat the return as
// fatal went on answering from a third of the catalogue with no sign anything was
// missing.
namespace {

// Best-effort part number for a record that failed to become a Magnetic. Read off the
// raw json, because whatever went wrong may have happened before the typed object
// existed.
std::string reference_hint(const json& recordJson) {
    if (recordJson.is_object()) {
        auto manufacturerInfo = recordJson.find("manufacturerInfo");
        if (manufacturerInfo != recordJson.end() && manufacturerInfo->is_object()) {
            auto reference = manufacturerInfo->find("reference");
            if (reference != manufacturerInfo->end() && reference->is_string()) {
                return reference->get<std::string>();
            }
        }
    }
    return "";
}

std::string locate(const std::string& source, size_t lineNumber, const std::string& reference) {
    std::string location = source + ":" + std::to_string(lineNumber);
    if (!reference.empty()) {
        location += " (part '" + reference + "')";
    }
    return location;
}

// The magnetics cache is keyed by manufacturerInfo.reference. This used to be two
// unguarded optional dereferences in a row, so a record that simply carried no
// manufacturer info produced its own anonymous "bad optional access".
std::string magnetic_cache_key(const OpenMagnetics::Magnetic& magnetic) {
    if (!magnetic.get_manufacturer_info()) {
        throw std::runtime_error("the record has no manufacturerInfo, and the magnetics cache is keyed by manufacturerInfo.reference");
    }
    if (!magnetic.get_manufacturer_info()->get_reference()) {
        throw std::runtime_error("the record has no manufacturerInfo.reference, which is the key the magnetics cache stores it under");
    }
    return magnetic.get_manufacturer_info()->get_reference().value();
}

std::pair<std::string, OpenMagnetics::Magnetic> read_magnetic_line(const std::string& line, bool expand) {
    json recordJson = json::parse(line);
    OpenMagnetics::Magnetic magnetic(recordJson);
    if (expand) {
        magnetic = OpenMagnetics::magnetic_autocomplete(magnetic);
    }
    std::string key = magnetic_cache_key(magnetic);
    return {std::move(key), std::move(magnetic)};
}

struct RejectedRecord {
    size_t lineNumber;
    std::string reference;
    std::string reason;
};

// Read the whole stream before touching the cache, so a strict load is all-or-nothing
// and a tolerant one is exact about what it dropped. Every failure is reported as
// "<source>:<line> (part 'X'): <what actually went wrong>".
std::vector<std::pair<std::string, OpenMagnetics::Magnetic>> stage_magnetics(std::istream& in,
                                                                             const std::string& source,
                                                                             bool expand,
                                                                             bool skipInvalid,
                                                                             std::vector<RejectedRecord>& rejected) {
    std::vector<std::pair<std::string, OpenMagnetics::Magnetic>> staged;
    std::string line;
    size_t lineNumber = 0;
    while (getline(in, line)) {
        lineNumber++;
        if (line.find_first_not_of(" \t\r\n") == std::string::npos) {
            continue;
        }
        try {
            staged.push_back(read_magnetic_line(line, expand));
        }
        catch (const std::exception& e) {
            std::string reference;
            try {
                reference = reference_hint(json::parse(line));
            }
            catch (const std::exception&) {
                // The line is not even json; the location alone identifies it.
            }
            if (!skipInvalid) {
                throw std::runtime_error(locate(source, lineNumber, reference) + ": " + e.what());
            }
            rejected.push_back({lineNumber, reference, e.what()});
        }
    }
    return staged;
}

size_t commit_magnetics(std::vector<std::pair<std::string, OpenMagnetics::Magnetic>>& staged) {
    for (auto& [key, magnetic] : staged) {
        OpenMagnetics::magneticsCache.load(key, std::move(magnetic));
    }
    return staged.size();
}

json rejection_report(size_t loaded, const std::vector<RejectedRecord>& rejected) {
    json report;
    report["loaded"] = loaded;
    report["cacheSize"] = OpenMagnetics::magneticsCache.size();
    report["rejected"] = json::array();
    for (const auto& record : rejected) {
        json entry;
        entry["line"] = record.lineNumber;
        entry["reference"] = record.reference;
        entry["reason"] = record.reason;
        report["rejected"].push_back(entry);
    }
    return report;
}

} // namespace

std::string load_magnetics_from_file(std::string path, bool expand) {
    std::ifstream in(path);
    if (!in) {
        // Used to fall through and return the cache size as if nothing had happened, so a
        // mistyped path was indistinguishable from a catalogue that loaded fine.
        throw std::runtime_error("load_magnetics_from_file: cannot open '" + path + "'");
    }
    std::vector<RejectedRecord> rejected;
    auto staged = stage_magnetics(in, path, expand, false, rejected);
    commit_magnetics(staged);
    return std::to_string(OpenMagnetics::magneticsCache.size());
}

json load_magnetics_from_file_report(std::string path, bool expand) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("load_magnetics_from_file_report: cannot open '" + path + "'");
    }
    std::vector<RejectedRecord> rejected;
    auto staged = stage_magnetics(in, path, expand, true, rejected);
    size_t loaded = commit_magnetics(staged);
    return rejection_report(loaded, rejected);
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
    std::vector<RejectedRecord> rejected;
    auto staged = stage_magnetics(in, "<string>", true, false, rejected);
    commit_magnetics(staged);
    return std::to_string(OpenMagnetics::magneticsCache.size());
}

json load_magnetics_from_string_report(std::string jsonText) {
    std::istringstream in(jsonText);
    std::vector<RejectedRecord> rejected;
    auto staged = stage_magnetics(in, "<string>", true, true, rejected);
    size_t loaded = commit_magnetics(staged);
    return rejection_report(loaded, rejected);
}

void register_database_bindings(py::module& m) {
    m.def("load_databases", &load_databases, "Load all databases from JSON",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_all_databases", &load_all_databases,
        R"pbdoc(
        Force-load every reference catalogue (cores, shapes, materials, wires,
        bobbins, insulation) that is still empty.

        Call this on one thread BEFORE using the engine from several threads:
        the catalogues lazy-load with an unsynchronised "if empty, load" check,
        so a first touch inside a parallel region is a data race. Pair it with
        set_databases_frozen(True).
        )pbdoc",
        py::call_guard<py::gil_scoped_release>());
    m.def("set_databases_frozen", &set_databases_frozen,
        R"pbdoc(
        Freeze (or unfreeze) the reference catalogues and the magnetics cache.

        While frozen, every mutating entry point — load_*, clear_*, and loading
        into the magnetics cache — throws instead of racing, which turns "a
        thread lazily reloaded a catalogue mid-flight" from undefined behaviour
        into a loud, diagnosable error. Freeze after load_all_databases() and
        after loading your part catalogue; unfreeze to change either.
        )pbdoc",
        py::arg("frozen"),
        py::call_guard<py::gil_scoped_release>());
    m.def("databases_frozen", &databases_frozen,
        "True when the catalogues are frozen for parallel use.",
        py::call_guard<py::gil_scoped_release>());
    m.def("read_databases", &read_databases, "Read databases from file path",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_mas", &load_mas, "Load a MAS (Magnetic Agnostic Structure) object",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_magnetic", &load_magnetic, "Load a magnetic component",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_magnetics", &load_magnetics, "Load multiple magnetic components",
        py::call_guard<py::gil_scoped_release>());
    m.def("read_mas", &read_mas, "Read a MAS object by key",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_core_materials", &load_core_materials, "Load core materials into database",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_core_shapes", &load_core_shapes, "Load core shapes into database",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_wires", &load_wires, "Load wires into database",
        py::call_guard<py::gil_scoped_release>());
    m.def("clear_databases", &clear_databases, "Clear all loaded databases",
        py::call_guard<py::gil_scoped_release>());
    m.def("is_core_material_database_empty", &is_core_material_database_empty, "Check if core material database is empty",
        py::call_guard<py::gil_scoped_release>());
    m.def("is_core_shape_database_empty", &is_core_shape_database_empty, "Check if core shape database is empty",
        py::call_guard<py::gil_scoped_release>());
    m.def("is_wire_database_empty", &is_wire_database_empty, "Check if wire database is empty",
        py::call_guard<py::gil_scoped_release>());
    m.def("load_magnetics_from_file", &load_magnetics_from_file,
        R"pbdoc(
        Load a catalogue of magnetics from an NDJSON file, one magnetic per line.

        All or nothing: the whole file is read and expanded before anything reaches
        the cache, so a rejected record never leaves a partly-loaded catalogue behind
        (ABT #823). The first record that cannot be loaded raises EngineError naming
        the file, the line number, the part reference and the underlying reason.
        Blank lines are skipped. Records are keyed by manufacturerInfo.reference, so
        a record without one is an error rather than an anonymous optional access.

        Use load_magnetics_from_file_report() instead when a partial catalogue is
        acceptable and you want the list of rejected records.

        Args:
            path: Path to the NDJSON file.
            expand: Autocomplete each magnetic (process the core, wind the coil).

        Returns:
            String with the number of magnetics in the cache after the load.
        )pbdoc",
        py::arg("path"), py::arg("expand"),
        py::call_guard<py::gil_scoped_release>());
    m.def("load_magnetics_from_file_report", &load_magnetics_from_file_report,
        R"pbdoc(
        Load an NDJSON catalogue, skipping records that cannot be loaded, and report them.

        The tolerant counterpart of load_magnetics_from_file (ABT #823): a bad record
        no longer aborts the batch, and the caller is told exactly which records were
        dropped and why instead of silently running on a truncated catalogue. A file
        that cannot be opened is still an error.

        Args:
            path: Path to the NDJSON file.
            expand: Autocomplete each magnetic (process the core, wind the coil).

        Returns:
            {'loaded': int,          # records from this file that were cached
             'cacheSize': int,       # magnetics in the cache after the load
             'rejected': [{'line': int, 'reference': str, 'reason': str}, ...]}
        )pbdoc",
        py::arg("path"), py::arg("expand"),
        py::call_guard<py::gil_scoped_release>());
    m.def("clear_magnetic_cache", &clear_magnetic_cache, "Clear cached magnetic calculations",
        py::call_guard<py::gil_scoped_release>());

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
        py::arg("file_to_load_json"), py::arg("include_toroids"), py::arg("use_only_cores_in_stock"),
        py::call_guard<py::gil_scoped_release>());

    m.def("clear_loaded_cores", &clear_loaded_cores,
        R"pbdoc(
        Clear all loaded cores from the database.
        )pbdoc",
        py::call_guard<py::gil_scoped_release>());

    m.def("load_magnetics_from_string", &load_magnetics_from_string,
        R"pbdoc(
        Load magnetic components from NDJSON text, one magnetic per line.

        Same contract as load_magnetics_from_file (ABT #823): all or nothing, and the
        first record that cannot be loaded raises EngineError naming the line number,
        the part reference and the reason. Magnetics are always autocompleted.

        Args:
            json_text: NDJSON string with one magnetic per line.

        Returns:
            String with the number of magnetics in the cache after the load.
        )pbdoc",
        py::arg("json_text"),
        py::call_guard<py::gil_scoped_release>());

    m.def("load_magnetics_from_string_report", &load_magnetics_from_string_report,
        R"pbdoc(
        Load NDJSON text, skipping records that cannot be loaded, and report them.

        The tolerant counterpart of load_magnetics_from_string (ABT #823).

        Args:
            json_text: NDJSON string with one magnetic per line.

        Returns:
            {'loaded': int, 'cacheSize': int,
             'rejected': [{'line': int, 'reference': str, 'reason': str}, ...]}
        )pbdoc",
        py::arg("json_text"),
        py::call_guard<py::gil_scoped_release>());

}

} // namespace PyMKF
