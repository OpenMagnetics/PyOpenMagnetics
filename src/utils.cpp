#include "utils.h"

namespace PyMKF {

double resolve_dimension_with_tolerance(json dimensionWithToleranceJson, std::string preferredValue) {
    DimensionWithTolerance dimensionWithTolerance(dimensionWithToleranceJson);
    OpenMagnetics::DimensionalValues preferred = json(preferredValue).get<OpenMagnetics::DimensionalValues>();
    return OpenMagnetics::resolve_dimensional_values(dimensionWithTolerance, preferred);
}

json calculate_basic_processed_data(json waveformJson) {
    Waveform waveform(waveformJson);
    auto processed = OpenMagnetics::Inputs::calculate_basic_processed_data(waveform);
    json result;
    to_json(result, processed);
    return result;
}

json calculate_harmonics(json waveformJson, double frequency) {
    Waveform waveform(waveformJson);
    auto sampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(waveform, frequency);
    auto harmonics = OpenMagnetics::Inputs::calculate_harmonics_data(sampledWaveform, frequency);
    json result;
    to_json(result, harmonics);
    return result;
}

json calculate_sampled_waveform(json waveformJson, double frequency) {
    Waveform waveform(waveformJson);
    auto sampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(waveform, frequency);
    json result;
    to_json(result, sampledWaveform);
    return result;
}

json calculate_processed_data(json signalDescriptorJson, json sampledWaveformJson, bool includeDcComponent) {
    SignalDescriptor signalDescriptor(signalDescriptorJson);
    Waveform sampledWaveform(sampledWaveformJson);
    auto processed = OpenMagnetics::Inputs::calculate_processed_data(signalDescriptor, sampledWaveform, includeDcComponent);
    json result;
    to_json(result, processed);
    return result;
}

double calculate_instantaneous_power(json excitationJson) {
    OperatingPointExcitation excitation(excitationJson);

    if (!excitation.get_current().value().get_processed().value().get_rms().value()) {
        auto current = excitation.get_current().value();
        auto processed = OpenMagnetics::Inputs::calculate_processed_data(current.get_harmonics().value(), current.get_waveform().value(), true);
        current.set_processed(processed);
        excitation.set_current(current);
    }
    if (!excitation.get_voltage().value().get_processed().value().get_rms().value()) {
        auto voltage = excitation.get_voltage().value();
        auto processed = OpenMagnetics::Inputs::calculate_processed_data(voltage.get_harmonics().value(), voltage.get_waveform().value(), true);
        voltage.set_processed(processed);
        excitation.set_voltage(voltage);
    }

    auto instantaneousPower = OpenMagnetics::Inputs::calculate_instantaneous_power(excitation);
    return instantaneousPower;
}

double calculate_rms_power(json excitationJson) {
    OperatingPointExcitation excitation(excitationJson);

    auto voltageSignalDescriptor = excitation.get_voltage().value();
    auto currentSignalDescriptor = excitation.get_current().value();

    if (!voltageSignalDescriptor.get_processed() || !voltageSignalDescriptor.get_processed()->get_rms()) {
        auto voltageSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(voltageSignalDescriptor.get_waveform().value(), excitation.get_frequency());
        voltageSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(voltageSampledWaveform, excitation.get_frequency()));
        voltageSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(voltageSignalDescriptor, voltageSampledWaveform, true));
    }

    if (!currentSignalDescriptor.get_processed() || !currentSignalDescriptor.get_processed()->get_rms()) {
        auto currentSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(currentSignalDescriptor.get_waveform().value(), excitation.get_frequency());
        currentSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(currentSampledWaveform, excitation.get_frequency()));
        currentSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(currentSignalDescriptor, currentSampledWaveform, true));
    }

    double rmsPower = currentSignalDescriptor.get_processed().value().get_rms().value() * voltageSignalDescriptor.get_processed().value().get_rms().value();
    return rmsPower;
}

json calculate_reflected_secondary(json primaryExcitationJson, double turnRatio) {
    OperatingPointExcitation primaryExcitation(primaryExcitationJson);

    OperatingPointExcitation excitationOfThisWinding(primaryExcitation);
    auto voltageSignalDescriptor = OpenMagnetics::Inputs::reflect_waveform(primaryExcitation.get_voltage().value(), 1.0 / turnRatio);
    
    auto voltageSignalDescriptorProcessed = voltageSignalDescriptor.get_processed();
    if (!voltageSignalDescriptorProcessed) {
        auto voltageSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(voltageSignalDescriptor.get_waveform().value(), excitationOfThisWinding.get_frequency());
        voltageSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(voltageSampledWaveform, excitationOfThisWinding.get_frequency()));
        voltageSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(voltageSignalDescriptor, voltageSampledWaveform, true));
    }

    auto currentSignalDescriptorProcessed = primaryExcitation.get_current().value().get_processed();
    if (!currentSignalDescriptorProcessed) {
        auto currentSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(primaryExcitation.get_current().value().get_waveform().value(), excitationOfThisWinding.get_frequency());
        auto currentSignalDescriptor = primaryExcitation.get_current().value();
        currentSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(currentSampledWaveform, excitationOfThisWinding.get_frequency()));
        currentSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(currentSignalDescriptor, currentSampledWaveform, true));
        primaryExcitation.set_current(currentSignalDescriptor);
        currentSignalDescriptorProcessed = currentSignalDescriptor.get_processed();
    }

    auto currentSignalDescriptor = OpenMagnetics::Inputs::reflect_waveform(primaryExcitation.get_current().value(), turnRatio, currentSignalDescriptorProcessed.value().get_label());

    auto voltageSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(voltageSignalDescriptor.get_waveform().value(), excitationOfThisWinding.get_frequency());
    voltageSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(voltageSampledWaveform, excitationOfThisWinding.get_frequency()));
    voltageSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(voltageSignalDescriptor, voltageSampledWaveform, true));

    auto currentSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(currentSignalDescriptor.get_waveform().value(), excitationOfThisWinding.get_frequency());
    currentSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(currentSampledWaveform, excitationOfThisWinding.get_frequency()));
    currentSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(currentSignalDescriptor, currentSampledWaveform, true));

    excitationOfThisWinding.set_voltage(voltageSignalDescriptor);
    excitationOfThisWinding.set_current(currentSignalDescriptor);

    json result;
    to_json(result, excitationOfThisWinding);
    return result;
}

json calculate_reflected_primary(json secondaryExcitationJson, double turnRatio) {
    OperatingPointExcitation secondaryExcitation(secondaryExcitationJson);

    OperatingPointExcitation excitationOfThisWinding(secondaryExcitation);
    auto voltageSignalDescriptor = OpenMagnetics::Inputs::reflect_waveform(secondaryExcitation.get_voltage().value(), turnRatio);
    auto currentSignalDescriptor = OpenMagnetics::Inputs::reflect_waveform(secondaryExcitation.get_current().value(), 1.0 / turnRatio);

    auto voltageSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(voltageSignalDescriptor.get_waveform().value(), excitationOfThisWinding.get_frequency());
    voltageSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(voltageSampledWaveform, excitationOfThisWinding.get_frequency()));
    voltageSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(voltageSignalDescriptor, voltageSampledWaveform, true));

    auto currentSampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(currentSignalDescriptor.get_waveform().value(), excitationOfThisWinding.get_frequency());
    currentSignalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(currentSampledWaveform, excitationOfThisWinding.get_frequency()));
    currentSignalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(currentSignalDescriptor, currentSampledWaveform, true));

    excitationOfThisWinding.set_voltage(voltageSignalDescriptor);
    excitationOfThisWinding.set_current(currentSignalDescriptor);

    json result;
    to_json(result, excitationOfThisWinding);
    return result;
}

py::list list_of_list_to_python_list(std::vector<std::vector<double>> arrayOfArrays) {
    py::list outerList;
    for (const auto& innerArray : arrayOfArrays) {
        py::list innerList;
        for (double value : innerArray) {
            innerList.append(value);
        }
        outerList.append(innerList);
    }
    return outerList;
}

std::vector<double> python_list_to_vector(py::list pythonList) {
    std::vector<double> result;
    for (py::handle item : pythonList) {
        result.push_back(item.cast<double>());
    }
    return result;
}

json standardize_signal_descriptor(json signalDescriptorJson, double frequency) {
    SignalDescriptor signalDescriptor(signalDescriptorJson);
    signalDescriptor = OpenMagnetics::Inputs::standardize_waveform(signalDescriptor, frequency);
    auto sampledWaveform = OpenMagnetics::Inputs::calculate_sampled_waveform(signalDescriptor.get_waveform().value(), frequency);
    signalDescriptor.set_harmonics(OpenMagnetics::Inputs::calculate_harmonics_data(sampledWaveform, frequency));
    signalDescriptor.set_processed(OpenMagnetics::Inputs::calculate_processed_data(signalDescriptor, sampledWaveform, true));
    json result;
    to_json(result, signalDescriptor);
    return result;
}

json create_waveform(json processedJson, double frequency) {
    ProcessedWaveform processed(processedJson);
    auto waveform = OpenMagnetics::Inputs::create_waveform(processed, frequency);
    json result;
    to_json(result, waveform);
    return result;
}

json calculate_processed(json harmonicsJson, json waveformJson) {
    Harmonics harmonics(harmonicsJson);
    Waveform waveform(waveformJson);
    auto processed = OpenMagnetics::Inputs::calculate_processed_data(harmonics, waveform, true);
    json result;
    to_json(result, processed);
    return result;
}

json scale_waveform_time_to_frequency(json waveformJson, double newFrequency) {
    Waveform waveform(waveformJson);
    auto scaled = OpenMagnetics::Inputs::scale_time_to_frequency(waveform, newFrequency);
    json result;
    to_json(result, scaled);
    return result;
}

json scale_excitation_time_to_frequency(json excitationJson, double newFrequency) {
    OperatingPointExcitation excitation(excitationJson);
    OpenMagnetics::Inputs::scale_time_to_frequency(excitation, newFrequency, false, true);
    json result;
    to_json(result, excitation);
    return result;
}

json calculate_induced_voltage(json excitationJson, double magnetizingInductance) {
    OperatingPointExcitation excitation(excitationJson);
    auto voltage = OpenMagnetics::Inputs::calculate_induced_voltage(excitation, magnetizingInductance);
    json result;
    to_json(result, voltage);
    return result;
}

json calculate_induced_current(json excitationJson, double magnetizingInductance) {
    OperatingPointExcitation excitation(excitationJson);
    auto current = OpenMagnetics::Inputs::calculate_magnetizing_current(excitation, magnetizingInductance, true, 0.0);

    if (excitation.get_voltage() && excitation.get_voltage()->get_processed() && excitation.get_voltage()->get_processed()->get_duty_cycle()) {
        auto processed = current.get_processed().value();
        processed.set_duty_cycle(excitation.get_voltage()->get_processed()->get_duty_cycle().value());
        current.set_processed(processed);
    }

    json result;
    to_json(result, current);
    return result;
}

bool check_requirement(json requirementJson, double value) {
    DimensionWithTolerance requirement(requirementJson);
    return OpenMagnetics::check_requirement(requirement, value);
}

json get_main_harmonic_indexes(json harmonicsJson, double threshold, int mainHarmonicIndex) {
    Harmonics harmonics(harmonicsJson);
    auto indexes = OpenMagnetics::get_main_harmonic_indexes(harmonics, threshold, static_cast<size_t>(mainHarmonicIndex));
    json result = json::array();
    for (auto idx : indexes) {
        result.push_back(idx);
    }
    return result;
}

json get_excitation_harmonic_indexes(json excitationJson, double threshold) {
    OperatingPointExcitation excitation(excitationJson);
    auto indexes = OpenMagnetics::get_main_harmonic_indexes(excitation, threshold);
    json result = json::array();
    for (auto idx : indexes) {
        result.push_back(idx);
    }
    return result;
}

void register_utils_bindings(py::module& m) {
    m.def("resolve_dimension_with_tolerance", &resolve_dimension_with_tolerance,
        R"pbdoc(
        Resolve a dimension specification that may include tolerances.

        Extracts a single value from dimension data that may contain
        nominal, minimum, and maximum values.

        Args:
            dimension_json: JSON object with dimension specification.
            preferred: Which value to prefer when present — "Nominal" (default),
                "Maximum", or "Minimum".

        Returns:
            Resolved dimension value as float.
        )pbdoc",
        py::arg("dimensionWithToleranceJson"), py::arg("preferredValue") = "Nominal");
    
    m.def("calculate_basic_processed_data", &calculate_basic_processed_data,
        R"pbdoc(
        Calculate basic processed data from a waveform.
        
        Extracts peak-to-peak, RMS, offset, and other basic metrics.
        
        Args:
            waveform_json: JSON object with waveform data and time points.
        
        Returns:
            JSON object with processed waveform characteristics.
        )pbdoc");
    
    m.def("calculate_harmonics", &calculate_harmonics,
        R"pbdoc(
        Calculate harmonic content of a waveform.
        
        Performs FFT analysis to extract harmonic amplitudes and phases.
        
        Args:
            waveform_json: JSON object with waveform data.
            frequency: Fundamental frequency in Hz.
        
        Returns:
            JSON object with harmonic amplitudes and frequencies.
        )pbdoc");
    
    m.def("calculate_sampled_waveform", &calculate_sampled_waveform,
        R"pbdoc(
        Resample a waveform at regular intervals.
        
        Interpolates waveform data to create uniformly sampled points.
        
        Args:
            waveform_json: JSON object with waveform data.
            frequency: Frequency for determining sample period.
        
        Returns:
            JSON object with uniformly sampled waveform.
        )pbdoc");
    
    m.def("calculate_processed_data", &calculate_processed_data,
        R"pbdoc(
        Calculate complete processed data from a signal descriptor.
        
        Computes RMS, peak, offset, effective frequency, and other metrics.
        
        Args:
            signal_descriptor_json: JSON object with signal data.
            sampled_waveform_json: JSON object with sampled waveform.
            include_dc_component: Whether to include DC in calculations.
        
        Returns:
            JSON object with complete processed data.
        )pbdoc",
        py::arg("signalDescriptorJson"), py::arg("sampledWaveformJson"), py::arg("includeDcComponent"));
    
    m.def("calculate_instantaneous_power", &calculate_instantaneous_power,
        R"pbdoc(
        Calculate instantaneous power waveform.
        
        Multiplies voltage and current waveforms point-by-point.
        
        Args:
            voltage_json: JSON object with voltage waveform.
            current_json: JSON object with current waveform.
            frequency: Operating frequency in Hz.
        
        Returns:
            JSON array of instantaneous power values.
        )pbdoc");
    
    m.def("calculate_rms_power", &calculate_rms_power,
        R"pbdoc(
        Calculate RMS (apparent) power.
        
        Computes product of RMS voltage and RMS current.
        
        Args:
            voltage_json: JSON object with voltage signal descriptor.
            current_json: JSON object with current signal descriptor.
            frequency: Operating frequency in Hz.
        
        Returns:
            RMS power value in watts.
        )pbdoc");
    
    m.def("calculate_reflected_secondary", &calculate_reflected_secondary,
        R"pbdoc(
        Calculate reflected secondary winding excitation.
        
        Transforms primary winding excitation to secondary side
        using the turns ratio.
        
        Args:
            primary_excitation_json: JSON object with primary excitation.
            turn_ratio: Primary to secondary turns ratio.
        
        Returns:
            JSON object with secondary excitation.
        )pbdoc");
    
    m.def("calculate_reflected_primary", &calculate_reflected_primary,
        R"pbdoc(
        Calculate reflected primary winding excitation.

        Transforms secondary winding excitation to primary side
        using the turns ratio.

        Args:
            secondary_excitation_json: JSON object with secondary excitation.
            turn_ratio: Primary to secondary turns ratio.

        Returns:
            JSON object with primary excitation.
        )pbdoc");

    m.def("standardize_signal_descriptor", &standardize_signal_descriptor,
        R"pbdoc(
        Standardize a signal descriptor by computing waveform, harmonics, and processed data.

        Args:
            signal_descriptor_json: JSON SignalDescriptor object.
            frequency: Operating frequency in Hz.

        Returns:
            JSON SignalDescriptor with all fields populated.
        )pbdoc",
        py::arg("signalDescriptorJson"), py::arg("frequency"));

    m.def("create_waveform", &create_waveform,
        R"pbdoc(
        Create a waveform from processed data.

        Args:
            processed_json: JSON ProcessedWaveform object with waveform parameters.
            frequency: Operating frequency in Hz.

        Returns:
            JSON Waveform object.
        )pbdoc",
        py::arg("processedJson"), py::arg("frequency"));

    m.def("calculate_processed", &calculate_processed,
        R"pbdoc(
        Calculate processed data from harmonics and waveform.

        Args:
            harmonics_json: JSON Harmonics object.
            waveform_json: JSON Waveform object.

        Returns:
            JSON ProcessedWaveform object with RMS, peak, offset, etc.
        )pbdoc",
        py::arg("harmonicsJson"), py::arg("waveformJson"));

    m.def("scale_waveform_time_to_frequency", &scale_waveform_time_to_frequency,
        R"pbdoc(
        Scale waveform time axis to a new frequency.

        Args:
            waveform_json: JSON Waveform object.
            new_frequency: Target frequency in Hz.

        Returns:
            JSON Waveform with rescaled time axis.
        )pbdoc",
        py::arg("waveformJson"), py::arg("newFrequency"));

    m.def("scale_excitation_time_to_frequency", &scale_excitation_time_to_frequency,
        R"pbdoc(
        Scale excitation time axis to a new frequency.

        Args:
            excitation_json: JSON OperatingPointExcitation object.
            new_frequency: Target frequency in Hz.

        Returns:
            JSON OperatingPointExcitation with rescaled time axis.
        )pbdoc",
        py::arg("excitationJson"), py::arg("newFrequency"));

    m.def("calculate_induced_voltage", &calculate_induced_voltage,
        R"pbdoc(
        Calculate induced voltage from current excitation and magnetizing inductance.

        Args:
            excitation_json: JSON OperatingPointExcitation with current data.
            magnetizing_inductance: Magnetizing inductance in Henries.

        Returns:
            JSON SignalDescriptor with induced voltage waveform.
        )pbdoc",
        py::arg("excitationJson"), py::arg("magnetizingInductance"));

    m.def("calculate_induced_current", &calculate_induced_current,
        R"pbdoc(
        Calculate induced (magnetizing) current from voltage excitation and inductance.

        Args:
            excitation_json: JSON OperatingPointExcitation with voltage data.
            magnetizing_inductance: Magnetizing inductance in Henries.

        Returns:
            JSON SignalDescriptor with induced current waveform.
        )pbdoc",
        py::arg("excitationJson"), py::arg("magnetizingInductance"));

    m.def("check_requirement", &check_requirement,
        R"pbdoc(
        Check if a value satisfies a dimensional requirement with tolerance.

        Args:
            requirement_json: JSON DimensionWithTolerance object.
            value: Value to check against the requirement.

        Returns:
            True if the value satisfies the requirement, False otherwise.
        )pbdoc",
        py::arg("requirementJson"), py::arg("value"));

    m.def("get_main_harmonic_indexes", &get_main_harmonic_indexes,
        R"pbdoc(
        Get indexes of the main harmonics above a threshold.

        Args:
            harmonics_json: JSON Harmonics object.
            threshold: Amplitude threshold for inclusion.
            main_harmonic_index: Index of the fundamental harmonic.

        Returns:
            JSON array of harmonic indexes.
        )pbdoc",
        py::arg("harmonicsJson"), py::arg("threshold"), py::arg("mainHarmonicIndex"));

    m.def("get_excitation_harmonic_indexes", &get_excitation_harmonic_indexes,
        R"pbdoc(
        Get indexes of significant harmonics in an excitation.

        Args:
            excitation_json: JSON OperatingPointExcitation object.
            threshold: Amplitude threshold for inclusion.

        Returns:
            JSON array of harmonic indexes.
        )pbdoc",
        py::arg("excitationJson"), py::arg("threshold"));
}

} // namespace PyMKF