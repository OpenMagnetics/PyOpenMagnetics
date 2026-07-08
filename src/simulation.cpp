#include "simulation.h"

namespace PyMKF {

json simulate(json inputsJson, json magneticJson, json modelsData) {
    try {
        OpenMagnetics::Inputs inputs(inputsJson);
        OpenMagnetics::Magnetic magnetic(magneticJson);
        
        auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
        if (!modelsData.is_null() && modelsData.find("reluctance") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["reluctance"], reluctanceModelName);
        }
        auto coreLossesModelName = OpenMagnetics::defaults.coreLossesModelDefault;
        if (!modelsData.is_null() && modelsData.find("coreLosses") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["coreLosses"], coreLossesModelName);
        }

        OpenMagnetics::MagneticSimulator magneticSimulator;
        magneticSimulator.set_core_losses_model_name(coreLossesModelName);
        magneticSimulator.set_reluctance_model_name(reluctanceModelName);
        auto mas = magneticSimulator.simulate(inputs, magnetic);

        json result;
        to_json(result, mas);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

std::string export_magnetic_as_subcircuit(json magneticJson) {
    // Returns the raw SPICE subcircuit netlist as a plain string. We must NOT
    // return nlohmann::ordered_json here: pybind11_json registers a caster for
    // nlohmann::json (std::map) but none for ordered_json (ordered_map), so any
    // ordered_json return value is unconvertible to a Python type and raises on
    // every call. Let bad input propagate as a real Python exception (pybind11
    // translates std::exception → RuntimeError) instead of returning an in-band
    // error value that the caller would write out as if it were a valid netlist.
    //
    // Use the NGSPICE exporter (not the default SIMBA model, which emits Simba
    // component JSON): consumers of this binding need a real ".subckt ... .ends"
    // SPICE subcircuit (e.g. the MAS MKF_MODEL path stamps it into
    // magnetic.modelOutputs.spiceSubcircuit).
    OpenMagnetics::Magnetic magnetic(magneticJson);
    return OpenMagnetics::CircuitSimulatorExporter(OpenMagnetics::CircuitSimulatorExporterModels::NGSPICE)
        .export_magnetic_as_subcircuit(magnetic);
}

json mas_autocomplete(json masJson, json configuration) {
    try {
        OpenMagnetics::Mas mas(masJson);
        auto completedMas = OpenMagnetics::mas_autocomplete(mas, configuration);
        json result;
        to_json(result, completedMas);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json magnetic_autocomplete(json magneticJson, json configuration) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto completedMagnetic = OpenMagnetics::magnetic_autocomplete(magnetic, configuration);
        json result;
        to_json(result, completedMagnetic);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json process_inputs(json inputsJson) {
    try {
        OpenMagnetics::Inputs inputs(inputsJson);
        auto operatingPoints = inputs.get_mutable_operating_points();
        for (size_t operatingPointIndex = 0; operatingPointIndex < operatingPoints.size(); ++operatingPointIndex) {
            auto excitationsPerWinding = operatingPoints[operatingPointIndex].get_excitations_per_winding();
            for (size_t excitationIndex = 0; excitationIndex < excitationsPerWinding.size(); ++excitationIndex) {
                auto excitation = operatingPoints[operatingPointIndex].get_mutable_excitations_per_winding()[excitationIndex];
                if (excitation.get_current()) {
                    auto current = excitation.get_current().value();
                    if (!current.get_processed() && current.get_waveform()) {
                        auto processed = OpenMagnetics::Inputs::calculate_basic_processed_data(current.get_waveform().value());
                        current.set_processed(processed);
                    }
                    if (!current.get_harmonics() && current.get_waveform()) {
                        auto harmonics = OpenMagnetics::Inputs::calculate_harmonics_data(current.get_waveform().value(), excitation.get_frequency());
                        current.set_harmonics(harmonics);
                    }
                    if (!current.get_waveform() && current.get_processed()) {
                        auto waveform = OpenMagnetics::Inputs::create_waveform(current.get_processed().value(), excitation.get_frequency());
                        current.set_waveform(waveform);
                    }
                    excitation.set_current(current);
                }
                if (excitation.get_voltage()) {
                    auto voltage = excitation.get_voltage().value();
                    if (!voltage.get_processed() && voltage.get_waveform()) {
                        auto processed = OpenMagnetics::Inputs::calculate_basic_processed_data(voltage.get_waveform().value());
                        voltage.set_processed(processed);
                    }
                    if (!voltage.get_harmonics() && voltage.get_waveform()) {
                        auto harmonics = OpenMagnetics::Inputs::calculate_harmonics_data(voltage.get_waveform().value(), excitation.get_frequency());
                        voltage.set_harmonics(harmonics);
                    }
                    if (!voltage.get_waveform() && voltage.get_processed()) {
                        auto waveform = OpenMagnetics::Inputs::create_waveform(voltage.get_processed().value(), excitation.get_frequency());
                        voltage.set_waveform(waveform);
                    }
                    excitation.set_voltage(voltage);
                }
                operatingPoints[operatingPointIndex].get_mutable_excitations_per_winding()[excitationIndex] = excitation;
            }
            inputs.get_mutable_operating_points()[operatingPointIndex] = operatingPoints[operatingPointIndex];
        }
        json result;
        to_json(result, inputs);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json extract_operating_point(json fileJson, size_t numberWindings, double frequency, double desiredMagnetizingInductance, json mapColumnNamesJson) {
    try {
        std::vector<std::map<std::string, std::string>> mapColumnNames = mapColumnNamesJson.get<std::vector<std::map<std::string, std::string>>>();
        auto reader = OpenMagnetics::CircuitSimulationReader(fileJson);
        auto operatingPoint = reader.extract_operating_point(numberWindings, frequency, mapColumnNames);
        operatingPoint = OpenMagnetics::Inputs::process_operating_point(operatingPoint, desiredMagnetizingInductance);
        json result;
        to_json(result, operatingPoint);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json extract_map_column_names(json fileJson, size_t numberWindings, double frequency) {
    try {
        auto reader = OpenMagnetics::CircuitSimulationReader(fileJson);
        auto columnNames = reader.extract_map_column_names(numberWindings, frequency);
        json result = json::array();
        for (auto& columnName : columnNames) {
            json aux;
            for (auto& [signal, name] : columnName) {
                aux[signal] = name;
            }
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

json extract_column_names(json fileJson) {
    try {
        auto reader = OpenMagnetics::CircuitSimulationReader(fileJson);
        auto columnNames = reader.extract_column_names();
        json result = json::array();
        for (auto& columnName : columnNames) {
            result.push_back(columnName);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_inductance_matrix(json magneticJson, double frequency, json modelsData) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        
        auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
        if (!modelsData.is_null() && modelsData.find("reluctance") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["reluctance"], reluctanceModelName);
        }

        OpenMagnetics::Inductance inductance(reluctanceModelName);
        auto inductanceMatrix = inductance.calculate_inductance_matrix(magnetic, frequency);

        json result;
        to_json(result, inductanceMatrix);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_leakage_inductance(json magneticJson, double frequency, size_t sourceIndex) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        auto leakageInductanceOutput = OpenMagnetics::LeakageInductance().calculate_leakage_inductance_all_windings(magnetic, frequency, sourceIndex);

        json result;
        to_json(result, leakageInductanceOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_dc_resistance_per_winding(json coilJson, double temperature) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        
        auto resistances = OpenMagnetics::WindingOhmicLosses::calculate_dc_resistance_per_winding(coil, temperature);

        json result = resistances;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_resistance_matrix(json magneticJson, double temperature, double frequency) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        
        OpenMagnetics::WindingLosses windingLosses;
        auto resistanceMatrix = windingLosses.calculate_resistance_matrix(magnetic, temperature, frequency);

        json result;
        to_json(result, resistanceMatrix);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_stray_capacitance(json coilJson, json operatingPointJson, json modelsData) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        OperatingPoint operatingPoint(operatingPointJson);
        
        auto strayCapacitanceModelName = OpenMagnetics::StrayCapacitanceModels::ALBACH;
        if (!modelsData.is_null() && modelsData.find("strayCapacitance") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["strayCapacitance"], strayCapacitanceModelName);
        }

        OpenMagnetics::StrayCapacitance strayCapacitance(strayCapacitanceModelName);
        auto strayCapacitanceOutput = strayCapacitance.calculate_capacitance(coil);

        json result;
        to_json(result, strayCapacitanceOutput);
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_maxwell_capacitance_matrix(json coilJson, json capacitanceAmongWindingsJson) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);
        auto capacitanceAmongWindings = capacitanceAmongWindingsJson.get<std::map<std::string, std::map<std::string, double>>>();

        auto maxwellMatrix = OpenMagnetics::StrayCapacitance::calculate_maxwell_capacitance_matrix(coil, capacitanceAmongWindings);

        json result = json::array();
        for (const auto& matrix : maxwellMatrix) {
            json matrixJson;
            to_json(matrixJson, matrix);
            result.push_back(matrixJson);
        }
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_impedance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_impedance_over_frequency(magnetic, start, stop, numberElements, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_common_mode_impedance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_common_mode_impedance_over_frequency(magnetic, start, stop, numberElements, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_differential_mode_impedance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_differential_mode_impedance_over_frequency(magnetic, start, stop, numberElements, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_q_factor_over_frequency(json magneticJson, double start, double stop, size_t numberElements, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_q_factor_over_frequency(magnetic, start, stop, numberElements, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_winding_resistance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, size_t windingIndex, double temperature, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_winding_resistance_over_frequency(magnetic, start, stop, numberElements, windingIndex, temperature, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_resistance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_resistance_over_frequency(magnetic, start, stop, numberElements, temperature, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_magnetizing_inductance_over_frequency(json magneticJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_magnetizing_inductance_over_frequency(magnetic, start, stop, numberElements, temperature, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_magnetizing_inductance_over_temperature(json magneticJson, double start, double stop, size_t numberElements, double frequency, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_magnetizing_inductance_over_temperature(magnetic, start, stop, numberElements, frequency, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_magnetizing_inductance_over_dc_bias(json magneticJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        auto result = OpenMagnetics::Sweeper::sweep_magnetizing_inductance_over_dc_bias(magnetic, start, stop, numberElements, temperature, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_core_losses_over_frequency(json magneticJson, json operatingPointJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);
        auto result = OpenMagnetics::Sweeper::sweep_core_losses_over_frequency(magnetic, operatingPoint, start, stop, numberElements, temperature, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json sweep_winding_losses_over_frequency(json magneticJson, json operatingPointJson, double start, double stop, size_t numberElements, double temperature, std::string mode, std::string title) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);
        auto result = OpenMagnetics::Sweeper::sweep_winding_losses_over_frequency(magnetic, operatingPoint, start, stop, numberElements, temperature, mode, title);
        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_coupling_coefficient_matrix(json magneticJson, double frequency, json modelsData) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
        if (!modelsData.is_null() && modelsData.find("reluctance") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["reluctance"], reluctanceModelName);
        }

        OpenMagnetics::Inductance inductance(reluctanceModelName);

        auto& functionalDescription = magnetic.get_coil().get_functional_description();
        size_t numWindings = functionalDescription.size();

        ScalarMatrixAtFrequency result;
        result.set_frequency(frequency);

        std::map<std::string, std::map<std::string, DimensionWithTolerance>> magnitude;

        for (size_t i = 0; i < numWindings; ++i) {
            std::string windingName_i = functionalDescription[i].get_name();

            for (size_t j = 0; j < numWindings; ++j) {
                std::string windingName_j = functionalDescription[j].get_name();

                double k = inductance.calculate_coupling_coefficient(magnetic, i, j, frequency);

                DimensionWithTolerance dimValue;
                dimValue.set_nominal(k);
                magnitude[windingName_i][windingName_j] = dimValue;
            }
        }

        result.set_magnitude(magnitude);

        json resultJson;
        to_json(resultJson, result);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_leakage_inductance_matrix(json magneticJson, double frequency, json modelsData) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        auto reluctanceModelName = OpenMagnetics::defaults.reluctanceModelDefault;
        if (!modelsData.is_null() && modelsData.find("reluctance") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["reluctance"], reluctanceModelName);
        }

        OpenMagnetics::Inductance inductance(reluctanceModelName);
        auto leakageInductanceMatrix = inductance.calculate_leakage_inductance_matrix(magnetic, frequency);

        json resultJson;
        to_json(resultJson, leakageInductanceMatrix);
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_capacitance_matrix(json coilJson, json modelsData) {
    try {
        OpenMagnetics::Coil coil(coilJson, false);

        auto strayCapacitanceModelName = OpenMagnetics::StrayCapacitanceModels::ALBACH;
        if (!modelsData.is_null() && modelsData.find("strayCapacitance") != modelsData.end()) {
            OpenMagnetics::from_json(modelsData["strayCapacitance"], strayCapacitanceModelName);
        }

        OpenMagnetics::StrayCapacitance strayCapacitance(strayCapacitanceModelName);
        auto strayCapacitanceOutput = strayCapacitance.calculate_capacitance(coil);

        json resultJson;
        if (strayCapacitanceOutput.get_capacitance_matrix()) {
            auto capacitanceMatrix = strayCapacitanceOutput.get_capacitance_matrix().value();
            for (const auto& [outerKey, innerMap] : capacitanceMatrix) {
                resultJson[outerKey] = json();
                for (const auto& [innerKey, scalarMatrix] : innerMap) {
                    json matrixJson;
                    to_json(matrixJson, scalarMatrix);
                    resultJson[outerKey][innerKey] = matrixJson;
                }
            }
        }

        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json calculate_capacitance_models_between_windings(double /*energy*/, double /*voltageDrop*/, double /*relativeTurnsRatio*/) {
    // Removed from MKF: OpenMagnetics::StrayCapacitance no longer exposes the six-capacitor /
    // tripole model helper (dropped in the same MKF cleanup as the converter externalisation;
    // WebLibMKF dropped this binding too). Kept as a stub so the API surface stays stable.
    return json{{"error", "calculate_capacitance_models_between_windings: removed from MKF "
                          "(StrayCapacitance no longer provides the six-capacitor / tripole model)."}};
}

json export_magnetic_as_symbol(json magneticJson, json inputsJson) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OpenMagnetics::Inputs inputs(inputsJson);
        auto result = OpenMagnetics::CircuitSimulatorExporter().export_magnetic_as_symbol(magnetic);
        json resultJson;
        resultJson["data"] = result;
        return resultJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

void register_simulation_bindings(py::module& m) {
    m.def("simulate", &simulate,
        R"pbdoc(
        Run a complete magnetic simulation for given operating conditions.
        
        Performs electromagnetic simulation including inductance calculation,
        field distribution, and performance metrics.
        
        Args:
            magnetic_json: JSON object containing magnetic component specification.
            inputs_json: JSON object containing operating points and conditions.
            models_json: JSON object specifying which models to use for simulation.
        
        Returns:
            JSON object with simulation results including outputs.
        )pbdoc");
    
    m.def("export_magnetic_as_subcircuit", &export_magnetic_as_subcircuit,
        R"pbdoc(
        Export a magnetic component as a SPICE-compatible subcircuit.
        
        Generates subcircuit netlist representation for circuit simulation.
        
        Args:
            magnetic_json: JSON object containing magnetic component specification.
            subcircuit_type: Type of subcircuit model to generate.
        
        Returns:
            String containing the subcircuit definition.
        )pbdoc");
    
    m.def("mas_autocomplete", &mas_autocomplete,
        R"pbdoc(
        Autocomplete a partial Mas (Magnetic Assembly Specification) structure.
        
        Fills in missing fields and calculates derived values.
        
        Args:
            mas_json: Partial Mas JSON object to complete.
        
        Returns:
            Complete Mas JSON object with all fields populated.
        )pbdoc");
    
    m.def("magnetic_autocomplete", &magnetic_autocomplete,
        R"pbdoc(
        Autocomplete a partial Magnetic component specification.
        
        Fills in missing fields and calculates derived values for core and coil.
        
        Args:
            magnetic_json: Partial Magnetic JSON object to complete.
        
        Returns:
            Complete Magnetic JSON object with all fields populated.
        )pbdoc");
    
    m.def("process_inputs", &process_inputs,
        R"pbdoc(
        Process raw input data and calculate derived quantities.
        
        Calculates harmonics, processed waveform data, and validates inputs.
        This should be called before using inputs with adviser functions.
        
        Args:
            inputs_json: Raw input JSON object with operating points.
        
        Returns:
            ProcessedWaveform inputs JSON with calculated harmonics and processed data.
        )pbdoc");
    
    m.def("extract_operating_point", &extract_operating_point,
        R"pbdoc(
        Extract operating point from circuit simulation data.
        
        Parses circuit simulation output file and extracts waveforms.
        
        Args:
            file_json: JSON object with simulation file data.
            number_windings: Number of windings in the magnetic.
            frequency: Operating frequency in Hz.
            desired_magnetizing_inductance: Target inductance value.
            map_column_names_json: Mapping of column names to signals.
        
        Returns:
            JSON object representing the extracted operating point.
        )pbdoc");
    
    m.def("extract_map_column_names", &extract_map_column_names,
        R"pbdoc(
        Extract column name mapping from circuit simulation file.
        
        Analyzes simulation file to determine which columns correspond
        to voltage and current signals for each winding.
        
        Args:
            file_json: JSON object with simulation file data.
            number_windings: Number of windings to map.
            frequency: Operating frequency for signal identification.
        
        Returns:
            JSON array mapping signal types to column names.
        )pbdoc");
    
    m.def("extract_column_names", &extract_column_names,
        R"pbdoc(
        Extract all column names from a circuit simulation file.
        
        Args:
            file_json: JSON object with simulation file data.
        
        Returns:
            JSON array of column name strings.
        )pbdoc");
    
    m.def("calculate_inductance_matrix", &calculate_inductance_matrix,
        R"pbdoc(
        Calculate the complete inductance matrix for a magnetic component.
        
        Computes the inductance matrix at the specified frequency, including
        self inductances (diagonal elements) and mutual inductances (off-diagonal).
        
        Args:
            magnetic_json: JSON object containing magnetic component specification.
            frequency: Operating frequency in Hz.
            models_json: JSON object specifying which models to use (e.g., reluctance model).
        
        Returns:
            JSON object with the inductance matrix at the specified frequency.
        )pbdoc");
    
    m.def("calculate_leakage_inductance", &calculate_leakage_inductance,
        R"pbdoc(
        Calculate leakage inductance between windings.
        
        Computes the leakage inductance from a source winding to all other windings.
        
        Args:
            magnetic_json: JSON object containing magnetic component specification.
            frequency: Operating frequency in Hz.
            source_index: Index of the source winding (0-based).
        
        Returns:
            JSON object with leakage inductance values to each winding.
        )pbdoc");
    
    m.def("calculate_dc_resistance_per_winding", &calculate_dc_resistance_per_winding,
        R"pbdoc(
        Calculate DC resistance for each winding.
        
        Computes the DC resistance of each winding based on wire properties
        and temperature.
        
        Args:
            coil_json: JSON object containing coil specification with turns and wire info.
            temperature: Temperature in degrees Celsius for resistance calculation.
        
        Returns:
            JSON array with DC resistance value for each winding in Ohms.
        )pbdoc");
    
    m.def("calculate_resistance_matrix", &calculate_resistance_matrix,
        R"pbdoc(
        Calculate the resistance matrix for a magnetic component.
        
        Computes the frequency-dependent resistance matrix including self and mutual
        resistances. Uses the Spreen (1990) method with inductance ratio scaling
        for proper mutual resistance calculation.
        
        Args:
            magnetic_json: JSON object containing magnetic component specification.
            temperature: Temperature in degrees Celsius for resistance calculation.
            frequency: Operating frequency in Hz.
        
        Returns:
            JSON object with resistance matrix (magnitude and frequency).
        )pbdoc");
    
    m.def("calculate_stray_capacitance", &calculate_stray_capacitance,
        R"pbdoc(
        Calculate stray capacitance for a coil.
        
        Computes turn-to-turn and winding-to-winding capacitances using the
        specified capacitance model.
        
        Args:
            coil_json: JSON object containing coil specification with turns.
            operating_point_json: JSON object with operating conditions for voltage distribution.
            models_json: JSON object specifying capacitance model (e.g., "Albach", "Koch").
        
        Returns:
            JSON object with capacitance values including capacitance among turns,
            capacitance among windings, and Maxwell capacitance matrix.
        )pbdoc");
    
    m.def("calculate_maxwell_capacitance_matrix", &calculate_maxwell_capacitance_matrix,
        R"pbdoc(
        Calculate Maxwell capacitance matrix from inter-winding capacitances.

        Converts inter-winding capacitance values to the standard Maxwell
        capacitance matrix format used in circuit simulation.

        Args:
            coil_json: JSON object containing coil specification.
            capacitance_among_windings_json: JSON object with capacitance values
                between each pair of windings.

        Returns:
            JSON array containing the Maxwell capacitance matrix.
        )pbdoc");

    m.def("sweep_impedance_over_frequency", &sweep_impedance_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep impedance over a frequency range.");

    m.def("sweep_common_mode_impedance_over_frequency", &sweep_common_mode_impedance_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep common-mode impedance (all windings driven in parallel — the CMC datasheet CM measurement; magnetizing tank only, no leakage resonance) over a frequency range.");

    m.def("sweep_differential_mode_impedance_over_frequency", &sweep_differential_mode_impedance_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep differential-mode impedance (leakage + winding R + inter-winding C) over a frequency range.");

    m.def("sweep_q_factor_over_frequency", &sweep_q_factor_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep Q factor over a frequency range.");

    m.def("sweep_winding_resistance_over_frequency", &sweep_winding_resistance_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("winding_index"),
        py::arg("temperature"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep winding resistance over a frequency range.");

    m.def("sweep_resistance_over_frequency", &sweep_resistance_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("temperature"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep total resistance over a frequency range.");

    m.def("sweep_magnetizing_inductance_over_frequency", &sweep_magnetizing_inductance_over_frequency,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("temperature"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep magnetizing inductance over a frequency range.");

    m.def("sweep_magnetizing_inductance_over_temperature", &sweep_magnetizing_inductance_over_temperature,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("frequency"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep magnetizing inductance over a temperature range.");

    m.def("sweep_magnetizing_inductance_over_dc_bias", &sweep_magnetizing_inductance_over_dc_bias,
        py::arg("magnetic_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("temperature"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep magnetizing inductance over DC bias current.");

    m.def("sweep_core_losses_over_frequency", &sweep_core_losses_over_frequency,
        py::arg("magnetic_json"),
        py::arg("operating_point_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("temperature"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep core losses over a frequency range.");

    m.def("sweep_winding_losses_over_frequency", &sweep_winding_losses_over_frequency,
        py::arg("magnetic_json"),
        py::arg("operating_point_json"),
        py::arg("start"),
        py::arg("stop"),
        py::arg("number_elements"),
        py::arg("temperature"),
        py::arg("mode"),
        py::arg("title"),
        "Sweep winding losses over a frequency range.");

    m.def("calculate_coupling_coefficient_matrix", &calculate_coupling_coefficient_matrix,
        py::arg("magnetic_json"),
        py::arg("frequency"),
        py::arg("models_data"),
        "Calculate the coupling coefficient matrix for a magnetic component.");

    m.def("calculate_leakage_inductance_matrix", &calculate_leakage_inductance_matrix,
        py::arg("magnetic_json"),
        py::arg("frequency"),
        py::arg("models_data"),
        "Calculate the leakage inductance matrix for a magnetic component.");

    m.def("calculate_capacitance_matrix", &calculate_capacitance_matrix,
        py::arg("coil_json"),
        py::arg("models_data"),
        "Calculate the capacitance matrix for a coil.");

    m.def("calculate_capacitance_models_between_windings", &calculate_capacitance_models_between_windings,
        py::arg("energy"),
        py::arg("voltage_drop"),
        py::arg("relative_turns_ratio"),
        "Calculate six-capacitor and tripole capacitance models between windings.");

    m.def("export_magnetic_as_symbol", &export_magnetic_as_symbol,
        py::arg("magnetic_json"),
        py::arg("inputs_json"),
        "Export a magnetic component as a circuit simulator symbol.");
}

} // namespace PyMKF
