#include "bobbin.h"

namespace PyMKF {

json get_bobbins() {
    auto bobbins = OpenMagnetics::get_bobbins();
    json result = json::array();
    for (auto elem : bobbins) {
        json aux;
        to_json(aux, elem);
        result.push_back(aux);
    }
    return result;
}

json get_bobbin_names() {
    auto bobbinNames = OpenMagnetics::get_bobbin_names();
    json result = json::array();
    for (auto elem : bobbinNames) {
        result.push_back(elem);
    }
    return result;
}

json find_bobbin_by_name(json bobbinName) {
    auto bobbinData = OpenMagnetics::find_bobbin_by_name(bobbinName);
    json result;
    to_json(result, bobbinData);
    return result;
}

json create_basic_bobbin(json coreDataJson, bool nullDimensions) {
    OpenMagnetics::Core core(coreDataJson, false, false, false);
    auto bobbin = OpenMagnetics::Bobbin::create_quick_bobbin(core, nullDimensions);

    json result;
    to_json(result, bobbin);
    return result;
}

json create_basic_bobbin_by_thickness(json coreDataJson, double thickness) {
    OpenMagnetics::Core core(coreDataJson, false, false, false);
    auto bobbin = OpenMagnetics::Bobbin::create_quick_bobbin(core, thickness);

    json result;
    to_json(result, bobbin);
    return result;
}

json calculate_bobbin_data(json magneticJson) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        auto optionalBobbin = magnetic.get_coil().get_bobbin();
        OpenMagnetics::Bobbin bobbin;

        if (std::holds_alternative<std::string>(optionalBobbin)) {
            auto bobbinJson = std::get<std::string>(optionalBobbin);
            if (bobbinJson == "Dummy") {
                bobbin = OpenMagnetics::Bobbin::create_quick_bobbin(magnetic.get_mutable_core());
            }
        }
        else {
            bobbin = OpenMagnetics::Bobbin(std::get<OpenMagnetics::Bobbin>(optionalBobbin));
            bobbin.process_data();
        }

        json result;
        to_json(result, bobbin);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json process_bobbin(json bobbinJson) {
    try {
        OpenMagnetics::Bobbin bobbin(bobbinJson);
        bobbin.process_data();

        json result;
        to_json(result, bobbin);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

bool check_if_fits(json bobbinJson, double dimension, bool isHorizontalOrRadial) {
    try {
        OpenMagnetics::Bobbin bobbin(bobbinJson);
        return bobbin.check_if_fits(dimension, isHorizontalOrRadial);
    }
    catch (const std::exception &exc) {
        std::cout << "Exception: " + std::string{exc.what()} << std::endl;
        return false;
    }
}

void register_bobbin_bindings(py::module& m) {
    m.def("get_bobbins", &get_bobbins, "Retrieve all available bobbins as JSON objects");
    m.def("get_bobbin_names", &get_bobbin_names, "Retrieve list of all bobbin names");
    m.def("find_bobbin_by_name", &find_bobbin_by_name, "Find bobbin data by name");
    m.def("create_basic_bobbin", &create_basic_bobbin, "Create a basic bobbin from core data");
    m.def("create_basic_bobbin_by_thickness", &create_basic_bobbin_by_thickness, "Create a basic bobbin with specified thickness");
    m.def("calculate_bobbin_data", &calculate_bobbin_data, "Calculate bobbin specifications");
    m.def("process_bobbin", &process_bobbin, "Process bobbin geometry");
    m.def("check_if_fits", &check_if_fits, "Check if winding fits in available space");
}

} // namespace PyMKF
