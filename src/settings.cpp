#include "settings.h"

namespace PyMKF {

py::dict get_constants() {
    py::dict constantsMap;
    constantsMap["residualGap"] = OpenMagnetics::constants.residualGap;
    constantsMap["minimumNonResidualGap"] = OpenMagnetics::constants.minimumNonResidualGap;
    constantsMap["vacuumPermeability"] = OpenMagnetics::constants.vacuumPermeability;
    constantsMap["vacuumPermittivity"] = OpenMagnetics::constants.vacuumPermittivity;
    constantsMap["spacerProtudingPercentage"] = OpenMagnetics::constants.spacerProtudingPercentage;
    constantsMap["coilPainterScale"] = OpenMagnetics::constants.coilPainterScale;
    constantsMap["minimumDistributedFringingFactor"] = OpenMagnetics::constants.minimumDistributedFringingFactor;
    constantsMap["maximumDistributedFringingFactor"] = OpenMagnetics::constants.maximumDistributedFringingFactor;
    constantsMap["initialGapLengthForSearching"] = OpenMagnetics::constants.initialGapLengthForSearching;
    constantsMap["roshenMagneticFieldStrengthStep"] = OpenMagnetics::constants.roshenMagneticFieldStrengthStep;
    constantsMap["foilToSectionMargin"] = OpenMagnetics::constants.foilToSectionMargin;
    constantsMap["planarToSectionMargin"] = OpenMagnetics::constants.planarToSectionMargin;
    return constantsMap;
}

py::dict get_defaults() {
    py::dict defaultsMap;
    json aux;
    to_json(aux, OpenMagnetics::defaults.coreLossesModelDefault);
    defaultsMap["coreLossesModelDefault"] = aux;
    to_json(aux, OpenMagnetics::defaults.coreTemperatureModelDefault);
    defaultsMap["coreTemperatureModelDefault"] = aux;
    to_json(aux, OpenMagnetics::defaults.reluctanceModelDefault);
    defaultsMap["reluctanceModelDefault"] = aux;
    to_json(aux, OpenMagnetics::defaults.magneticFieldStrengthModelDefault);
    defaultsMap["magneticFieldStrengthModelDefault"] = aux;
    to_json(aux, OpenMagnetics::defaults.magneticFieldStrengthFringingEffectModelDefault);
    defaultsMap["magneticFieldStrengthFringingEffectModelDefault"] = aux;
    defaultsMap["maximumProportionMagneticFluxDensitySaturation"] = OpenMagnetics::defaults.maximumProportionMagneticFluxDensitySaturation;
    defaultsMap["coreAdviserFrequencyReference"] = OpenMagnetics::defaults.coreAdviserFrequencyReference;
    defaultsMap["coreAdviserMagneticFluxDensityReference"] = OpenMagnetics::defaults.coreAdviserMagneticFluxDensityReference;
    defaultsMap["coreAdviserThresholdValidity"] = OpenMagnetics::defaults.coreAdviserThresholdValidity;
    defaultsMap["coreAdviserMaximumCoreTemperature"] = OpenMagnetics::defaults.coreAdviserMaximumCoreTemperature;
    defaultsMap["coreAdviserMaximumPercentagePowerCoreLosses"] = OpenMagnetics::defaults.coreAdviserMaximumPercentagePowerCoreLosses;
    defaultsMap["coreAdviserMaximumMagneticsAfterFiltering"] = OpenMagnetics::defaults.coreAdviserMaximumMagneticsAfterFiltering;
    defaultsMap["coreAdviserMaximumNumberStacks"] = OpenMagnetics::defaults.coreAdviserMaximumNumberStacks;
    defaultsMap["maximumCurrentDensity"] = OpenMagnetics::defaults.maximumCurrentDensity;
    defaultsMap["maximumEffectiveCurrentDensity"] = OpenMagnetics::defaults.maximumEffectiveCurrentDensity;
    defaultsMap["maximumNumberParallels"] = OpenMagnetics::defaults.maximumNumberParallels;
    defaultsMap["magneticFluxDensitySaturation"] = OpenMagnetics::defaults.magneticFluxDensitySaturation;
    defaultsMap["magnetizingInductanceThresholdValidity"] = OpenMagnetics::defaults.magnetizingInductanceThresholdValidity;
    defaultsMap["harmonicAmplitudeThreshold"] = OpenMagnetics::defaults.harmonicAmplitudeThreshold;
    defaultsMap["ambientTemperature"] = OpenMagnetics::defaults.ambientTemperature;
    defaultsMap["measurementFrequency"] = OpenMagnetics::defaults.measurementFrequency;
    defaultsMap["magneticFieldMirroringDimension"] = OpenMagnetics::defaults.magneticFieldMirroringDimension;
    defaultsMap["maximumCoilPattern"] = OpenMagnetics::defaults.maximumCoilPattern;
    to_json(aux, OpenMagnetics::defaults.defaultRoundWindowSectionsOrientation);
    defaultsMap["defaultRoundWindowSectionsOrientation"] = aux;
    to_json(aux, OpenMagnetics::defaults.defaultRectangularWindowSectionsOrientation);
    defaultsMap["defaultRectangularWindowSectionsOrientation"] = aux;
    defaultsMap["defaultEnamelledInsulationMaterial"] = OpenMagnetics::defaults.defaultEnamelledInsulationMaterial;
    defaultsMap["defaultInsulationMaterial"] = OpenMagnetics::defaults.defaultInsulationMaterial;
    defaultsMap["defaultLayerInsulationMaterial"] = OpenMagnetics::defaults.defaultLayerInsulationMaterial;
    defaultsMap["overlappingFactorSurroundingTurns"] = OpenMagnetics::defaults.overlappingFactorSurroundingTurns;
    to_json(aux, OpenMagnetics::defaults.commonWireStandard);
    defaultsMap["commonWireStandard"] = aux;
    return defaultsMap;
}

json get_settings() {
    try {
        json settingsJson;

        // General
        settingsJson["verbose"] = OpenMagnetics::settings.get_verbose();
        settingsJson["useToroidalCores"] = OpenMagnetics::settings.get_use_toroidal_cores();
        settingsJson["useConcentricCores"] = OpenMagnetics::settings.get_use_concentric_cores();
        settingsJson["useOnlyCoresInStock"] = OpenMagnetics::settings.get_use_only_cores_in_stock();
        settingsJson["usePowderCores"] = OpenMagnetics::settings.get_use_powder_cores();

        // Inputs
        settingsJson["inputsTrimHarmonics"] = OpenMagnetics::settings.get_inputs_trim_harmonics();
        settingsJson["inputsNumberPointsSampledWaveforms"] = OpenMagnetics::settings.get_inputs_number_points_sampled_waveforms();

        // Magnetizing inductance
        settingsJson["magnetizingInductanceIncludeAirInductance"] = OpenMagnetics::settings.get_magnetizing_inductance_include_air_inductance();

        // Coil
        settingsJson["coilAllowMarginTape"] = OpenMagnetics::settings.get_coil_allow_margin_tape();
        settingsJson["coilAllowInsulatedWire"] = OpenMagnetics::settings.get_coil_allow_insulated_wire();
        settingsJson["coilFillSectionsWithMarginTape"] = OpenMagnetics::settings.get_coil_fill_sections_with_margin_tape();
        settingsJson["coilWindEvenIfNotFit"] = OpenMagnetics::settings.get_coil_wind_even_if_not_fit();
        settingsJson["coilDelimitAndCompact"] = OpenMagnetics::settings.get_coil_delimit_and_compact();
        settingsJson["coilTryRewind"] = OpenMagnetics::settings.get_coil_try_rewind();
        settingsJson["coilIncludeAdditionalCoordinates"] = OpenMagnetics::settings.get_coil_include_additional_coordinates();
        settingsJson["coilEqualizeMargins"] = OpenMagnetics::settings.get_coil_equalize_margins();
        settingsJson["coilOnlyOneTurnPerLayerInContiguousRectangular"] = OpenMagnetics::settings.get_coil_only_one_turn_per_layer_in_contiguous_rectangular();
        settingsJson["coilMaximumLayersPlanar"] = OpenMagnetics::settings.get_coil_maximum_layers_planar();
        settingsJson["coilMesherInsideTurnsFactor"] = OpenMagnetics::settings.get_coil_mesher_inside_turns_factor();
        settingsJson["coilEnableUserWindingLossesModels"] = OpenMagnetics::settings.get_coil_enable_user_winding_losses_models();

        // Effective parameter standard
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_effective_parameter_standard());
            settingsJson["effectiveParameterStandard"] = aux;
        }
        settingsJson["nanocrystallineStackingFactor"] = OpenMagnetics::settings.get_nanocrystalline_stacking_factor();

        // Painter
        settingsJson["painterNumberPointsX"] = OpenMagnetics::settings.get_painter_number_points_x();
        settingsJson["painterNumberPointsY"] = OpenMagnetics::settings.get_painter_number_points_y();
        settingsJson["painterMode"] = OpenMagnetics::settings.get_painter_mode();
        settingsJson["painterLogarithmicScale"] = OpenMagnetics::settings.get_painter_logarithmic_scale();
        settingsJson["painterIncludeFringing"] = OpenMagnetics::settings.get_painter_include_fringing();
        settingsJson["painterDrawSpacer"] = OpenMagnetics::settings.get_painter_draw_spacer();
        settingsJson["painterSimpleLitz"] = OpenMagnetics::settings.get_painter_simple_litz();
        settingsJson["painterAdvancedLitz"] = OpenMagnetics::settings.get_painter_advanced_litz();
        if (OpenMagnetics::settings.get_painter_maximum_value_colorbar()) {
            settingsJson["painterMaximumValueColorbar"] = OpenMagnetics::settings.get_painter_maximum_value_colorbar();
        }
        if (OpenMagnetics::settings.get_painter_minimum_value_colorbar()) {
            settingsJson["painterMinimumValueColorbar"] = OpenMagnetics::settings.get_painter_minimum_value_colorbar();
        }
        settingsJson["painterColorFerrite"] = OpenMagnetics::settings.get_painter_color_ferrite();
        settingsJson["painterColorBobbin"] = OpenMagnetics::settings.get_painter_color_bobbin();
        settingsJson["painterColorCopper"] = OpenMagnetics::settings.get_painter_color_copper();
        settingsJson["painterColorInsulation"] = OpenMagnetics::settings.get_painter_color_insulation();
        settingsJson["painterColorFr4"] = OpenMagnetics::settings.get_painter_color_fr4();
        settingsJson["painterColorEnamel"] = OpenMagnetics::settings.get_painter_color_enamel();
        settingsJson["painterColorFEP"] = OpenMagnetics::settings.get_painter_color_fep();
        settingsJson["painterColorETFE"] = OpenMagnetics::settings.get_painter_color_etfe();
        settingsJson["painterColorTCA"] = OpenMagnetics::settings.get_painter_color_tca();
        settingsJson["painterColorPFA"] = OpenMagnetics::settings.get_painter_color_pfa();
        settingsJson["painterColorSilk"] = OpenMagnetics::settings.get_painter_color_silk();
        settingsJson["painterColorMargin"] = OpenMagnetics::settings.get_painter_color_margin();
        settingsJson["painterColorSpacer"] = OpenMagnetics::settings.get_painter_color_spacer();
        settingsJson["painterColorLines"] = OpenMagnetics::settings.get_painter_color_lines();
        settingsJson["painterColorText"] = OpenMagnetics::settings.get_painter_color_text();
        settingsJson["painterColorCurrentDensity"] = OpenMagnetics::settings.get_painter_color_current_density();
        settingsJson["painterColorMagneticFieldMinimum"] = OpenMagnetics::settings.get_painter_color_magnetic_field_minimum();
        settingsJson["painterColorMagneticFieldMaximum"] = OpenMagnetics::settings.get_painter_color_magnetic_field_maximum();
        settingsJson["painterCciCoordinatesPath"] = OpenMagnetics::settings.get_painter_cci_coordinates_path();
        settingsJson["painterMirroringDimension"] = OpenMagnetics::settings.get_painter_mirroring_dimension();
        if (OpenMagnetics::settings.get_painter_magnetic_field_strength_model()) {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_painter_magnetic_field_strength_model().value());
            settingsJson["painterMagneticFieldStrengthModel"] = aux;
        }

        // Magnetic field
        settingsJson["magneticFieldNumberPointsX"] = OpenMagnetics::settings.get_magnetic_field_number_points_x();
        settingsJson["magneticFieldNumberPointsY"] = OpenMagnetics::settings.get_magnetic_field_number_points_y();
        settingsJson["magneticFieldIncludeFringing"] = OpenMagnetics::settings.get_magnetic_field_include_fringing();
        settingsJson["magneticFieldMirroringDimension"] = OpenMagnetics::settings.get_magnetic_field_mirroring_dimension();

        // Leakage inductance
        settingsJson["leakageInductanceGridAutoScaling"] = OpenMagnetics::settings.get_leakage_inductance_grid_auto_scaling();
        settingsJson["leakageInductanceGridPrecisionLevelPlanar"] = OpenMagnetics::settings.get_leakage_inductance_grid_precision_level_planar();
        settingsJson["leakageInductanceGridPrecisionLevelWound"] = OpenMagnetics::settings.get_leakage_inductance_grid_precision_level_wound();

        // Adviser
        settingsJson["coilAdviserMaximumNumberWires"] = OpenMagnetics::settings.get_coil_adviser_maximum_number_wires();
        settingsJson["coreAdviserIncludeStacks"] = OpenMagnetics::settings.get_core_adviser_include_stacks();
        settingsJson["coreAdviserIncludeDistributedGaps"] = OpenMagnetics::settings.get_core_adviser_include_distributed_gaps();
        settingsJson["coreAdviserIncludeMargin"] = OpenMagnetics::settings.get_core_adviser_include_margin();
        settingsJson["coreAdviserEnableIntermediatePruning"] = OpenMagnetics::settings.get_core_adviser_enable_intermediate_pruning();
        settingsJson["coreAdviserMaximumMagneticsAfterFiltering"] = OpenMagnetics::settings.get_core_adviser_maximum_magnetics_after_filtering();
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_gapping_strategy());
            settingsJson["gappingStrategy"] = aux;
        }

        // Wire adviser
        settingsJson["wireAdviserIncludePlanar"] = OpenMagnetics::settings.get_wire_adviser_include_planar();
        settingsJson["wireAdviserIncludeFoil"] = OpenMagnetics::settings.get_wire_adviser_include_foil();
        settingsJson["wireAdviserIncludeRectangular"] = OpenMagnetics::settings.get_wire_adviser_include_rectangular();
        settingsJson["wireAdviserIncludeLitz"] = OpenMagnetics::settings.get_wire_adviser_include_litz();
        settingsJson["wireAdviserIncludeRound"] = OpenMagnetics::settings.get_wire_adviser_include_round();
        settingsJson["wireAdviserAllowRectangularInToroidalCores"] = OpenMagnetics::settings.get_wire_adviser_allow_rectangular_in_toroidal_cores();

        // Harmonics
        settingsJson["harmonicAmplitudeThresholdQuickMode"] = OpenMagnetics::settings.get_harmonic_amplitude_threshold_quick_mode();
        settingsJson["harmonicAmplitudeThreshold"] = OpenMagnetics::settings.get_harmonic_amplitude_threshold();

        // Models
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_magnetic_field_strength_model());
            settingsJson["magneticFieldStrengthModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_magnetic_field_strength_fringing_effect_model());
            settingsJson["magneticFieldStrengthFringingEffectModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_leakage_inductance_magnetic_field_strength_model());
            settingsJson["leakageInductanceMagneticFieldStrengthModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_reluctance_model());
            settingsJson["reluctanceModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_core_temperature_model());
            settingsJson["coreTemperatureModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_core_thermal_resistance_model());
            settingsJson["coreThermalResistanceModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_winding_skin_effect_losses_model());
            settingsJson["windingSkinEffectLossesModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_winding_proximity_effect_losses_model());
            settingsJson["windingProximityEffectLossesModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_stray_capacitance_model());
            settingsJson["strayCapacitanceModel"] = aux;
        }
        {
            json aux;
            to_json(aux, OpenMagnetics::settings.get_electric_field_output_unit());
            settingsJson["electricFieldOutputUnit"] = aux;
        }

        // Circuit simulator
        settingsJson["circuitSimulatorCurveFittingMode"] = OpenMagnetics::settings.get_circuit_simulator_curve_fitting_mode();
        if (OpenMagnetics::settings.get_circuit_simulator_fracpole_options()) {
            settingsJson["circuitSimulatorFracpoleOptions"] = OpenMagnetics::settings.get_circuit_simulator_fracpole_options().value();
        }
        settingsJson["circuitSimulatorIncludeSaturation"] = OpenMagnetics::settings.get_circuit_simulator_include_saturation();
        settingsJson["circuitSimulatorIncludeMutualResistance"] = OpenMagnetics::settings.get_circuit_simulator_include_mutual_resistance();
        settingsJson["circuitSimulatorCoreLossTopology"] = OpenMagnetics::settings.get_circuit_simulator_core_loss_topology();

        // Preferred manufacturers
        settingsJson["preferredCoreMaterialFerriteManufacturer"] = OpenMagnetics::settings.get_preferred_core_material_ferrite_manufacturer();
        settingsJson["preferredCoreMaterialPowderManufacturer"] = OpenMagnetics::settings.get_preferred_core_material_powder_manufacturer();
        settingsJson["coreCrossReferencerAllowDifferentCoreMaterialType"] = OpenMagnetics::settings.get_core_cross_referencer_allow_different_core_material_type();

        return settingsJson;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

void set_settings(json settingsJson) {
    try {
        // General
        if (settingsJson.contains("verbose")) OpenMagnetics::settings.set_verbose(settingsJson["verbose"]);
        if (settingsJson.contains("useToroidalCores")) OpenMagnetics::settings.set_use_toroidal_cores(settingsJson["useToroidalCores"]);
        if (settingsJson.contains("useConcentricCores")) OpenMagnetics::settings.set_use_concentric_cores(settingsJson["useConcentricCores"]);
        if (settingsJson.contains("useOnlyCoresInStock")) OpenMagnetics::settings.set_use_only_cores_in_stock(settingsJson["useOnlyCoresInStock"]);
        if (settingsJson.contains("usePowderCores")) OpenMagnetics::settings.set_use_powder_cores(settingsJson["usePowderCores"]);

        // Inputs
        if (settingsJson.contains("inputsTrimHarmonics")) OpenMagnetics::settings.set_inputs_trim_harmonics(settingsJson["inputsTrimHarmonics"]);
        if (settingsJson.contains("inputsNumberPointsSampledWaveforms")) OpenMagnetics::settings.set_inputs_number_points_sampled_waveforms(settingsJson["inputsNumberPointsSampledWaveforms"]);

        // Magnetizing inductance
        if (settingsJson.contains("magnetizingInductanceIncludeAirInductance")) OpenMagnetics::settings.set_magnetizing_inductance_include_air_inductance(settingsJson["magnetizingInductanceIncludeAirInductance"]);

        // Coil
        if (settingsJson.contains("coilAllowMarginTape")) OpenMagnetics::settings.set_coil_allow_margin_tape(settingsJson["coilAllowMarginTape"]);
        if (settingsJson.contains("coilAllowInsulatedWire")) OpenMagnetics::settings.set_coil_allow_insulated_wire(settingsJson["coilAllowInsulatedWire"]);
        if (settingsJson.contains("coilFillSectionsWithMarginTape")) OpenMagnetics::settings.set_coil_fill_sections_with_margin_tape(settingsJson["coilFillSectionsWithMarginTape"]);
        if (settingsJson.contains("coilWindEvenIfNotFit")) OpenMagnetics::settings.set_coil_wind_even_if_not_fit(settingsJson["coilWindEvenIfNotFit"]);
        if (settingsJson.contains("coilDelimitAndCompact")) OpenMagnetics::settings.set_coil_delimit_and_compact(settingsJson["coilDelimitAndCompact"]);
        if (settingsJson.contains("coilTryRewind")) OpenMagnetics::settings.set_coil_try_rewind(settingsJson["coilTryRewind"]);
        if (settingsJson.contains("coilIncludeAdditionalCoordinates")) OpenMagnetics::settings.set_coil_include_additional_coordinates(settingsJson["coilIncludeAdditionalCoordinates"]);
        if (settingsJson.contains("coilEqualizeMargins")) OpenMagnetics::settings.set_coil_equalize_margins(settingsJson["coilEqualizeMargins"]);
        if (settingsJson.contains("coilOnlyOneTurnPerLayerInContiguousRectangular")) OpenMagnetics::settings.set_coil_only_one_turn_per_layer_in_contiguous_rectangular(settingsJson["coilOnlyOneTurnPerLayerInContiguousRectangular"]);
        if (settingsJson.contains("coilMaximumLayersPlanar")) OpenMagnetics::settings.set_coil_maximum_layers_planar(settingsJson["coilMaximumLayersPlanar"]);
        if (settingsJson.contains("coilMesherInsideTurnsFactor")) OpenMagnetics::settings.set_coil_mesher_inside_turns_factor(settingsJson["coilMesherInsideTurnsFactor"]);
        if (settingsJson.contains("coilEnableUserWindingLossesModels")) OpenMagnetics::settings.set_coil_enable_user_winding_losses_models(settingsJson["coilEnableUserWindingLossesModels"]);

        // Effective parameter standard
        if (settingsJson.contains("effectiveParameterStandard")) {
            OpenMagnetics::EffectiveParameterStandard standard;
            from_json(settingsJson["effectiveParameterStandard"], standard);
            OpenMagnetics::settings.set_effective_parameter_standard(standard);
        }
        if (settingsJson.contains("nanocrystallineStackingFactor")) OpenMagnetics::settings.set_nanocrystalline_stacking_factor(settingsJson["nanocrystallineStackingFactor"]);

        // Painter
        if (settingsJson.contains("painterNumberPointsX")) OpenMagnetics::settings.set_painter_number_points_x(settingsJson["painterNumberPointsX"]);
        if (settingsJson.contains("painterNumberPointsY")) OpenMagnetics::settings.set_painter_number_points_y(settingsJson["painterNumberPointsY"]);
        if (settingsJson.contains("painterMode")) OpenMagnetics::settings.set_painter_mode(settingsJson["painterMode"]);
        if (settingsJson.contains("painterLogarithmicScale")) OpenMagnetics::settings.set_painter_logarithmic_scale(settingsJson["painterLogarithmicScale"]);
        if (settingsJson.contains("painterIncludeFringing")) OpenMagnetics::settings.set_painter_include_fringing(settingsJson["painterIncludeFringing"]);
        if (settingsJson.contains("painterDrawSpacer")) OpenMagnetics::settings.set_painter_draw_spacer(settingsJson["painterDrawSpacer"]);
        if (settingsJson.contains("painterSimpleLitz")) OpenMagnetics::settings.set_painter_simple_litz(settingsJson["painterSimpleLitz"]);
        if (settingsJson.contains("painterAdvancedLitz")) OpenMagnetics::settings.set_painter_advanced_litz(settingsJson["painterAdvancedLitz"]);
        if (settingsJson.contains("painterMaximumValueColorbar")) OpenMagnetics::settings.set_painter_maximum_value_colorbar(settingsJson["painterMaximumValueColorbar"]);
        if (settingsJson.contains("painterMinimumValueColorbar")) OpenMagnetics::settings.set_painter_minimum_value_colorbar(settingsJson["painterMinimumValueColorbar"]);
        if (settingsJson.contains("painterColorFerrite")) OpenMagnetics::settings.set_painter_color_ferrite(settingsJson["painterColorFerrite"]);
        if (settingsJson.contains("painterColorBobbin")) OpenMagnetics::settings.set_painter_color_bobbin(settingsJson["painterColorBobbin"]);
        if (settingsJson.contains("painterColorCopper")) OpenMagnetics::settings.set_painter_color_copper(settingsJson["painterColorCopper"]);
        if (settingsJson.contains("painterColorInsulation")) OpenMagnetics::settings.set_painter_color_insulation(settingsJson["painterColorInsulation"]);
        if (settingsJson.contains("painterColorFr4")) OpenMagnetics::settings.set_painter_color_fr4(settingsJson["painterColorFr4"]);
        if (settingsJson.contains("painterColorEnamel")) OpenMagnetics::settings.set_painter_color_enamel(settingsJson["painterColorEnamel"]);
        if (settingsJson.contains("painterColorFEP")) OpenMagnetics::settings.set_painter_color_fep(settingsJson["painterColorFEP"]);
        if (settingsJson.contains("painterColorETFE")) OpenMagnetics::settings.set_painter_color_etfe(settingsJson["painterColorETFE"]);
        if (settingsJson.contains("painterColorTCA")) OpenMagnetics::settings.set_painter_color_tca(settingsJson["painterColorTCA"]);
        if (settingsJson.contains("painterColorPFA")) OpenMagnetics::settings.set_painter_color_pfa(settingsJson["painterColorPFA"]);
        if (settingsJson.contains("painterColorSilk")) OpenMagnetics::settings.set_painter_color_silk(settingsJson["painterColorSilk"]);
        if (settingsJson.contains("painterColorMargin")) OpenMagnetics::settings.set_painter_color_margin(settingsJson["painterColorMargin"]);
        if (settingsJson.contains("painterColorSpacer")) OpenMagnetics::settings.set_painter_color_spacer(settingsJson["painterColorSpacer"]);
        if (settingsJson.contains("painterColorLines")) OpenMagnetics::settings.set_painter_color_lines(settingsJson["painterColorLines"]);
        if (settingsJson.contains("painterColorText")) OpenMagnetics::settings.set_painter_color_text(settingsJson["painterColorText"]);
        if (settingsJson.contains("painterColorCurrentDensity")) OpenMagnetics::settings.set_painter_color_current_density(settingsJson["painterColorCurrentDensity"]);
        if (settingsJson.contains("painterColorMagneticFieldMinimum")) OpenMagnetics::settings.set_painter_color_magnetic_field_minimum(settingsJson["painterColorMagneticFieldMinimum"]);
        if (settingsJson.contains("painterColorMagneticFieldMaximum")) OpenMagnetics::settings.set_painter_color_magnetic_field_maximum(settingsJson["painterColorMagneticFieldMaximum"]);
        if (settingsJson.contains("painterCciCoordinatesPath")) OpenMagnetics::settings.set_painter_cci_coordinates_path(settingsJson["painterCciCoordinatesPath"]);
        if (settingsJson.contains("painterMirroringDimension")) OpenMagnetics::settings.set_painter_mirroring_dimension(settingsJson["painterMirroringDimension"]);
        if (settingsJson.contains("painterMagneticFieldStrengthModel")) {
            OpenMagnetics::MagneticFieldStrengthModels model;
            from_json(settingsJson["painterMagneticFieldStrengthModel"], model);
            OpenMagnetics::settings.set_painter_magnetic_field_strength_model(model);
        }

        // Magnetic field
        if (settingsJson.contains("magneticFieldNumberPointsX")) OpenMagnetics::settings.set_magnetic_field_number_points_x(settingsJson["magneticFieldNumberPointsX"]);
        if (settingsJson.contains("magneticFieldNumberPointsY")) OpenMagnetics::settings.set_magnetic_field_number_points_y(settingsJson["magneticFieldNumberPointsY"]);
        if (settingsJson.contains("magneticFieldIncludeFringing")) OpenMagnetics::settings.set_magnetic_field_include_fringing(settingsJson["magneticFieldIncludeFringing"]);
        if (settingsJson.contains("magneticFieldMirroringDimension")) OpenMagnetics::settings.set_magnetic_field_mirroring_dimension(settingsJson["magneticFieldMirroringDimension"]);

        // Leakage inductance
        if (settingsJson.contains("leakageInductanceGridAutoScaling")) OpenMagnetics::settings.set_leakage_inductance_grid_auto_scaling(settingsJson["leakageInductanceGridAutoScaling"]);
        if (settingsJson.contains("leakageInductanceGridPrecisionLevelPlanar")) OpenMagnetics::settings.set_leakage_inductance_grid_precision_level_planar(settingsJson["leakageInductanceGridPrecisionLevelPlanar"]);
        if (settingsJson.contains("leakageInductanceGridPrecisionLevelWound")) OpenMagnetics::settings.set_leakage_inductance_grid_precision_level_wound(settingsJson["leakageInductanceGridPrecisionLevelWound"]);

        // Adviser
        if (settingsJson.contains("coilAdviserMaximumNumberWires")) OpenMagnetics::settings.set_coil_adviser_maximum_number_wires(settingsJson["coilAdviserMaximumNumberWires"]);
        if (settingsJson.contains("coreAdviserIncludeStacks")) OpenMagnetics::settings.set_core_adviser_include_stacks(settingsJson["coreAdviserIncludeStacks"]);
        if (settingsJson.contains("coreAdviserIncludeDistributedGaps")) OpenMagnetics::settings.set_core_adviser_include_distributed_gaps(settingsJson["coreAdviserIncludeDistributedGaps"]);
        if (settingsJson.contains("coreAdviserIncludeMargin")) OpenMagnetics::settings.set_core_adviser_include_margin(settingsJson["coreAdviserIncludeMargin"]);
        if (settingsJson.contains("coreAdviserEnableIntermediatePruning")) OpenMagnetics::settings.set_core_adviser_enable_intermediate_pruning(settingsJson["coreAdviserEnableIntermediatePruning"]);
        if (settingsJson.contains("coreAdviserMaximumMagneticsAfterFiltering")) OpenMagnetics::settings.set_core_adviser_maximum_magnetics_after_filtering(settingsJson["coreAdviserMaximumMagneticsAfterFiltering"]);
        if (settingsJson.contains("gappingStrategy")) {
            OpenMagnetics::GappingOptimizationStrategy strategy;
            from_json(settingsJson["gappingStrategy"], strategy);
            OpenMagnetics::settings.set_gapping_strategy(strategy);
        }

        // Wire adviser
        if (settingsJson.contains("wireAdviserIncludePlanar")) OpenMagnetics::settings.set_wire_adviser_include_planar(settingsJson["wireAdviserIncludePlanar"]);
        if (settingsJson.contains("wireAdviserIncludeFoil")) OpenMagnetics::settings.set_wire_adviser_include_foil(settingsJson["wireAdviserIncludeFoil"]);
        if (settingsJson.contains("wireAdviserIncludeRectangular")) OpenMagnetics::settings.set_wire_adviser_include_rectangular(settingsJson["wireAdviserIncludeRectangular"]);
        if (settingsJson.contains("wireAdviserIncludeLitz")) OpenMagnetics::settings.set_wire_adviser_include_litz(settingsJson["wireAdviserIncludeLitz"]);
        if (settingsJson.contains("wireAdviserIncludeRound")) OpenMagnetics::settings.set_wire_adviser_include_round(settingsJson["wireAdviserIncludeRound"]);
        if (settingsJson.contains("wireAdviserAllowRectangularInToroidalCores")) OpenMagnetics::settings.set_wire_adviser_allow_rectangular_in_toroidal_cores(settingsJson["wireAdviserAllowRectangularInToroidalCores"]);

        // Harmonics
        if (settingsJson.contains("harmonicAmplitudeThresholdQuickMode")) OpenMagnetics::settings.set_harmonic_amplitude_threshold_quick_mode(settingsJson["harmonicAmplitudeThresholdQuickMode"]);
        if (settingsJson.contains("harmonicAmplitudeThreshold")) OpenMagnetics::settings.set_harmonic_amplitude_threshold(settingsJson["harmonicAmplitudeThreshold"]);

        // Models
        if (settingsJson.contains("magneticFieldStrengthModel")) {
            OpenMagnetics::MagneticFieldStrengthModels model;
            from_json(settingsJson["magneticFieldStrengthModel"], model);
            OpenMagnetics::settings.set_magnetic_field_strength_model(model);
        }
        if (settingsJson.contains("magneticFieldStrengthFringingEffectModel")) {
            OpenMagnetics::MagneticFieldStrengthFringingEffectModels model;
            from_json(settingsJson["magneticFieldStrengthFringingEffectModel"], model);
            OpenMagnetics::settings.set_magnetic_field_strength_fringing_effect_model(model);
        }
        if (settingsJson.contains("leakageInductanceMagneticFieldStrengthModel")) {
            OpenMagnetics::MagneticFieldStrengthModels model;
            from_json(settingsJson["leakageInductanceMagneticFieldStrengthModel"], model);
            OpenMagnetics::settings.set_leakage_inductance_magnetic_field_strength_model(model);
        }
        if (settingsJson.contains("reluctanceModel")) {
            OpenMagnetics::ReluctanceModels model;
            from_json(settingsJson["reluctanceModel"], model);
            OpenMagnetics::settings.set_reluctance_model(model);
        }
        if (settingsJson.contains("coreTemperatureModel")) {
            OpenMagnetics::CoreTemperatureModels model;
            from_json(settingsJson["coreTemperatureModel"], model);
            OpenMagnetics::settings.set_core_temperature_model(model);
        }
        if (settingsJson.contains("coreThermalResistanceModel")) {
            OpenMagnetics::CoreThermalResistanceModels model;
            from_json(settingsJson["coreThermalResistanceModel"], model);
            OpenMagnetics::settings.set_core_thermal_resistance_model(model);
        }
        if (settingsJson.contains("windingSkinEffectLossesModel")) {
            OpenMagnetics::WindingSkinEffectLossesModels model;
            from_json(settingsJson["windingSkinEffectLossesModel"], model);
            OpenMagnetics::settings.set_winding_skin_effect_losses_model(model);
        }
        if (settingsJson.contains("windingProximityEffectLossesModel")) {
            OpenMagnetics::WindingProximityEffectLossesModels model;
            from_json(settingsJson["windingProximityEffectLossesModel"], model);
            OpenMagnetics::settings.set_winding_proximity_effect_losses_model(model);
        }
        if (settingsJson.contains("strayCapacitanceModel")) {
            OpenMagnetics::StrayCapacitanceModels model;
            from_json(settingsJson["strayCapacitanceModel"], model);
            OpenMagnetics::settings.set_stray_capacitance_model(model);
        }
        if (settingsJson.contains("electricFieldOutputUnit")) {
            OpenMagnetics::ElectricFieldOutputUnit unit;
            from_json(settingsJson["electricFieldOutputUnit"], unit);
            OpenMagnetics::settings.set_electric_field_output_unit(unit);
        }

        // Core losses model
        if (settingsJson.contains("coreLossesPreferredModelName")) {
            OpenMagnetics::CoreLossesModels model;
            from_json(settingsJson["coreLossesPreferredModelName"], model);
            OpenMagnetics::settings.set_core_losses_preferred_model_name(model);
        }

        // Circuit simulator
        if (settingsJson.contains("circuitSimulatorCurveFittingMode")) OpenMagnetics::settings.set_circuit_simulator_curve_fitting_mode(settingsJson["circuitSimulatorCurveFittingMode"]);
        if (settingsJson.contains("circuitSimulatorFracpoleOptions")) OpenMagnetics::settings.set_circuit_simulator_fracpole_options(settingsJson["circuitSimulatorFracpoleOptions"].get<std::map<std::string, double>>());
        if (settingsJson.contains("circuitSimulatorIncludeSaturation")) OpenMagnetics::settings.set_circuit_simulator_include_saturation(settingsJson["circuitSimulatorIncludeSaturation"]);
        if (settingsJson.contains("circuitSimulatorIncludeMutualResistance")) OpenMagnetics::settings.set_circuit_simulator_include_mutual_resistance(settingsJson["circuitSimulatorIncludeMutualResistance"]);
        if (settingsJson.contains("circuitSimulatorCoreLossTopology")) OpenMagnetics::settings.set_circuit_simulator_core_loss_topology(settingsJson["circuitSimulatorCoreLossTopology"]);

        // Preferred manufacturers
        if (settingsJson.contains("preferredCoreMaterialFerriteManufacturer")) OpenMagnetics::settings.set_preferred_core_material_ferrite_manufacturer(settingsJson["preferredCoreMaterialFerriteManufacturer"]);
        if (settingsJson.contains("preferredCoreMaterialPowderManufacturer")) OpenMagnetics::settings.set_preferred_core_material_powder_manufacturer(settingsJson["preferredCoreMaterialPowderManufacturer"]);
        if (settingsJson.contains("coreCrossReferencerAllowDifferentCoreMaterialType")) OpenMagnetics::settings.set_core_cross_referencer_allow_different_core_material_type(settingsJson["coreCrossReferencerAllowDifferentCoreMaterialType"]);
    }
    catch (const std::exception &exc) {
        throw std::runtime_error("Exception: " + std::string{exc.what()});
    }
}

void reset_settings() {
    OpenMagnetics::settings.reset();
}

json get_default_models() {
    try {
        json models;
        models["coreLosses"] = magic_enum::enum_name(OpenMagnetics::defaults.coreLossesModelDefault);
        models["coreTemperature"] = magic_enum::enum_name(OpenMagnetics::defaults.coreTemperatureModelDefault);
        models["reluctance"] = magic_enum::enum_name(OpenMagnetics::defaults.reluctanceModelDefault);
        models["magneticFieldStrength"] = magic_enum::enum_name(OpenMagnetics::defaults.magneticFieldStrengthModelDefault);
        models["magneticFieldStrengthFringingEffect"] = magic_enum::enum_name(OpenMagnetics::defaults.magneticFieldStrengthFringingEffectModelDefault);
        return models;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["data"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

void register_settings_bindings(py::module& m) {
    m.def("get_constants", &get_constants,
        R"pbdoc(
        Get physical and system constants used in calculations.
        
        Returns a dictionary of constants including vacuum permeability,
        vacuum permittivity, gap parameters, and display settings.
        
        Returns:
            Dictionary with constant names as keys and values.
        )pbdoc");
    
    m.def("get_defaults", &get_defaults,
        R"pbdoc(
        Get default values for various parameters and models.
        
        Returns defaults for core losses models, temperature models,
        reluctance models, and design thresholds.
        
        Returns:
            Dictionary with default parameter names and values.
        )pbdoc");
    
    m.def("get_settings", &get_settings,
        R"pbdoc(
        Get current library settings.
        
        Returns all configurable settings including coil winding options,
        painter/visualization settings, and magnetic field calculation options.
        
        Returns:
            JSON object with all current settings.
        )pbdoc");
    
    m.def("set_settings", &set_settings,
        R"pbdoc(
        Update library settings.
        
        Configures coil winding options, visualization settings, and
        calculation parameters.
        
        Args:
            settings_json: JSON object with settings to update.
                          Only included keys will be modified.
        
        Common settings:
            - coilAllowMarginTape: Allow margin tape in windings
            - coilAllowInsulatedWire: Allow insulated wire
            - useOnlyCoresInStock: Limit to in-stock cores
            - painterNumberPointsX/Y: Field plot resolution
        )pbdoc");
    
    m.def("reset_settings", &reset_settings,
        R"pbdoc(
        Reset all settings to default values.
        
        Restores all library settings to their initial defaults.
        Useful for ensuring consistent behavior between tests.
        )pbdoc");
    
    m.def("get_default_models", &get_default_models,
        R"pbdoc(
        Get names of default calculation models.
        
        Returns the default model selections for core losses,
        temperature, reluctance, and magnetic field calculations.
        
        Returns:
            JSON object mapping model types to default model names.
        )pbdoc");
}

} // namespace PyMKF