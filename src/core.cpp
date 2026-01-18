#include "core.h"

namespace PyMKF {

json get_core_materials() {
    try {
        auto materials = OpenMagnetics::get_materials(std::nullopt);
        json result = json::array();
        for (auto elem: materials) {
            json aux;
            to_json(aux, elem);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

double get_material_permeability(json materialName, double temperature, double magneticFieldDcBias, double frequency) {
    try {
        auto materialData = OpenMagnetics::find_core_material_by_name(materialName);
        OpenMagnetics::InitialPermeability initialPermeability;
        return initialPermeability.get_initial_permeability(materialData, temperature, magneticFieldDcBias, frequency);
    }
    catch (const std::exception &exc) {
        throw std::runtime_error("Exception: " + std::string{exc.what()});
    }
}

double get_material_resistivity(json materialName, double temperature) {
    try {
        auto materialData = OpenMagnetics::find_core_material_by_name(materialName);
        auto resistivityModel = OpenMagnetics::ResistivityModel::factory(OpenMagnetics::ResistivityModels::CORE_MATERIAL);
        return (*resistivityModel).get_resistivity(materialData, temperature);
    }
    catch (const std::exception &exc) {
        throw std::runtime_error("Exception: " + std::string{exc.what()});
    }
}

json get_core_material_steinmetz_coefficients(json materialName, double frequency) {
    try {
        auto steinmetzCoreLossesMethodRangeDatum = OpenMagnetics::CoreLossesModel::get_steinmetz_coefficients(materialName, frequency);
        json result;
        to_json(result, steinmetzCoreLossesMethodRangeDatum);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_core_shapes() {
    try {
        auto shapes = OpenMagnetics::get_shapes(true);
        json result = json::array();
        for (auto elem : shapes) {
            json aux;
            to_json(aux, elem);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_core_shape_families() {
    try {
        auto shapes = OpenMagnetics::get_shapes(false);
        std::vector<CoreShapeFamily> families;
        json result = json::array();
        for (auto elem : shapes) {
            auto family = elem.get_family();
            if (std::find(families.begin(), families.end(), family) == families.end()) {
                families.push_back(family);
                json aux;
                to_json(aux, family);
                result.push_back(aux);
            }
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_core_material_names() {
    try {
        auto materialNames = OpenMagnetics::get_core_material_names(std::nullopt);
        json result = json::array();
        for (auto elem : materialNames) {
            result.push_back(elem);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_core_material_names_by_manufacturer(std::string manufacturerName) {
    try {
        auto materialNames = OpenMagnetics::get_core_material_names(manufacturerName);
        json result = json::array();
        for (auto elem : materialNames) {
            result.push_back(elem);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json get_core_shape_names(bool includeToroidal) {
    try {
        OpenMagnetics::settings.set_use_toroidal_cores(includeToroidal);
        auto shapeNames = OpenMagnetics::get_core_shape_names();
        json result = json::array();
        for (auto elem : shapeNames) {
            result.push_back(elem);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json find_core_material_by_name(json materialName) {
    try {
        auto materialData = OpenMagnetics::find_core_material_by_name(materialName);
        json result;
        to_json(result, materialData);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json find_core_shape_by_name(json shapeName) {
    try {
        auto shapeData = OpenMagnetics::find_core_shape_by_name(shapeName);
        json result;
        to_json(result, shapeData);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_core_processed_description(json coreDataJson) {
    try {
        OpenMagnetics::Core core(coreDataJson, false, false, false);
        core.process_data();
        json result;
        to_json(result, core.get_processed_description().value());
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_core_geometrical_description(json coreDataJson) {
    try {
        OpenMagnetics::Core core(coreDataJson, false, false, false);
        auto geometricalDescription = core.create_geometrical_description().value();
        json result = json::array();
        for (auto& elem : geometricalDescription) {
            json aux;
            to_json(aux, elem);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_core_gapping(json coreDataJson) {
    try {
        OpenMagnetics::Core core(coreDataJson, false, false, false);
        core.process_gap();
        json result = json::array();
        for (auto& gap : core.get_functional_description().get_gapping()) {
            json aux;
            to_json(aux, gap);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_shape_data(json shapeJson) {
    CoreShape shape(shapeJson);
    OpenMagnetics::Core core;
    CoreFunctionalDescription coreFunctionalDescription;
    coreFunctionalDescription.set_shape(shape);
    coreFunctionalDescription.set_material("Dummy");
    coreFunctionalDescription.set_number_stacks(1);
    if (shape.get_magnetic_circuit() == MagneticCircuit::OPEN) {
        coreFunctionalDescription.set_type(CoreType::TWO_PIECE_SET);
    }
    else {
        if (shape.get_family() == CoreShapeFamily::T) {
            coreFunctionalDescription.set_type(CoreType::TOROIDAL);
        }
        else {
            coreFunctionalDescription.set_type(CoreType::CLOSED_SHAPE);
        }
    }
    core.set_functional_description(coreFunctionalDescription);
    core.process_data();

    json result;
    to_json(result, core);
    return result;
}

json calculate_core_data(json coreDataJson, bool includeMaterialData) {
    try {
        OpenMagnetics::Core core(coreDataJson, includeMaterialData, true);
        json result;
        to_json(result, core);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json load_core_data(json coresJson) {
    json result = json::array();
    for (auto& coreJson : coresJson) {
        OpenMagnetics::Core core(coreJson, false);
        json aux;
        to_json(aux, core);
        result.push_back(aux);
    }
    return result;
}

json get_material_data(std::string materialName) {
    auto materialData = OpenMagnetics::find_core_material_by_name(materialName);
    json result;
    to_json(result, materialData);
    return result;
}

json get_core_temperature_dependant_parameters(json coreData, double temperature) {
    OpenMagnetics::Core core(coreData);
    json result;

    result["magneticFluxDensitySaturation"] = core.get_magnetic_flux_density_saturation(temperature, false);
    result["magneticFieldStrengthSaturation"] = core.get_magnetic_field_strength_saturation(temperature);
    result["initialPermeability"] = core.get_initial_permeability(temperature);
    result["effectivePermeability"] = core.get_effective_permeability(temperature);
    result["reluctance"] = core.get_reluctance(temperature);
    auto reluctanceModel = OpenMagnetics::ReluctanceModel::factory();
    result["permeance"] = 1.0 / reluctanceModel->get_ungapped_core_reluctance(core);
    result["resistivity"] = core.get_resistivity(temperature);

    return result;
}

json get_shape_data(std::string shapeName) {
    try {
        auto shapeData = OpenMagnetics::find_core_shape_by_name(shapeName);
        json result;
        to_json(result, shapeData);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

std::vector<std::string> get_available_shape_families() {
    std::vector<std::string> families;
    for (auto& family : magic_enum::enum_names<CoreShapeFamily>()) {
        std::string familyJson(family);
        families.push_back(familyJson);
    }
    return families;
}

std::vector<std::string> get_available_core_manufacturers() {
    std::vector<std::string> manufacturers;
    auto materials = OpenMagnetics::get_materials("");
    for (auto material : materials) {
        std::string manufacturer = material.get_manufacturer_info().get_name();
        if (std::find(manufacturers.begin(), manufacturers.end(), manufacturer) == manufacturers.end()) {
            manufacturers.push_back(manufacturer);
        }
    }
    return manufacturers;
}

std::vector<std::string> get_available_core_shape_families() {
    std::vector<std::string> families;
    for (auto& family : magic_enum::enum_names<CoreShapeFamily>()) {
        std::string familyJson(family);
        families.push_back(familyJson);
    }
    return families;
}

std::vector<std::string> get_available_core_materials(std::string manufacturer) {
    return OpenMagnetics::get_core_material_names(manufacturer);
}

std::vector<std::string> get_available_core_shapes() {
    return OpenMagnetics::get_core_shape_names();
}

json get_available_cores() {
    if (OpenMagnetics::coreMaterialDatabase.empty()) {
        OpenMagnetics::load_cores();
    }

    try {
        json result = json::array();
        for (auto elem : OpenMagnetics::coreDatabase) {
            json aux;
            to_json(aux, elem);
            result.push_back(aux);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_gap_reluctance(json coreGapData, std::string modelNameString) {
    OpenMagnetics::ReluctanceModels modelName;
    from_json(modelNameString, modelName);
    auto reluctanceModel = OpenMagnetics::ReluctanceModel::factory(modelName);
    CoreGap coreGap(coreGapData);

    auto coreGapResult = reluctanceModel->get_gap_reluctance(coreGap);
    json result;
    to_json(result, coreGapResult);
    return result;
}

json get_gap_reluctance_model_information() {
    json info;
    info["information"] = OpenMagnetics::ReluctanceModel::get_models_information();
    info["errors"] = OpenMagnetics::ReluctanceModel::get_models_errors();
    info["internal_links"] = OpenMagnetics::ReluctanceModel::get_models_internal_links();
    info["external_links"] = OpenMagnetics::ReluctanceModel::get_models_external_links();
    return info;
}

double calculate_inductance_from_number_turns_and_gapping(json coreData, json coilData, json operatingPointData, json modelsData) {
    OpenMagnetics::Core core(coreData);
    OpenMagnetics::Coil coil(coilData);
    OperatingPoint operatingPoint(operatingPointData);

    std::map<std::string, std::string> models = modelsData.get<std::map<std::string, std::string>>();

    auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
    if (models.find("reluctance") != models.end()) {
        std::string modelNameJsonUpper = models["reluctance"];
        std::transform(modelNameJsonUpper.begin(), modelNameJsonUpper.end(), modelNameJsonUpper.begin(), ::toupper);
        reluctanceModelName = magic_enum::enum_cast<OpenMagnetics::ReluctanceModels>(modelNameJsonUpper).value();
    }

    OpenMagnetics::MagnetizingInductance magnetizingInductanceObj(reluctanceModelName);
    double magnetizingInductance = magnetizingInductanceObj.calculate_inductance_from_number_turns_and_gapping(core, coil, &operatingPoint).get_magnetizing_inductance().get_nominal().value();

    return magnetizingInductance;
}

double calculate_number_turns_from_gapping_and_inductance(json coreData, json inputsData, json modelsData) {
    OpenMagnetics::Core core(coreData);
    OpenMagnetics::Inputs inputs(inputsData);

    std::map<std::string, std::string> models = modelsData.get<std::map<std::string, std::string>>();
    
    auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
    if (models.find("reluctance") != models.end()) {
        OpenMagnetics::from_json(models["reluctance"], reluctanceModelName);
    }

    OpenMagnetics::MagnetizingInductance magnetizingInductanceObj(reluctanceModelName);
    double numberTurns = magnetizingInductanceObj.calculate_number_turns_from_gapping_and_inductance(core, &inputs);

    return numberTurns;
}

json calculate_gapping_from_number_turns_and_inductance(json coreData, json coilData, json inputsData, std::string gappingTypeJson, int decimals, json modelsData) {
    OpenMagnetics::Core core(coreData);
    OpenMagnetics::Coil coil(coilData);
    OpenMagnetics::Inputs inputs(inputsData);

    std::map<std::string, std::string> models = modelsData.get<std::map<std::string, std::string>>();
    std::transform(gappingTypeJson.begin(), gappingTypeJson.end(), gappingTypeJson.begin(), ::toupper);
    OpenMagnetics::GappingType gappingType = magic_enum::enum_cast<OpenMagnetics::GappingType>(gappingTypeJson).value();
    
    auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
    if (models.find("reluctance") != models.end()) {
        OpenMagnetics::from_json(models["reluctance"], reluctanceModelName);
    }

    OpenMagnetics::MagnetizingInductance magnetizingInductanceObj(reluctanceModelName);
    std::vector<CoreGap> gapping = magnetizingInductanceObj.calculate_gapping_from_number_turns_and_inductance(core, coil, &inputs, gappingType, decimals);

    core.set_processed_description(std::nullopt);
    core.set_geometrical_description(std::nullopt);
    core.get_mutable_functional_description().set_gapping(gapping);
    core.process_data();
    core.process_gap();
    auto geometricalDescription = core.create_geometrical_description();
    core.set_geometrical_description(geometricalDescription);

    json result;
    to_json(result, core);
    return result;
}

double calculate_core_maximum_magnetic_energy(json coreDataJson, json operatingPointJson) {
    try {
        OperatingPoint operatingPoint = OperatingPoint(operatingPointJson);
        OpenMagnetics::Core core = OpenMagnetics::Core(coreDataJson, false, false, false);
        if (!core.get_processed_description()) {
            core.process_data();
            core.process_gap();
        }

        auto magneticEnergy = OpenMagnetics::MagneticEnergy();

        double coreMaximumMagneticEnergy;
        if (operatingPoint.get_excitations_per_winding().size() == 0) {
            coreMaximumMagneticEnergy = magneticEnergy.calculate_core_maximum_magnetic_energy(core, std::nullopt);
        }
        else {
            coreMaximumMagneticEnergy = magneticEnergy.calculate_core_maximum_magnetic_energy(core, operatingPoint);
        }
        return coreMaximumMagneticEnergy;
    }
    catch (const std::exception &exc) {
        std::cout << "Exception: " + std::string{exc.what()} << std::endl;
        return -1;
    }
}

double calculate_saturation_current(json magneticJson, double temperature) {
    OpenMagnetics::Magnetic magnetic(magneticJson);
    return magnetic.calculate_saturation_current(temperature);
}

double calculate_temperature_from_core_thermal_resistance(json coreJson, double totalLosses) {
    OpenMagnetics::Core core(coreJson);
    return OpenMagnetics::Temperature::calculate_temperature_from_core_thermal_resistance(core, totalLosses);
}

void register_core_bindings(py::module& m) {
    // Core materials
    m.def("get_core_materials", &get_core_materials,
        R"pbdoc(
        Retrieve all available core materials from the database.
        
        Returns complete material specifications including:
        - Manufacturer information
        - Permeability curves
        - Steinmetz coefficients for loss calculations
        - Saturation characteristics
        - Temperature coefficients
        
        Returns:
            JSON array of CoreMaterial objects with full specifications.
        
        Example:
            >>> materials = PyMKF.get_core_materials()
            >>> ferroxcube = [m for m in materials if "Ferroxcube" in m["manufacturerInfo"]["name"]]
        )pbdoc");
    
    m.def("get_material_permeability", &get_material_permeability, 
        R"pbdoc(
        Calculate initial permeability for a material under specific conditions.
        
        Accounts for temperature dependence, DC bias effects, and frequency
        roll-off based on material characterization data.
        
        Args:
            material_name: Name of the core material (e.g., "3C95", "N87").
            temperature: Operating temperature in Celsius.
            magnetic_field_dc_bias: DC magnetic field bias in A/m.
            frequency: Operating frequency in Hz.
        
        Returns:
            Initial relative permeability (dimensionless).
        
        Example:
            >>> mu_i = PyMKF.get_material_permeability("3C95", 25, 0, 100000)
            >>> print(f"Permeability at 100kHz: {mu_i:.0f}")
        )pbdoc",
        py::arg("material_name"), py::arg("temperature"), py::arg("magnetic_field_dc_bias"), py::arg("frequency"));
    
    m.def("get_material_resistivity", &get_material_resistivity,
        R"pbdoc(
        Calculate electrical resistivity for a core material.
        
        Core resistivity affects eddy current losses and is temperature-dependent.
        
        Args:
            material_name: Name of the core material.
            temperature: Temperature in Celsius.
        
        Returns:
            Resistivity in Ohm·m.
        )pbdoc",
        py::arg("material_name"), py::arg("temperature"));
    
    m.def("get_core_material_steinmetz_coefficients", &get_core_material_steinmetz_coefficients,
        R"pbdoc(
        Retrieve Steinmetz coefficients for core loss calculation.
        
        Returns k, alpha, beta coefficients for: Pv = k * f^alpha * B^beta
        Coefficients are interpolated for the specified frequency from
        manufacturer's multi-range characterization data.
        
        Args:
            material_name: Name of the core material.
            frequency: Operating frequency in Hz for coefficient selection.
        
        Returns:
            JSON SteinmetzCoreLossesMethodRangeDatum with fields:
                - k: Steinmetz constant
                - alpha: Frequency exponent
                - beta: Flux density exponent
                - minimumFrequency, maximumFrequency: Valid range
                - ct0, ct1, ct2: Optional temperature coefficients
        )pbdoc",
        py::arg("material_name"), py::arg("frequency"));

    // Core shapes
    m.def("get_core_shapes", &get_core_shapes,
        R"pbdoc(
        Retrieve all available core shapes from the database.
        
        Returns shape specifications including:
        - Dimensional parameters
        - Family type (E, ETD, PQ, RM, toroidal, etc.)
        - Winding window geometry
        - Magnetic circuit type (open/closed)
        
        Returns:
            JSON array of CoreShape objects.
        )pbdoc");
    
    m.def("get_core_shape_families", &get_core_shape_families,
        R"pbdoc(
        Retrieve list of unique core shape families.
        
        Families include: E, EI, EFD, EQ, ER, ETD, EC, PQ, PM, RM, T (toroidal),
        P (pot), U, UI, LP (planar), and others.
        
        Returns:
            JSON array of CoreShapeFamily strings.
        )pbdoc");

    // Name retrieval functions
    m.def("get_core_material_names", &get_core_material_names,
        R"pbdoc(
        Retrieve list of all core material names in database.
        
        Returns:
            JSON array of material name strings.
        )pbdoc");
    
    m.def("get_core_material_names_by_manufacturer", &get_core_material_names_by_manufacturer,
        R"pbdoc(
        Retrieve core material names filtered by manufacturer.
        
        Args:
            manufacturer_name: Manufacturer name (e.g., "TDK", "Ferroxcube").
        
        Returns:
            JSON array of material name strings from that manufacturer.
        )pbdoc",
        py::arg("manufacturer_name"));
    
    m.def("get_core_shape_names", &get_core_shape_names,
        R"pbdoc(
        Retrieve list of core shape names.
        
        Args:
            include_toroidal: Whether to include toroidal shapes.
        
        Returns:
            JSON array of shape name strings (e.g., "E 42/21/15", "ETD 49").
        )pbdoc",
        py::arg("include_toroidal"));

    // Lookup functions
    m.def("find_core_material_by_name", &find_core_material_by_name,
        R"pbdoc(
        Find complete core material data by name.
        
        Args:
            name: Material name (e.g., "3C95", "N87", "N49").
        
        Returns:
            JSON CoreMaterial object with full specification, or error.
        )pbdoc",
        py::arg("name"));
    
    m.def("find_core_shape_by_name", &find_core_shape_by_name,
        R"pbdoc(
        Find complete core shape data by name.
        
        Args:
            name: Shape name (e.g., "E 42/21/15", "ETD 49/25/16").
        
        Returns:
            JSON CoreShape object with full dimensional data, or error.
        )pbdoc",
        py::arg("name"));

    // Core calculations
    m.def("calculate_core_data", &calculate_core_data,
        R"pbdoc(
        Process core functional description and compute all derived parameters.
        
        Takes a core functional description (shape, material, gapping) and
        calculates the processed description including:
        - Effective magnetic parameters (Ae, le, Ve)
        - Winding window dimensions
        - Column geometry
        - Geometrical description for visualization
        
        Args:
            core_data_json: JSON object with functionalDescription containing:
                - shape: CoreShape object or shape name string
                - material: CoreMaterial object or material name string
                - gapping: Array of CoreGap objects
                - numberStacks: Number of stacked cores (default 1)
            include_material_data: Whether to include full material curves.
        
        Returns:
            JSON Core object with functionalDescription, processedDescription,
            and geometricalDescription fully populated.
        
        Example:
            >>> core_data = {
            ...     "functionalDescription": {
            ...         "shape": "E 42/21/15",
            ...         "material": "3C95",
            ...         "gapping": [{"type": "subtractive", "length": 0.001}],
            ...         "numberStacks": 1
            ...     }
            ... }
            >>> core = PyMKF.calculate_core_data(core_data, False)
            >>> print(f"Ae = {core['processedDescription']['effectiveParameters']['effectiveArea']*1e6:.1f} mm²")
        )pbdoc",
        py::arg("core_data_json"), py::arg("include_material_data"));
    
    m.def("calculate_core_processed_description", &calculate_core_processed_description,
        R"pbdoc(
        Calculate only the processed description for a core.
        
        Faster than calculate_core_data when only effective parameters are needed.
        
        Args:
            core_data_json: JSON object with functionalDescription.
        
        Returns:
            JSON CoreProcessedDescription with effectiveParameters,
            windingWindows, and columns.
        )pbdoc",
        py::arg("core_data_json"));
    
    m.def("calculate_core_geometrical_description", &calculate_core_geometrical_description,
        R"pbdoc(
        Calculate geometrical description for core visualization.
        
        Generates 3D piece geometry for CAD export or rendering.
        
        Args:
            core_data_json: JSON object with functionalDescription.
        
        Returns:
            JSON array of CoreGeometricalDescriptionElement objects.
        )pbdoc",
        py::arg("core_data_json"));
    
    m.def("calculate_core_gapping", &calculate_core_gapping,
        R"pbdoc(
        Process and calculate gapping configuration for a core.
        
        Computes gap areas, positions, and fringing factors.
        
        Args:
            core_data_json: JSON object with core and gapping specification.
        
        Returns:
            JSON array of processed CoreGap objects.
        )pbdoc",
        py::arg("core_data_json"));
    
    m.def("load_core_data", &load_core_data,
        R"pbdoc(
        Load and process multiple cores from JSON array.
        
        Args:
            cores_json: JSON array of core specifications.
        
        Returns:
            JSON array of processed Core objects.
        )pbdoc",
        py::arg("cores_json"));
    
    m.def("get_material_data", &get_material_data,
        R"pbdoc(
        Get complete material data by name.
        
        Args:
            material_name: Name of the material.
        
        Returns:
            JSON CoreMaterial object.
        )pbdoc",
        py::arg("material_name"));
    
    m.def("get_core_temperature_dependant_parameters", &get_core_temperature_dependant_parameters,
        R"pbdoc(
        Get temperature-dependent magnetic parameters for a core.
        
        Calculates key parameters at the specified temperature:
        
        Args:
            core_data: JSON object with core specification.
            temperature: Temperature in Celsius.
        
        Returns:
            JSON object with:
                - magneticFluxDensitySaturation: Bsat in Tesla
                - magneticFieldStrengthSaturation: Hsat in A/m
                - initialPermeability: μi (dimensionless)
                - effectivePermeability: μe (dimensionless)
                - reluctance: Core reluctance in A/Wb
                - permeance: Inverse reluctance in Wb/A
                - resistivity: Core resistivity in Ohm·m
        )pbdoc",
        py::arg("core_data"), py::arg("temperature"));
    
    m.def("calculate_shape_data", &calculate_shape_data,
        R"pbdoc(
        Calculate complete core data from shape only.
        
        Creates a core with dummy material for shape analysis.
        
        Args:
            shape_json: JSON CoreShape object.
        
        Returns:
            JSON Core object with processed dimensions.
        )pbdoc",
        py::arg("shape_json"));
    
    m.def("get_shape_data", &get_shape_data,
        R"pbdoc(
        Get shape data by name.
        
        Args:
            shape_name: Name of the shape.
        
        Returns:
            JSON CoreShape object.
        )pbdoc",
        py::arg("shape_name"));

    // Availability queries
    m.def("get_available_shape_families", &get_available_shape_families,
        R"pbdoc(
        Get list of all supported shape family types.
        
        Returns:
            List of family name strings.
        )pbdoc");
    
    m.def("get_available_core_materials", &get_available_core_materials,
        R"pbdoc(
        Get list of available core materials, optionally filtered by manufacturer.
        
        Args:
            manufacturer: Manufacturer name filter (empty for all).
        
        Returns:
            List of material name strings.
        )pbdoc",
        py::arg("manufacturer"));
    
    m.def("get_available_core_manufacturers", &get_available_core_manufacturers,
        R"pbdoc(
        Get list of all core material manufacturers in database.
        
        Returns:
            List of manufacturer name strings (TDK, Ferroxcube, Fair-Rite, etc.).
        )pbdoc");
    
    m.def("get_available_core_shape_families", &get_available_core_shape_families,
        R"pbdoc(
        Get list of all core shape families.
        
        Returns:
            List of family name strings.
        )pbdoc");
    
    m.def("get_available_core_shapes", &get_available_core_shapes,
        R"pbdoc(
        Get list of all available core shape names.
        
        Returns:
            List of shape name strings.
        )pbdoc");
    
    m.def("get_available_cores", &get_available_cores,
        R"pbdoc(
        Get all available pre-configured cores from database.
        
        Returns complete Core objects ready for use, typically representing
        manufacturer stock items.
        
        Returns:
            JSON array of Core objects.
        )pbdoc");

    // Gap and reluctance
    m.def("calculate_gap_reluctance", &calculate_gap_reluctance,
        R"pbdoc(
        Calculate magnetic reluctance of an air gap.
        
        Uses analytical models to compute gap reluctance including fringing.
        
        Args:
            core_gap_data: JSON CoreGap object with gap geometry.
            model_name_string: Reluctance model name:
                - "ZHANG": Zhang's improved method
                - "MUEHLETHALER": 3D reluctance approach
                - "PARTRIDGE": McLyman handbook method
                - "EFFECTIVE_AREA": Area-based approximation
                - "STENGLEIN": Large gap method
                - "BALAKRISHNAN": Schwarz-Christoffel method
                - "CLASSIC": Basic uniform field
        
        Returns:
            JSON AirGapReluctanceOutput with:
                - reluctance: Gap reluctance in A/Wb
                - fringingFactor: Fringing flux correction factor
        )pbdoc",
        py::arg("core_gap_data"), py::arg("model_name_string"));
    
    m.def("get_gap_reluctance_model_information", &get_gap_reluctance_model_information,
        R"pbdoc(
        Get documentation for available gap reluctance models.
        
        Returns:
            JSON object with:
                - information: Description of each model
                - errors: Typical error percentages
                - internal_links: OpenMagnetics documentation links
                - external_links: Academic reference links
        )pbdoc");
    
    m.def("calculate_inductance_from_number_turns_and_gapping", &calculate_inductance_from_number_turns_and_gapping,
        R"pbdoc(
        Calculate inductance from turns count and gap configuration.
        
        Uses reluctance model to compute: L = N² / R_total
        
        Args:
            core_data: JSON object with core specification.
            coil_data: JSON object with coil specification (for turns).
            operating_point_data: JSON operating point for DC bias consideration.
            models_data: JSON dict with "reluctance" model selection.
        
        Returns:
            Magnetizing inductance in Henries.
        )pbdoc",
        py::arg("core_data"), py::arg("coil_data"), py::arg("operating_point_data"), py::arg("models_data"));
    
    m.def("calculate_number_turns_from_gapping_and_inductance", &calculate_number_turns_from_gapping_and_inductance,
        R"pbdoc(
        Calculate required turns from gap and target inductance.
        
        Computes: N = sqrt(L * R_total)
        
        Args:
            core_data: JSON object with core specification.
            inputs_data: JSON Inputs with magnetizingInductance requirement.
            models_data: JSON dict with "reluctance" model selection.
        
        Returns:
            Required number of turns (may be non-integer).
        )pbdoc",
        py::arg("core_data"), py::arg("inputs_data"), py::arg("models_data"));
    
    m.def("calculate_gapping_from_number_turns_and_inductance", &calculate_gapping_from_number_turns_and_inductance,
        R"pbdoc(
        Calculate required gap from turns count and target inductance.
        
        Iteratively solves for gap length to achieve target inductance.
        
        Args:
            core_data: JSON object with core specification.
            coil_data: JSON object with coil specification.
            inputs_data: JSON Inputs with magnetizingInductance requirement.
            gapping_type_json: Gap type ("SUBTRACTIVE", "ADDITIVE", "DISTRIBUTED").
            decimals: Precision in decimal places for gap length.
            models_data: JSON dict with "reluctance" model selection.
        
        Returns:
            JSON Core object with updated gapping configuration.
        )pbdoc",
        py::arg("core_data"), py::arg("coil_data"), py::arg("inputs_data"),
        py::arg("gapping_type_json"), py::arg("decimals"), py::arg("models_data"));

    // Additional core functions
    m.def("calculate_core_maximum_magnetic_energy", &calculate_core_maximum_magnetic_energy,
        R"pbdoc(
        Calculate maximum magnetic energy storage capacity of core.
        
        Energy = 0.5 * L * I²_sat or from gap volume and saturation.
        
        Args:
            core_data_json: JSON object with core specification.
            operating_point_json: JSON operating point (optional, for DC bias).
        
        Returns:
            Maximum storable magnetic energy in Joules.
        )pbdoc",
        py::arg("core_data_json"), py::arg("operating_point_json"));
    
    m.def("calculate_saturation_current", &calculate_saturation_current,
        R"pbdoc(
        Calculate saturation current for a complete magnetic.
        
        The current at which core reaches saturation flux density.
        
        Args:
            magnetic_json: JSON Magnetic object (core + coil).
            temperature: Operating temperature in Celsius.
        
        Returns:
            Saturation current in Amperes.
        )pbdoc",
        py::arg("magnetic_json"), py::arg("temperature"));
    
    m.def("calculate_temperature_from_core_thermal_resistance", &calculate_temperature_from_core_thermal_resistance,
        R"pbdoc(
        Calculate core temperature from thermal resistance and losses.
        
        T_core = T_ambient + P_loss * R_thermal
        
        Args:
            core_json: JSON Core object with thermal resistance data.
            total_losses: Total power dissipation in Watts.
        
        Returns:
            Estimated core temperature in Celsius.
        )pbdoc", 
        py::arg("core_json"), py::arg("total_losses"));
}

} // namespace PyMKF
