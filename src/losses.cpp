#include "losses.h"

namespace PyMKF {

json calculate_core_losses(json coreData, json coilData, json inputsData, json modelsData) {
    OpenMagnetics::Core core(coreData);
    OpenMagnetics::Coil coil(coilData);
    OpenMagnetics::Inputs inputs(inputsData);
    auto operatingPoint = inputs.get_operating_point(0);
    OperatingPointExcitation excitation = operatingPoint.get_excitations_per_winding()[0];
    double magnetizingInductance = OpenMagnetics::resolve_dimensional_values(inputs.get_design_requirements().get_magnetizing_inductance());
    if (!excitation.get_current()) {
        auto magnetizingCurrent = OpenMagnetics::Inputs::calculate_magnetizing_current(excitation, magnetizingInductance, true, 0.0);
        excitation.set_current(magnetizingCurrent);
        operatingPoint.get_mutable_excitations_per_winding()[0] = excitation;
    }

    std::map<std::string, std::string> models = modelsData.get<std::map<std::string, std::string>>();

    auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
    if (models.find("reluctance") != models.end()) {
        OpenMagnetics::from_json(models["reluctance"], reluctanceModelName);
    }
    auto coreLossesModelName = OpenMagnetics::defaults.coreLossesModelDefault;
    if (models.find("coreLosses") != models.end()) {
        OpenMagnetics::from_json(models["coreLosses"], coreLossesModelName);
    }
    auto coreTemperatureModelName = OpenMagnetics::defaults.coreTemperatureModelDefault;
    if (models.find("coreTemperature") != models.end()) {
        OpenMagnetics::from_json(models["coreTemperature"], coreTemperatureModelName);
    }

    OpenMagnetics::Magnetic magnetic;
    magnetic.set_core(core);
    magnetic.set_coil(coil);

    OpenMagnetics::MagneticSimulator magneticSimulator;
    magneticSimulator.set_core_losses_model_name(coreLossesModelName);
    magneticSimulator.set_core_temperature_model_name(coreTemperatureModelName);
    magneticSimulator.set_reluctance_model_name(reluctanceModelName);
    auto coreLossesOutput = magneticSimulator.calculate_core_losses(operatingPoint, magnetic);
    json result;
    to_json(result, coreLossesOutput);

    OpenMagnetics::MagnetizingInductance magnetizingInductanceObj(reluctanceModelName);
    auto magneticFluxDensity = magnetizingInductanceObj.calculate_inductance_and_magnetic_flux_density(core, coil, &operatingPoint).second;

    result["magneticFluxDensityPeak"] = magneticFluxDensity.get_processed().value().get_peak().value();
    result["magneticFluxDensityAcPeak"] = magneticFluxDensity.get_processed().value().get_peak().value() - magneticFluxDensity.get_processed().value().get_offset();
    result["voltageRms"] = operatingPoint.get_mutable_excitations_per_winding()[0].get_voltage().value().get_processed().value().get_rms().value();
    result["currentRms"] = operatingPoint.get_mutable_excitations_per_winding()[0].get_current().value().get_processed().value().get_rms().value();
    result["apparentPower"] = operatingPoint.get_mutable_excitations_per_winding()[0].get_voltage().value().get_processed().value().get_rms().value() * operatingPoint.get_mutable_excitations_per_winding()[0].get_current().value().get_processed().value().get_rms().value();
    if (coreLossesOutput.get_temperature()) {
        result["maximumCoreTemperature"] = coreLossesOutput.get_temperature().value();
        result["maximumCoreTemperatureRise"] = coreLossesOutput.get_temperature().value() - operatingPoint.get_conditions().get_ambient_temperature();
    }

    return result;
}

json get_core_losses_model_information(json material) {
    json info;
    info["information"] = OpenMagnetics::CoreLossesModel::get_models_information();
    info["errors"] = OpenMagnetics::CoreLossesModel::get_models_errors();
    info["internal_links"] = OpenMagnetics::CoreLossesModel::get_models_internal_links();
    info["external_links"] = OpenMagnetics::CoreLossesModel::get_models_external_links();
    info["available_models"] = OpenMagnetics::CoreLossesModel::get_methods_string(material);
    return info;
}

json get_core_temperature_model_information() {
    json info;
    info["information"] = OpenMagnetics::CoreTemperatureModel::get_models_information();
    info["errors"] = OpenMagnetics::CoreTemperatureModel::get_models_errors();
    info["internal_links"] = OpenMagnetics::CoreTemperatureModel::get_models_internal_links();
    info["external_links"] = OpenMagnetics::CoreTemperatureModel::get_models_external_links();
    return info;
}

json calculate_steinmetz_coefficients(json dataJson, json rangesJson) {
    try {
        std::vector<std::pair<double, double>> ranges;
        for (auto rangeJson : rangesJson) {
            std::pair<double, double> range{rangeJson[0], rangeJson[1]};
            ranges.push_back(range);
        }
        std::vector<VolumetricLossesPoint> data;
        for (auto datumJson : dataJson) {
            VolumetricLossesPoint datum(datumJson);
            data.push_back(datum);
        }

        auto [coefficientsPerRange, errorPerRange] = OpenMagnetics::CoreLossesSteinmetzModel::calculate_steinmetz_coefficients(data, ranges);

        json result;
        to_json(result, coefficientsPerRange);
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json calculate_steinmetz_coefficients_with_error(json dataJson, json rangesJson) {
    try {
        std::vector<std::pair<double, double>> ranges;
        for (auto rangeJson : rangesJson) {
            std::pair<double, double> range{rangeJson[0], rangeJson[1]};
            ranges.push_back(range);
        }
        std::vector<VolumetricLossesPoint> data;
        for (auto datumJson : dataJson) {
            VolumetricLossesPoint datum(datumJson);
            data.push_back(datum);
        }

        auto [coefficientsPerRange, errorPerRange] = OpenMagnetics::CoreLossesSteinmetzModel::calculate_steinmetz_coefficients(data, ranges);

        json aux;
        to_json(aux, coefficientsPerRange);
        json result;
        result["coefficientsPerRange"] = aux;
        result["errorPerRange"] = errorPerRange;
        return result;
    }
    catch (const std::exception &exc) {
        return "Exception: " + std::string{exc.what()};
    }
}

json calculate_winding_losses(json magneticJson, json operatingPointJson, double temperature) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);

        auto windingLossesOutput = OpenMagnetics::WindingLosses().calculate_losses(magnetic, operatingPoint, temperature);

        json result;
        to_json(result, windingLossesOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_ohmic_losses(json coilJson, json operatingPointJson, double temperature) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        OperatingPoint operatingPoint(operatingPointJson);

        auto windingLossesOutput = OpenMagnetics::WindingOhmicLosses::calculate_ohmic_losses(coil, operatingPoint, temperature);

        json result;
        to_json(result, windingLossesOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_magnetic_field_strength_field(json operatingPointJson, json magneticJson) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);
        OpenMagnetics::MagneticField magneticField;

        auto windingWindowMagneticStrengthFieldOutput = magneticField.calculate_magnetic_field_strength_field(operatingPoint, magnetic);

        json result;
        to_json(result, windingWindowMagneticStrengthFieldOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_proximity_effect_losses(json coilJson, double temperature, json windingLossesOutputJson, json windingWindowMagneticStrengthFieldOutputJson) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        WindingLossesOutput windingLossesOutput(windingLossesOutputJson);
        WindingWindowMagneticStrengthFieldOutput windingWindowMagneticStrengthFieldOutput(windingWindowMagneticStrengthFieldOutputJson);

        auto windingLossesOutputOutput = OpenMagnetics::WindingProximityEffectLosses::calculate_proximity_effect_losses(coil, temperature, windingLossesOutput, windingWindowMagneticStrengthFieldOutput);

        json result;
        to_json(result, windingLossesOutputOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_skin_effect_losses(json coilJson, json windingLossesOutputJson, double temperature) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        WindingLossesOutput windingLossesOutput(windingLossesOutputJson);

        auto windingLossesOutputOutput = OpenMagnetics::WindingSkinEffectLosses::calculate_skin_effect_losses(coil, temperature, windingLossesOutput);
        json result;
        to_json(result, windingLossesOutputOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_skin_effect_losses_per_meter(json wireJson, json currentJson, double temperature, double currentDivider) {
    try {
        OpenMagnetics::Wire wire(wireJson);
        SignalDescriptor current(currentJson);

        auto skinEffectLossesPerMeter = OpenMagnetics::WindingSkinEffectLosses::calculate_skin_effect_losses_per_meter(wire, current, temperature, currentDivider);

        json result = skinEffectLossesPerMeter;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

double calculate_dc_resistance_per_meter(json wireJson, double temperature) {
    OpenMagnetics::Wire wire(wireJson);
    auto dcResistancePerMeter = OpenMagnetics::WindingOhmicLosses::calculate_dc_resistance_per_meter(wire, temperature);
    return dcResistancePerMeter;
}

double calculate_dc_losses_per_meter(json wireJson, json currentJson, double temperature) {
    OpenMagnetics::Wire wire(wireJson);
    SignalDescriptor current(currentJson);
    auto dcLossesPerMeter = OpenMagnetics::WindingOhmicLosses::calculate_ohmic_losses_per_meter(wire, current, temperature);
    return dcLossesPerMeter;
}

double calculate_skin_ac_factor(json wireJson, json currentJson, double temperature) {
    OpenMagnetics::Wire wire(wireJson);
    SignalDescriptor current(currentJson);
    auto dcLossesPerMeter = OpenMagnetics::WindingOhmicLosses::calculate_ohmic_losses_per_meter(wire, current, temperature);
    auto [skinLossesPerMeter, _] = OpenMagnetics::WindingSkinEffectLosses::calculate_skin_effect_losses_per_meter(wire, current, temperature);
    auto skinAcFactor = (skinLossesPerMeter + dcLossesPerMeter) / dcLossesPerMeter;
    return skinAcFactor;
}

double calculate_skin_ac_losses_per_meter(json wireJson, json currentJson, double temperature) {
    OpenMagnetics::Wire wire(wireJson);
    SignalDescriptor current(currentJson);
    auto [skinLossesPerMeter, _] = OpenMagnetics::WindingSkinEffectLosses::calculate_skin_effect_losses_per_meter(wire, current, temperature);
    return skinLossesPerMeter;
}

double calculate_skin_ac_resistance_per_meter(json wireJson, json currentJson, double temperature) {
    OpenMagnetics::Wire wire(wireJson);
    SignalDescriptor current(currentJson);
    auto dcLossesPerMeter = OpenMagnetics::WindingOhmicLosses::calculate_ohmic_losses_per_meter(wire, current, temperature);
    auto [skinLossesPerMeter, _] = OpenMagnetics::WindingSkinEffectLosses::calculate_skin_effect_losses_per_meter(wire, current, temperature);
    auto skinAcFactor = (skinLossesPerMeter + dcLossesPerMeter) / dcLossesPerMeter;
    auto dcResistancePerMeter = OpenMagnetics::WindingOhmicLosses::calculate_dc_resistance_per_meter(wire, temperature);

    return dcResistancePerMeter * skinAcFactor;
}

double calculate_effective_current_density(json wireJson, json currentJson, double temperature) {
    OpenMagnetics::Wire wire(wireJson);
    SignalDescriptor current(currentJson);
    auto effectiveCurrentDensity = wire.calculate_effective_current_density(current, temperature);

    return effectiveCurrentDensity;
}

double calculate_effective_skin_depth(std::string materialName, json currentJson, double temperature) {
    try {
        SignalDescriptor current(currentJson);

        if (!current.get_processed()->get_effective_frequency()) {
            throw std::runtime_error("Current processed is missing field effective frequency");
        }
        auto currentEffectiveFrequency = current.get_processed()->get_effective_frequency().value();
        double effectiveSkinDepth = OpenMagnetics::WindingSkinEffectLosses::calculate_skin_depth(materialName, currentEffectiveFrequency, temperature);
        return effectiveSkinDepth;
    }
    catch(const std::exception& ex) {
        return -1;
    }
}

void register_losses_bindings(py::module& m) {
    // Core losses
    m.def("calculate_core_losses", &calculate_core_losses,
        R"pbdoc(
        Calculate core losses for a magnetic component at given operating conditions.
        
        Computes volumetric core losses using the specified model (Steinmetz, iGSE, etc.)
        and returns detailed loss breakdown including temperature effects.
        
        Args:
            core_data: JSON object with core specification (shape, material, gapping).
            coil_data: JSON object with coil specification (windings, turns).
            inputs_data: JSON object with operating points (frequency, flux density).
            models_data: JSON dict specifying models to use:
                - "coreLosses": "STEINMETZ", "IGSE", "MSE", "BARG", "ROSHEN", "PROPRIETARY"
                - "reluctance": "ZHANG", "MUEHLETHALER", "PARTRIDGE", "STENGLEIN"
                - "coreTemperature": Model for temperature estimation
        
        Returns:
            JSON object containing:
                - coreLosses: Total core power loss in Watts
                - magneticFluxDensityPeak: Peak B-field in Tesla
                - magneticFluxDensityAcPeak: AC component peak in Tesla
                - voltageRms: RMS voltage in Volts
                - currentRms: RMS current in Amperes
                - apparentPower: Apparent power in VA
                - maximumCoreTemperature: Estimated max temperature in Celsius
                - maximumCoreTemperatureRise: Temperature rise in Kelvin
        
        Example:
            >>> models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
            >>> losses = PyMKF.calculate_core_losses(core, coil, inputs, models)
            >>> print(f"Core losses: {losses['coreLosses']:.2f} W")
        )pbdoc",
        py::arg("core_data"), py::arg("coil_data"), py::arg("inputs_data"), py::arg("models_data"));
    
    m.def("get_core_losses_model_information", &get_core_losses_model_information,
        R"pbdoc(
        Get documentation and metadata for available core loss models.
        
        Returns information about each model including theoretical basis,
        accuracy, and applicable references.
        
        Args:
            material: JSON object with material data to check model availability.
        
        Returns:
            JSON object containing:
                - information: Description of each model
                - errors: Typical error percentages for each model
                - internal_links: Links to OpenMagnetics documentation
                - external_links: Links to academic references
                - available_models: Models valid for the given material
        )pbdoc",
        py::arg("material"));
    
    m.def("get_core_temperature_model_information", &get_core_temperature_model_information,
        R"pbdoc(
        Get documentation for available core temperature models.
        
        Returns:
            JSON object with model information, errors, and reference links.
        )pbdoc");
    
    m.def("calculate_steinmetz_coefficients", &calculate_steinmetz_coefficients,
        R"pbdoc(
        Fit Steinmetz equation coefficients from measured loss data.
        
        Uses curve fitting to determine k, alpha, beta coefficients for the
        Steinmetz equation: Pv = k * f^alpha * B^beta
        
        Args:
            data_json: JSON array of VolumetricLossesPoint objects with fields:
                - magneticFluxDensity: B-field in Tesla
                - frequency: Frequency in Hz
                - volumetricLosses: Power density in W/m³
            ranges_json: JSON array of [min_freq, max_freq] tuples defining
                         frequency ranges for piecewise fitting.
        
        Returns:
            JSON array of SteinmetzCoreLossesMethodRangeDatum with fitted
            coefficients (k, alpha, beta) for each frequency range.
        )pbdoc",
        py::arg("data_json"), py::arg("ranges_json"));
    
    m.def("calculate_steinmetz_coefficients_with_error", &calculate_steinmetz_coefficients_with_error,
        R"pbdoc(
        Fit Steinmetz coefficients with error estimation.
        
        Same as calculate_steinmetz_coefficients but also returns fitting error.
        
        Args:
            data_json: JSON array of VolumetricLossesPoint measurements.
            ranges_json: JSON array of frequency range tuples.
        
        Returns:
            JSON object with:
                - coefficientsPerRange: Fitted Steinmetz coefficients
                - errorPerRange: RMS fitting error for each range
        )pbdoc",
        py::arg("data_json"), py::arg("ranges_json"));

    // Winding losses
    m.def("calculate_winding_losses", &calculate_winding_losses,
        R"pbdoc(
        Calculate total winding losses including all AC effects.
        
        Computes comprehensive winding losses including:
        - DC ohmic losses (I²R)
        - Skin effect losses (current crowding at high frequency)
        - Proximity effect losses (eddy currents from nearby conductors)
        
        Args:
            magnetic_json: JSON object with complete magnetic specification.
            operating_point_json: JSON object with excitation conditions.
            temperature: Winding temperature in Celsius.
        
        Returns:
            JSON WindingLossesOutput object containing:
                - windingLosses: Total winding loss in Watts
                - windingLossesPerWinding: Losses per winding array
                - ohmicLosses: DC resistance losses breakdown
                - skinEffectLosses: High-frequency skin losses
                - proximityEffectLosses: Proximity effect losses
        )pbdoc",
        py::arg("magnetic_json"), py::arg("operating_point_json"), py::arg("temperature"));
    
    m.def("calculate_ohmic_losses", &calculate_ohmic_losses,
        R"pbdoc(
        Calculate DC ohmic losses in coil windings.
        
        Computes pure resistive I²R losses without AC effects.
        
        Args:
            coil_json: JSON object with coil specification.
            operating_point_json: JSON object with current excitation.
            temperature: Wire temperature in Celsius.
        
        Returns:
            JSON WindingLossesOutput with ohmicLosses field populated.
        )pbdoc",
        py::arg("coil_json"), py::arg("operating_point_json"), py::arg("temperature"));
    
    m.def("calculate_magnetic_field_strength_field", &calculate_magnetic_field_strength_field,
        R"pbdoc(
        Calculate magnetic field strength distribution in winding window.
        
        Computes H-field at all points in the winding window for proximity
        effect calculations and field visualization.
        
        Args:
            operating_point_json: JSON object with excitation conditions.
            magnetic_json: JSON object with magnetic specification.
        
        Returns:
            JSON WindingWindowMagneticStrengthFieldOutput with field data
            at each spatial point and frequency harmonic.
        )pbdoc",
        py::arg("operating_point_json"), py::arg("magnetic_json"));
    
    m.def("calculate_proximity_effect_losses", &calculate_proximity_effect_losses,
        R"pbdoc(
        Calculate proximity effect losses from pre-computed field data.
        
        Uses magnetic field distribution to compute eddy current losses
        induced by external fields from neighboring conductors.
        
        Args:
            coil_json: JSON object with coil specification.
            temperature: Wire temperature in Celsius.
            winding_losses_output_json: Previous WindingLossesOutput (for accumulation).
            field_output_json: WindingWindowMagneticStrengthFieldOutput from
                              calculate_magnetic_field_strength_field().
        
        Returns:
            Updated JSON WindingLossesOutput with proximityEffectLosses added.
        )pbdoc",
        py::arg("coil_json"), py::arg("temperature"), 
        py::arg("winding_losses_output_json"), py::arg("field_output_json"));
    
    m.def("calculate_skin_effect_losses", &calculate_skin_effect_losses,
        R"pbdoc(
        Calculate skin effect losses in coil windings.
        
        Computes additional losses due to current crowding toward conductor
        surface at high frequencies.
        
        Args:
            coil_json: JSON object with coil specification.
            winding_losses_output_json: Previous WindingLossesOutput.
            temperature: Wire temperature in Celsius.
        
        Returns:
            Updated JSON WindingLossesOutput with skinEffectLosses added.
        )pbdoc",
        py::arg("coil_json"), py::arg("winding_losses_output_json"), py::arg("temperature"));
    
    m.def("calculate_skin_effect_losses_per_meter", &calculate_skin_effect_losses_per_meter,
        R"pbdoc(
        Calculate skin effect losses per meter of wire.
        
        Useful for wire selection and comparison.
        
        Args:
            wire_json: JSON object with wire specification.
            current_json: JSON SignalDescriptor with current waveform.
            temperature: Wire temperature in Celsius.
            current_divider: Current sharing factor (1.0 for single conductor).
        
        Returns:
            JSON object with skin effect loss power per meter in W/m.
        )pbdoc",
        py::arg("wire_json"), py::arg("current_json"), py::arg("temperature"), py::arg("current_divider"));

    // DC resistance and losses
    m.def("calculate_dc_resistance_per_meter", &calculate_dc_resistance_per_meter,
        R"pbdoc(
        Calculate DC resistance per meter of wire at given temperature.
        
        Args:
            wire_json: JSON object with wire specification.
            temperature: Wire temperature in Celsius.
        
        Returns:
            DC resistance in Ohms per meter.
        )pbdoc",
        py::arg("wire_json"), py::arg("temperature"));
    
    m.def("calculate_dc_losses_per_meter", &calculate_dc_losses_per_meter,
        R"pbdoc(
        Calculate DC ohmic losses per meter of wire.
        
        Args:
            wire_json: JSON object with wire specification.
            current_json: JSON SignalDescriptor with current waveform.
            temperature: Wire temperature in Celsius.
        
        Returns:
            DC power loss in Watts per meter.
        )pbdoc",
        py::arg("wire_json"), py::arg("current_json"), py::arg("temperature"));
    
    m.def("calculate_skin_ac_losses_per_meter", &calculate_skin_ac_losses_per_meter,
        R"pbdoc(
        Calculate AC skin effect losses per meter (excluding DC component).
        
        Args:
            wire_json: JSON object with wire specification.
            current_json: JSON SignalDescriptor with current waveform.
            temperature: Wire temperature in Celsius.
        
        Returns:
            AC skin effect power loss in Watts per meter.
        )pbdoc",
        py::arg("wire_json"), py::arg("current_json"), py::arg("temperature"));
    
    m.def("calculate_skin_ac_factor", &calculate_skin_ac_factor,
        R"pbdoc(
        Calculate skin effect AC resistance factor (Fr = Rac/Rdc).
        
        The ratio of total AC resistance (including skin effect) to DC resistance.
        Fr = 1.0 means no skin effect; Fr > 1.0 indicates skin effect losses.
        
        Args:
            wire_json: JSON object with wire specification.
            current_json: JSON SignalDescriptor with current waveform.
            temperature: Wire temperature in Celsius.
        
        Returns:
            AC factor (dimensionless ratio >= 1.0).
        )pbdoc",
        py::arg("wire_json"), py::arg("current_json"), py::arg("temperature"));
    
    m.def("calculate_skin_ac_resistance_per_meter", &calculate_skin_ac_resistance_per_meter,
        R"pbdoc(
        Calculate total AC resistance per meter including skin effect.
        
        Rac = Rdc * Fr where Fr is the skin effect AC factor.
        
        Args:
            wire_json: JSON object with wire specification.
            current_json: JSON SignalDescriptor with current waveform.
            temperature: Wire temperature in Celsius.
        
        Returns:
            Total AC resistance in Ohms per meter.
        )pbdoc",
        py::arg("wire_json"), py::arg("current_json"), py::arg("temperature"));
    
    m.def("calculate_effective_current_density", &calculate_effective_current_density,
        R"pbdoc(
        Calculate effective current density in wire conductor.
        
        Accounts for frequency-dependent current distribution due to skin effect.
        
        Args:
            wire_json: JSON object with wire specification.
            current_json: JSON SignalDescriptor with current waveform.
            temperature: Wire temperature in Celsius.
        
        Returns:
            Effective current density in A/m².
        )pbdoc",
        py::arg("wire_json"), py::arg("current_json"), py::arg("temperature"));
    
    m.def("calculate_effective_skin_depth", &calculate_effective_skin_depth,
        R"pbdoc(
        Calculate effective skin depth for a conductor material.
        
        The skin depth is the depth at which current density falls to 1/e
        of its surface value: delta = sqrt(2*rho / (omega*mu))
        
        Args:
            material_name: Name of conductor material (e.g., "copper").
            current_json: JSON SignalDescriptor with effective frequency.
            temperature: Conductor temperature in Celsius.
        
        Returns:
            Skin depth in meters, or -1 if effective frequency not available.
        )pbdoc",
        py::arg("material_name"), py::arg("current_json"), py::arg("temperature"));
}

} // namespace PyMKF
