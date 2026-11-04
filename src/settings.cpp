#include "settings.h"
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

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
    // ABT #647: the CCI coordinate directory is OPTIONAL — strand counts up to 1000 use the
    // build-time embedded coordinates — so merely REPORTING the settings must not force it to
    // resolve. get_painter_cci_coordinates_path() throws when nothing resolves, which made a
    // routine get_settings() fail on every relocated install (i.e. every published wheel: the
    // builder's source tree is gone by then). Report null for "none resolved" instead.
    if (auto cciCoordinatesPath = OpenMagnetics::settings.try_get_painter_cci_coordinates_path()) {
        settingsJson["painterCciCoordinatesPath"] = cciCoordinatesPath.value();
    }
    else {
        settingsJson["painterCciCoordinatesPath"] = nullptr;
    }
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
    settingsJson["coreAdviserEnableTemperatureFilter"] = OpenMagnetics::settings.get_core_adviser_enable_temperature_filter();
    settingsJson["coreAdviserMaximumTemperature"] = OpenMagnetics::settings.get_core_adviser_maximum_temperature();
    settingsJson["coreAdviserSaturationMargin"] = OpenMagnetics::settings.get_core_adviser_saturation_margin();
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
    // Memory kept for the turn-field sums of recently evaluated meshes (0 keeps nothing).
    settingsJson["magneticFieldTurnSumsCacheBytes"] = OpenMagnetics::settings.get_magnetic_field_turn_sums_cache_bytes();

    // Thermal network: a turn overlapping its enclosure throws (true) or loses that conduction path with an ERROR logged (false).
    settingsJson["thermalNetworkStrictGeometry"] = OpenMagnetics::settings.get_thermal_network_strict_geometry();

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

    // Material data (ABT #2265)
    settingsJson["allowMaterialDataExtrapolation"] = OpenMagnetics::settings.get_allow_material_data_extrapolation();

    return settingsJson;
}

// Applies every key of settingsJson that PyOM knows. With checkedKeys set, it also records each key name it looks
// for, so calling it on an empty object lists the known keys without applying anything (set_settings uses this).
static void apply_settings(json settingsJson, std::set<std::string>* checkedKeys) {
    auto has = [&](const char* key) {
        if (checkedKeys) checkedKeys->insert(key);
        return settingsJson.contains(key);
    };
    // Material data (ABT #2265): whether material data (Steinmetz, permeability, ...) is evaluated outside the range
    // it was measured on, holding the nearest data with a warning, or throws there.
    if (has("allowMaterialDataExtrapolation")) OpenMagnetics::settings.set_allow_material_data_extrapolation(settingsJson["allowMaterialDataExtrapolation"]);

    // General
    if (has("verbose")) OpenMagnetics::settings.set_verbose(settingsJson["verbose"]);
    if (has("useToroidalCores")) OpenMagnetics::settings.set_use_toroidal_cores(settingsJson["useToroidalCores"]);
    if (has("useConcentricCores")) OpenMagnetics::settings.set_use_concentric_cores(settingsJson["useConcentricCores"]);
    if (has("useOnlyCoresInStock")) OpenMagnetics::settings.set_use_only_cores_in_stock(settingsJson["useOnlyCoresInStock"]);
    if (has("usePowderCores")) OpenMagnetics::settings.set_use_powder_cores(settingsJson["usePowderCores"]);

    // Inputs
    if (has("inputsTrimHarmonics")) OpenMagnetics::settings.set_inputs_trim_harmonics(settingsJson["inputsTrimHarmonics"]);
    if (has("inputsNumberPointsSampledWaveforms")) OpenMagnetics::settings.set_inputs_number_points_sampled_waveforms(settingsJson["inputsNumberPointsSampledWaveforms"]);

    // Magnetizing inductance
    if (has("magnetizingInductanceIncludeAirInductance")) OpenMagnetics::settings.set_magnetizing_inductance_include_air_inductance(settingsJson["magnetizingInductanceIncludeAirInductance"]);

    // Coil
    if (has("coilAllowMarginTape")) OpenMagnetics::settings.set_coil_allow_margin_tape(settingsJson["coilAllowMarginTape"]);
    if (has("coilAllowInsulatedWire")) OpenMagnetics::settings.set_coil_allow_insulated_wire(settingsJson["coilAllowInsulatedWire"]);
    if (has("coilFillSectionsWithMarginTape")) OpenMagnetics::settings.set_coil_fill_sections_with_margin_tape(settingsJson["coilFillSectionsWithMarginTape"]);
    if (has("coilWindEvenIfNotFit")) OpenMagnetics::settings.set_coil_wind_even_if_not_fit(settingsJson["coilWindEvenIfNotFit"]);
    if (has("coilDelimitAndCompact")) OpenMagnetics::settings.set_coil_delimit_and_compact(settingsJson["coilDelimitAndCompact"]);
    if (has("coilTryRewind")) OpenMagnetics::settings.set_coil_try_rewind(settingsJson["coilTryRewind"]);
    if (has("coilIncludeAdditionalCoordinates")) OpenMagnetics::settings.set_coil_include_additional_coordinates(settingsJson["coilIncludeAdditionalCoordinates"]);
    if (has("coilEqualizeMargins")) OpenMagnetics::settings.set_coil_equalize_margins(settingsJson["coilEqualizeMargins"]);
    if (has("coilOnlyOneTurnPerLayerInContiguousRectangular")) OpenMagnetics::settings.set_coil_only_one_turn_per_layer_in_contiguous_rectangular(settingsJson["coilOnlyOneTurnPerLayerInContiguousRectangular"]);
    if (has("coilMaximumLayersPlanar")) OpenMagnetics::settings.set_coil_maximum_layers_planar(settingsJson["coilMaximumLayersPlanar"]);
    if (has("coilMesherInsideTurnsFactor")) OpenMagnetics::settings.set_coil_mesher_inside_turns_factor(settingsJson["coilMesherInsideTurnsFactor"]);
    if (has("coilEnableUserWindingLossesModels")) OpenMagnetics::settings.set_coil_enable_user_winding_losses_models(settingsJson["coilEnableUserWindingLossesModels"]);

    // Effective parameter standard
    if (has("effectiveParameterStandard")) {
        EffectiveParameterStandard standard;
        from_json(settingsJson["effectiveParameterStandard"], standard);
        OpenMagnetics::settings.set_effective_parameter_standard(standard);
    }

    // Painter
    if (has("painterNumberPointsX")) OpenMagnetics::settings.set_painter_number_points_x(settingsJson["painterNumberPointsX"]);
    if (has("painterNumberPointsY")) OpenMagnetics::settings.set_painter_number_points_y(settingsJson["painterNumberPointsY"]);
    if (has("painterMode")) OpenMagnetics::settings.set_painter_mode(settingsJson["painterMode"]);
    if (has("painterLogarithmicScale")) OpenMagnetics::settings.set_painter_logarithmic_scale(settingsJson["painterLogarithmicScale"]);
    if (has("painterIncludeFringing")) OpenMagnetics::settings.set_painter_include_fringing(settingsJson["painterIncludeFringing"]);
    if (has("painterDrawSpacer")) OpenMagnetics::settings.set_painter_draw_spacer(settingsJson["painterDrawSpacer"]);
    if (has("painterSimpleLitz")) OpenMagnetics::settings.set_painter_simple_litz(settingsJson["painterSimpleLitz"]);
    if (has("painterAdvancedLitz")) OpenMagnetics::settings.set_painter_advanced_litz(settingsJson["painterAdvancedLitz"]);
    if (has("painterMaximumValueColorbar")) OpenMagnetics::settings.set_painter_maximum_value_colorbar(settingsJson["painterMaximumValueColorbar"]);
    if (has("painterMinimumValueColorbar")) OpenMagnetics::settings.set_painter_minimum_value_colorbar(settingsJson["painterMinimumValueColorbar"]);
    if (has("painterColorFerrite")) OpenMagnetics::settings.set_painter_color_ferrite(settingsJson["painterColorFerrite"]);
    if (has("painterColorBobbin")) OpenMagnetics::settings.set_painter_color_bobbin(settingsJson["painterColorBobbin"]);
    if (has("painterColorCopper")) OpenMagnetics::settings.set_painter_color_copper(settingsJson["painterColorCopper"]);
    if (has("painterColorInsulation")) OpenMagnetics::settings.set_painter_color_insulation(settingsJson["painterColorInsulation"]);
    if (has("painterColorFr4")) OpenMagnetics::settings.set_painter_color_fr4(settingsJson["painterColorFr4"]);
    if (has("painterColorEnamel")) OpenMagnetics::settings.set_painter_color_enamel(settingsJson["painterColorEnamel"]);
    if (has("painterColorFEP")) OpenMagnetics::settings.set_painter_color_fep(settingsJson["painterColorFEP"]);
    if (has("painterColorETFE")) OpenMagnetics::settings.set_painter_color_etfe(settingsJson["painterColorETFE"]);
    if (has("painterColorTCA")) OpenMagnetics::settings.set_painter_color_tca(settingsJson["painterColorTCA"]);
    if (has("painterColorPFA")) OpenMagnetics::settings.set_painter_color_pfa(settingsJson["painterColorPFA"]);
    if (has("painterColorSilk")) OpenMagnetics::settings.set_painter_color_silk(settingsJson["painterColorSilk"]);
    if (has("painterColorMargin")) OpenMagnetics::settings.set_painter_color_margin(settingsJson["painterColorMargin"]);
    if (has("painterColorSpacer")) OpenMagnetics::settings.set_painter_color_spacer(settingsJson["painterColorSpacer"]);
    if (has("painterColorLines")) OpenMagnetics::settings.set_painter_color_lines(settingsJson["painterColorLines"]);
    if (has("painterColorText")) OpenMagnetics::settings.set_painter_color_text(settingsJson["painterColorText"]);
    if (has("painterColorCurrentDensity")) OpenMagnetics::settings.set_painter_color_current_density(settingsJson["painterColorCurrentDensity"]);
    if (has("painterColorMagneticFieldMinimum")) OpenMagnetics::settings.set_painter_color_magnetic_field_minimum(settingsJson["painterColorMagneticFieldMinimum"]);
    if (has("painterColorMagneticFieldMaximum")) OpenMagnetics::settings.set_painter_color_magnetic_field_maximum(settingsJson["painterColorMagneticFieldMaximum"]);
    // null means "not set" (see get_settings above), so set_settings(get_settings()) round-trips
    // instead of trying to assign a null to a std::string.
    if (has("painterCciCoordinatesPath") && !settingsJson["painterCciCoordinatesPath"].is_null())
        OpenMagnetics::settings.set_painter_cci_coordinates_path(settingsJson["painterCciCoordinatesPath"]);
    if (has("painterMirroringDimension")) OpenMagnetics::settings.set_painter_mirroring_dimension(settingsJson["painterMirroringDimension"]);
    if (has("painterMagneticFieldStrengthModel")) {
        OpenMagnetics::MagneticFieldStrengthModels model;
        from_json(settingsJson["painterMagneticFieldStrengthModel"], model);
        OpenMagnetics::settings.set_painter_magnetic_field_strength_model(model);
    }

    // Magnetic field
    if (has("magneticFieldNumberPointsX")) OpenMagnetics::settings.set_magnetic_field_number_points_x(settingsJson["magneticFieldNumberPointsX"]);
    if (has("magneticFieldNumberPointsY")) OpenMagnetics::settings.set_magnetic_field_number_points_y(settingsJson["magneticFieldNumberPointsY"]);
    if (has("magneticFieldIncludeFringing")) OpenMagnetics::settings.set_magnetic_field_include_fringing(settingsJson["magneticFieldIncludeFringing"]);
    if (has("magneticFieldMirroringDimension")) OpenMagnetics::settings.set_magnetic_field_mirroring_dimension(settingsJson["magneticFieldMirroringDimension"]);

    // Leakage inductance
    if (has("leakageInductanceGridAutoScaling")) OpenMagnetics::settings.set_leakage_inductance_grid_auto_scaling(settingsJson["leakageInductanceGridAutoScaling"]);
    if (has("leakageInductanceGridPrecisionLevelPlanar")) OpenMagnetics::settings.set_leakage_inductance_grid_precision_level_planar(settingsJson["leakageInductanceGridPrecisionLevelPlanar"]);
    if (has("leakageInductanceGridPrecisionLevelWound")) OpenMagnetics::settings.set_leakage_inductance_grid_precision_level_wound(settingsJson["leakageInductanceGridPrecisionLevelWound"]);

    // Adviser
    if (has("coilAdviserMaximumNumberWires")) OpenMagnetics::settings.set_coil_adviser_maximum_number_wires(settingsJson["coilAdviserMaximumNumberWires"]);
    if (has("coreAdviserIncludeStacks")) OpenMagnetics::settings.set_core_adviser_include_stacks(settingsJson["coreAdviserIncludeStacks"]);
    if (has("coreAdviserIncludeDistributedGaps")) OpenMagnetics::settings.set_core_adviser_include_distributed_gaps(settingsJson["coreAdviserIncludeDistributedGaps"]);
    if (has("coreAdviserIncludeMargin")) OpenMagnetics::settings.set_core_adviser_include_margin(settingsJson["coreAdviserIncludeMargin"]);
    if (has("coreAdviserEnableIntermediatePruning")) OpenMagnetics::settings.set_core_adviser_enable_intermediate_pruning(settingsJson["coreAdviserEnableIntermediatePruning"]);
    if (has("coreAdviserMaximumMagneticsAfterFiltering")) OpenMagnetics::settings.set_core_adviser_maximum_magnetics_after_filtering(settingsJson["coreAdviserMaximumMagneticsAfterFiltering"]);
    if (has("coreAdviserEnableTemperatureFilter")) OpenMagnetics::settings.set_core_adviser_enable_temperature_filter(settingsJson["coreAdviserEnableTemperatureFilter"]);
    if (has("coreAdviserMaximumTemperature")) OpenMagnetics::settings.set_core_adviser_maximum_temperature(settingsJson["coreAdviserMaximumTemperature"]);
    if (has("coreAdviserSaturationMargin")) OpenMagnetics::settings.set_core_adviser_saturation_margin(settingsJson["coreAdviserSaturationMargin"]);
    if (has("gappingStrategy")) {
        GappingOptimizationStrategy strategy;
        from_json(settingsJson["gappingStrategy"], strategy);
        OpenMagnetics::settings.set_gapping_strategy(strategy);
    }

    // Wire adviser
    if (has("wireAdviserIncludePlanar")) OpenMagnetics::settings.set_wire_adviser_include_planar(settingsJson["wireAdviserIncludePlanar"]);
    if (has("wireAdviserIncludeFoil")) OpenMagnetics::settings.set_wire_adviser_include_foil(settingsJson["wireAdviserIncludeFoil"]);
    if (has("wireAdviserIncludeRectangular")) OpenMagnetics::settings.set_wire_adviser_include_rectangular(settingsJson["wireAdviserIncludeRectangular"]);
    if (has("wireAdviserIncludeLitz")) OpenMagnetics::settings.set_wire_adviser_include_litz(settingsJson["wireAdviserIncludeLitz"]);
    if (has("wireAdviserIncludeRound")) OpenMagnetics::settings.set_wire_adviser_include_round(settingsJson["wireAdviserIncludeRound"]);
    if (has("wireAdviserAllowRectangularInToroidalCores")) OpenMagnetics::settings.set_wire_adviser_allow_rectangular_in_toroidal_cores(settingsJson["wireAdviserAllowRectangularInToroidalCores"]);

    // Harmonics
    if (has("harmonicAmplitudeThresholdQuickMode")) OpenMagnetics::settings.set_harmonic_amplitude_threshold_quick_mode(settingsJson["harmonicAmplitudeThresholdQuickMode"]);
    if (has("harmonicAmplitudeThreshold")) OpenMagnetics::settings.set_harmonic_amplitude_threshold(settingsJson["harmonicAmplitudeThreshold"]);
    if (has("magneticFieldTurnSumsCacheBytes")) OpenMagnetics::settings.set_magnetic_field_turn_sums_cache_bytes(settingsJson["magneticFieldTurnSumsCacheBytes"].get<size_t>());

    // Thermal network
    if (has("thermalNetworkStrictGeometry")) OpenMagnetics::settings.set_thermal_network_strict_geometry(settingsJson["thermalNetworkStrictGeometry"]);

    // Models
    if (has("magneticFieldStrengthModel")) {
        OpenMagnetics::MagneticFieldStrengthModels model;
        from_json(settingsJson["magneticFieldStrengthModel"], model);
        OpenMagnetics::settings.set_magnetic_field_strength_model(model);
    }
    if (has("magneticFieldStrengthFringingEffectModel")) {
        OpenMagnetics::MagneticFieldStrengthFringingEffectModels model;
        from_json(settingsJson["magneticFieldStrengthFringingEffectModel"], model);
        OpenMagnetics::settings.set_magnetic_field_strength_fringing_effect_model(model);
    }
    if (has("leakageInductanceMagneticFieldStrengthModel")) {
        OpenMagnetics::MagneticFieldStrengthModels model;
        from_json(settingsJson["leakageInductanceMagneticFieldStrengthModel"], model);
        OpenMagnetics::settings.set_leakage_inductance_magnetic_field_strength_model(model);
    }
    if (has("reluctanceModel")) {
        OpenMagnetics::ReluctanceModels model;
        from_json(settingsJson["reluctanceModel"], model);
        OpenMagnetics::settings.set_reluctance_model(model);
    }
    if (has("coreTemperatureModel")) {
        OpenMagnetics::CoreTemperatureModels model;
        from_json(settingsJson["coreTemperatureModel"], model);
        OpenMagnetics::settings.set_core_temperature_model(model);
    }
    if (has("coreThermalResistanceModel")) {
        OpenMagnetics::CoreThermalResistanceModels model;
        from_json(settingsJson["coreThermalResistanceModel"], model);
        OpenMagnetics::settings.set_core_thermal_resistance_model(model);
    }
    if (has("windingSkinEffectLossesModel")) {
        OpenMagnetics::WindingSkinEffectLossesModels model;
        from_json(settingsJson["windingSkinEffectLossesModel"], model);
        OpenMagnetics::settings.set_winding_skin_effect_losses_model(model);
    }
    if (has("windingProximityEffectLossesModel")) {
        OpenMagnetics::WindingProximityEffectLossesModels model;
        from_json(settingsJson["windingProximityEffectLossesModel"], model);
        OpenMagnetics::settings.set_winding_proximity_effect_losses_model(model);
    }
    if (has("strayCapacitanceModel")) {
        OpenMagnetics::StrayCapacitanceModels model;
        from_json(settingsJson["strayCapacitanceModel"], model);
        OpenMagnetics::settings.set_stray_capacitance_model(model);
    }
    if (has("electricFieldOutputUnit")) {
        OpenMagnetics::ElectricFieldOutputUnit unit;
        from_json(settingsJson["electricFieldOutputUnit"], unit);
        OpenMagnetics::settings.set_electric_field_output_unit(unit);
    }

    // Core losses model
    if (has("coreLossesPreferredModelName")) {
        OpenMagnetics::CoreLossesModels model;
        from_json(settingsJson["coreLossesPreferredModelName"], model);
        OpenMagnetics::settings.set_core_losses_preferred_model_name(model);
    }

    // Circuit simulator
    if (has("circuitSimulatorCurveFittingMode")) OpenMagnetics::settings.set_circuit_simulator_curve_fitting_mode(settingsJson["circuitSimulatorCurveFittingMode"]);
    if (has("circuitSimulatorFracpoleOptions")) OpenMagnetics::settings.set_circuit_simulator_fracpole_options(settingsJson["circuitSimulatorFracpoleOptions"].get<std::map<std::string, double>>());
    if (has("circuitSimulatorIncludeSaturation")) OpenMagnetics::settings.set_circuit_simulator_include_saturation(settingsJson["circuitSimulatorIncludeSaturation"]);
    if (has("circuitSimulatorIncludeMutualResistance")) OpenMagnetics::settings.set_circuit_simulator_include_mutual_resistance(settingsJson["circuitSimulatorIncludeMutualResistance"]);
    if (has("circuitSimulatorCoreLossTopology")) OpenMagnetics::settings.set_circuit_simulator_core_loss_topology(settingsJson["circuitSimulatorCoreLossTopology"]);

    // Preferred manufacturers
    if (has("preferredCoreMaterialFerriteManufacturer")) OpenMagnetics::settings.set_preferred_core_material_ferrite_manufacturer(settingsJson["preferredCoreMaterialFerriteManufacturer"]);
    if (has("preferredCoreMaterialPowderManufacturer")) OpenMagnetics::settings.set_preferred_core_material_powder_manufacturer(settingsJson["preferredCoreMaterialPowderManufacturer"]);
    if (has("coreCrossReferencerAllowDifferentCoreMaterialType")) OpenMagnetics::settings.set_core_cross_referencer_allow_different_core_material_type(settingsJson["coreCrossReferencerAllowDifferentCoreMaterialType"]);
}

void set_settings(json settingsJson) {
    // ABT #2265: an unknown key used to be dropped silently, so a misspelt or not-yet-exposed setting
    // (e.g. allowMaterialDataExtrapolation before it was added here) looked set and did nothing. The known keys come
    // from apply_settings itself, so this list cannot drift from what is applied.
    static const std::set<std::string> knownKeys = [] {
        std::set<std::string> keys;
        apply_settings(json::object(), &keys);
        return keys;
    }();
    if (!settingsJson.is_object()) {
        throw std::invalid_argument("set_settings expects a JSON object of settings, got: " + settingsJson.dump());
    }
    std::vector<std::string> unknown;
    for (const auto& item : settingsJson.items()) {
        if (!knownKeys.count(item.key())) unknown.push_back(item.key());
    }
    if (!unknown.empty()) {
        std::string list;
        for (const auto& key : unknown) list += (list.empty() ? "" : ", ") + key;
        throw std::invalid_argument("set_settings: unknown setting(s): " + list + ". Nothing was applied; get_settings() lists the known keys.");
    }
    apply_settings(settingsJson, nullptr);
}

void reset_settings() {
    OpenMagnetics::settings.reset();
}

json get_default_models() {
    json models;
    models["coreLosses"] = magic_enum::enum_name(OpenMagnetics::defaults.coreLossesModelDefault);
    models["coreTemperature"] = magic_enum::enum_name(OpenMagnetics::defaults.coreTemperatureModelDefault);
    models["reluctance"] = magic_enum::enum_name(OpenMagnetics::defaults.reluctanceModelDefault);
    models["magneticFieldStrength"] = magic_enum::enum_name(OpenMagnetics::defaults.magneticFieldStrengthModelDefault);
    models["magneticFieldStrengthFringingEffect"] = magic_enum::enum_name(OpenMagnetics::defaults.magneticFieldStrengthFringingEffectModelDefault);
    return models;
}

std::vector<std::string> get_all_magnetic_field_strength_models() {
    std::vector<std::string> models;
    for (auto& [value, name] : magic_enum::enum_entries<OpenMagnetics::MagneticFieldStrengthModels>()) {
        json aux;
        to_json(aux, value);
        models.push_back(aux);
    }
    return models;
}

std::vector<std::string> get_all_fringing_effect_models() {
    std::vector<std::string> models;
    for (auto& [value, name] : magic_enum::enum_entries<OpenMagnetics::MagneticFieldStrengthFringingEffectModels>()) {
        json aux;
        to_json(aux, value);
        models.push_back(aux);
    }
    return models;
}

std::vector<std::string> get_all_reluctance_models() {
    std::vector<std::string> models;
    for (auto& [value, name] : magic_enum::enum_entries<OpenMagnetics::ReluctanceModels>()) {
        json aux;
        to_json(aux, value);
        models.push_back(aux);
    }
    return models;
}

std::vector<std::string> get_all_stray_capacitance_models() {
    std::vector<std::string> models;
    for (auto& [value, name] : magic_enum::enum_entries<OpenMagnetics::StrayCapacitanceModels>()) {
        json aux;
        to_json(aux, value);
        models.push_back(aux);
    }
    return models;
}

std::vector<std::string> get_all_winding_proximity_effect_models() {
    std::vector<std::string> models;
    for (auto& [value, name] : magic_enum::enum_entries<OpenMagnetics::WindingProximityEffectLossesModels>()) {
        json aux;
        to_json(aux, value);
        models.push_back(aux);
    }
    return models;
}

std::vector<std::string> get_all_winding_skin_effect_models() {
    std::vector<std::string> models;
    for (auto& [value, name] : magic_enum::enum_entries<OpenMagnetics::WindingSkinEffectLossesModels>()) {
        json aux;
        to_json(aux, value);
        models.push_back(aux);
    }
    return models;
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

    m.def("get_all_magnetic_field_strength_models", &get_all_magnetic_field_strength_models,
        R"pbdoc(
        Get list of all available magnetic field strength models.

        Returns:
            List of model name strings.
        )pbdoc");

    m.def("get_all_fringing_effect_models", &get_all_fringing_effect_models,
        R"pbdoc(
        Get list of all available fringing effect models.

        Returns:
            List of model name strings.
        )pbdoc");

    m.def("get_all_reluctance_models", &get_all_reluctance_models,
        R"pbdoc(
        Get list of all available reluctance models.

        Returns:
            List of model name strings.
        )pbdoc");

    m.def("get_all_stray_capacitance_models", &get_all_stray_capacitance_models,
        R"pbdoc(
        Get list of all available stray capacitance models.

        Returns:
            List of model name strings.
        )pbdoc");

    m.def("get_all_winding_proximity_effect_models", &get_all_winding_proximity_effect_models,
        R"pbdoc(
        Get list of all available winding proximity effect models.

        Returns:
            List of model name strings.
        )pbdoc");

    m.def("get_all_winding_skin_effect_models", &get_all_winding_skin_effect_models,
        R"pbdoc(
        Get list of all available winding skin effect models.

        Returns:
            List of model name strings.
        )pbdoc");
}

} // namespace PyMKF