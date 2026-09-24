"""Walk every MAS topology schema and prove the converter-spec adapter honours EVERY property.

For each schema in MAS/schemas/inputs/topologies/ this test:
  1. checks the full sample below sets every property the schema defines (the test fails when a schema grows);
  2. adapts it (adapt_converter_spec) and checks the field map names a destination for every top-level and
     operating-point property — none rejected, none silently dropped;
  3. designs it through process_converter (the Kirchhoff design) and
  4. for every property, applies a documented probe: an altered value must change the designed MAS Inputs or the
     ngspice deck ("effect"), a violating value must raise EngineError naming it ("constraint"), or the schema
     itself declares the field inactive for this sample ("inactive", with the schema's own condition).

The MAS schemas are located from $MAS_SCHEMAS_DIR, else the MAS checkout the PyOM build fetched
(build*/_deps/mas-src/schemas). The four properties MAS has no destination for (a DC-resistance or
temperature-rise limit on the magnetic — MAS designRequirements has no such field) must raise the schema-gap
error, and are listed in SCHEMA_GAPS.
"""
import copy
import glob
import json
import math
import os

import pytest

import PyOpenMagnetics as PyMKF


def _schemas_dir():
    env = os.environ.get("MAS_SCHEMAS_DIR")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in sorted(glob.glob(os.path.join(here, "..", "build*", "_deps", "mas-src", "schemas"))):
        if os.path.isdir(os.path.join(cand, "inputs", "topologies")):
            return cand
    raise RuntimeError("MAS schemas not found: set MAS_SCHEMAS_DIR to MAS/schemas")


SCHEMAS = _schemas_dir()


def op(vo, io, fs, **extra):
    d = {"outputVoltages": vo, "outputCurrents": io, "switchingFrequency": fs, "ambientTemperature": 25.0,
         "outputVoltagesType": "dc", "outputCurrentsType": "dc"}
    d.update(extra)
    return d


SAMPLES = {
 "buck": ("buck", {"inputVoltage": {"minimum": 11, "nominal": 12, "maximum": 13}, "diodeVoltageDrop": 0.5,
          "maximumSwitchCurrent": 3.0, "currentRippleRatio": 0.3, "efficiency": 0.95,
          "operatingPoints": [op([5.0], [2.0], 200e3)]}),
 "boost": ("boost", {"inputVoltage": {"minimum": 11, "nominal": 12, "maximum": 13}, "diodeVoltageDrop": 0.5,
          "maximumSwitchCurrent": 6.0, "currentRippleRatio": 0.3, "efficiency": 0.95,
          "operatingPoints": [op([24.0], [1.0], 200e3)]}),
 "flyback": ("flyback", {"inputVoltage": {"minimum": 43, "nominal": 48, "maximum": 53}, "diodeVoltageDrop": 0.6,
          "maximumDrainSourceVoltage": 200.0, "maximumDutyCycle": 0.5, "currentRippleRatio": 0.4, "efficiency": 0.9,
          "operatingPoints": [op([12.0], [2.0], 100e3, mode="continuousConductionMode"),
                              op([12.0], [1.0], 100e3, mode="continuousConductionMode")]}),
 "forward": ("forward", {"inputVoltage": {"minimum": 43, "nominal": 48, "maximum": 53}, "diodeVoltageDrop": 0.6,
          "currentRippleRatio": 0.3, "dutyCycle": 0.42, "maximumSwitchCurrent": 20.0, "efficiency": 0.9,
          "operatingPoints": [op([5.0], [10.0], 200e3)]}),
 "pushPull": ("push_pull", {"inputVoltage": {"minimum": 43, "nominal": 48, "maximum": 53}, "diodeVoltageDrop": 0.6,
          "currentRippleRatio": 0.3, "dutyCycle": 0.45, "maximumSwitchCurrent": 20.0,
          "maximumDrainSourceVoltage": 150.0, "efficiency": 0.9,
          "operatingPoints": [op([12.0], [5.0], 100e3)]}),
 "isolatedBuck": ("isolated_buck", {"inputVoltage": {"minimum": 43, "nominal": 48, "maximum": 53},
          "diodeVoltageDrop": 0.5, "maximumSwitchCurrent": 5.0, "currentRippleRatio": 0.3, "efficiency": 0.9,
          "operatingPoints": [op([12.0, 12.0], [0.5, 0.5], 200e3)]}),
 "isolatedBuckBoost": ("isolated_buck_boost", {"inputVoltage": {"minimum": 22, "nominal": 24, "maximum": 26},
          "diodeVoltageDrop": 0.5, "maximumSwitchCurrent": 8.0, "currentRippleRatio": 0.3, "efficiency": 0.9,
          "operatingPoints": [op([12.0, 12.0], [0.5, 0.5], 200e3)]}),
 "sepic": ("sepic", {"inputVoltage": {"minimum": 11, "nominal": 12, "maximum": 13}, "diodeVoltageDrop": 0.5,
          "maximumSwitchCurrent": 10.0, "currentRippleRatio": 0.3, "efficiency": 0.9, "synchronousRectifier": False,
          "coupledInductor": False, "couplingCoefficient": 0.98, "operatingPoints": [op([12.0], [1.0], 250e3)]}),
 "zeta": ("zeta", {"inputVoltage": {"minimum": 11, "nominal": 12, "maximum": 13}, "diodeVoltageDrop": 0.5,
          "maximumSwitchCurrent": 10.0, "currentRippleRatio": 0.3, "efficiency": 0.9, "synchronousRectifier": False,
          "coupledInductor": False, "couplingCoefficient": 0.98, "operatingPoints": [op([12.0], [1.0], 300e3)]}),
 "cuk": ("cuk", {"inputVoltage": {"minimum": 11, "nominal": 12, "maximum": 13}, "diodeVoltageDrop": 0.5,
          "maximumSwitchCurrent": 10.0, "currentRippleRatio": 0.3, "efficiency": 0.9, "synchronous": True,
          "bidirectional": True, "isolated": False, "coupledInductor": False, "turnsRatio": 1.0,
          "couplingCoefficient": 0.98, "couplingCapacitanceSecondary": 10e-6,
          "operatingPoints": [op([12.0], [1.0], 200e3, powerFlow="forward")]}),
 "fourSwitchBuckBoost": ("fsbb", {"inputVoltage": {"minimum": 22, "nominal": 24, "maximum": 26},
          "maximumSwitchCurrent": 20.0, "currentRippleRatio": 0.3, "outputVoltageRippleRatio": 0.01,
          "efficiency": 0.95, "controlMode": "peakCurrent", "transitionMode": "splitPwm", "bidirectional": False,
          "phaseCount": 1, "transitionHysteresisRatio": 0.15, "operatingPoints": [op([12.0], [5.0], 300e3)]}),
 "weinberg": ("weinberg", {"inputVoltage": {"minimum": 45, "nominal": 50, "maximum": 55}, "diodeVoltageDrop": 0.7,
          "maximumSwitchCurrent": 100.0, "currentRippleRatio": 0.3, "efficiency": 0.95, "variant": "classic",
          "synchronousRectifier": False, "couplingCoefficientInput": 0.999, "couplingCoefficientMain": 0.99,
          "operatingPoints": [op([150.0], [10.0], 50e3)]}),
 "asymmetricHalfBridge": ("ahb", {"inputVoltage": {"minimum": 95, "nominal": 100, "maximum": 105},
          "diodeVoltageDrop": 0.6, "efficiency": 0.9, "rectifierType": "fullBridge", "useLeakageInductance": True,
          "leakageInductance": 2e-6, "magnetizingInductance": 500e-6, "outputInductance": 10e-6,
          "dcBlockingCapacitance": 2e-6, "maximumDutyCycle": 0.5, "inputVoltageStepRange": 10.0,
          "operatingPoints": [op([12.0], [10.0], 100e3, dutyCycle=0.4)]}),
 "llcResonant": ("llc", {"inputVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "minSwitchingFrequency": 80e3, "maxSwitchingFrequency": 125e3, "resonantFrequency": math.sqrt(80e3 * 125e3),
          "inductanceRatio": 5.0, "qualityFactor": 0.4, "efficiency": 0.95, "bridgeType": "halfBridge",
          "rectifierType": "fullBridge", "integratedResonantInductor": True,
          "seriesInductance": 50e-6, "resonantCapacitance": 1.0 / ((2 * math.pi * math.sqrt(80e3 * 125e3)) ** 2 * 50e-6),
          "operatingPoints": [op([24.0], [10.0], 100e3)]}),
 "cllcResonant": ("cllc", {"inputVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "minSwitchingFrequency": 150e3, "maxSwitchingFrequency": 250e3, "qualityFactor": 0.3, "efficiency": 0.95,
          "symmetricDesign": False, "bidirectional": True, "bridgeType": "fullBridge",
          "integratedResonantInductor1": False, "integratedResonantInductor2": False,
          "resonantInductorRatio": 0.95, "resonantCapacitorRatio": 1.05,
          "operatingPoints": [op([48.0], [10.0], 200e3, powerFlow="forward")]}),
 "clllcResonant": ("clllc", {"highVoltageBusVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "lowVoltageBusVoltage": {"minimum": 46, "nominal": 48, "maximum": 50},
          "minSwitchingFrequency": 150e3, "maxSwitchingFrequency": 250e3, "primaryResonantFrequency": 200e3,
          "inductanceRatioK": 4.45, "qualityFactor": 0.4, "tankSymmetryRatio": 1.0, "efficiency": 0.95,
          "bridgeTypePrimary": "fullBridge", "bridgeTypeSecondary": "fullBridge", "controlStrategy": "hybridPfmPsm",
          "integratedResonantInductors": False,
          "primarySeriesInductance": 30e-6, "primaryResonantCapacitance": 1.0 / ((2 * math.pi * 200e3) ** 2 * 30e-6),
          "operatingPoints": [op([48.0], [10.0], 200e3, powerFlowDirection="forward", phaseShiftDegrees=0.0)]}),
 "seriesResonant": ("src", {"inputVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "minSwitchingFrequency": 100e3, "maxSwitchingFrequency": 130e3, "resonantFrequency": 110e3,
          "qualityFactor": 2.0, "efficiency": 0.95, "bridgeType": "fullBridge", "rectifierType": "fullBridgeDiode",
          "isolated": True, "useSynchronousRectifier": False,
          "seriesInductance": 60e-6, "resonantCapacitance": 1.0 / ((2 * math.pi * 110e3) ** 2 * 60e-6),
          "operatingPoints": [op([48.0], [10.0], 110e3)]}),
 "dualActiveBridge": ("dab", {"inputVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "efficiency": 0.95, "seriesInductance": 0, "useLeakageInductance": True, "perSecondaryLeakage": [],
          "operatingPoints": [op([48.0], [40.0], 80e3, modulationType="TPS", innerPhaseShift1=0.0,
                                innerPhaseShift2=0.0, innerPhaseShift3=30.0)]}),
 "phaseShiftedFullBridge": ("psfb", {"inputVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "efficiency": 0.95, "seriesInductance": 0, "useLeakageInductance": True, "outputInductance": 0,
          "rectifierType": "fullBridge", "maximumPhaseShift": 0.8,
          "operatingPoints": [op([24.0], [50.0], 100e3, phaseShift=120.0)]}),
 "phaseShiftedHalfBridge": ("pshb", {"inputVoltage": {"minimum": 380, "nominal": 400, "maximum": 420},
          "efficiency": 0.95, "seriesInductance": 0, "useLeakageInductance": True, "outputInductance": 0,
          "rectifierType": "fullBridge", "maximumPhaseShift": 0.8,
          "operatingPoints": [op([24.0], [50.0], 100e3, phaseShift=120.0)]}),
 "powerFactorCorrection": ("pfc", {"inputVoltage": {"minimum": 200, "nominal": 230, "maximum": 260},
          "outputVoltage": 400.0, "outputPower": 500.0, "lineFrequency": 50.0, "switchingFrequency": 100e3,
          "currentRippleRatio": 0.2, "efficiency": 0.95, "mode": "continuousConductionMode",
          "topologyVariant": "boost", "numberOfPhases": 1, "wideBandgapSwitch": False, "bulkCapacitance": 330e-6,
          "diodeVoltageDrop": 1.0, "maximumSwitchCurrent": 20.0, "maximumCoreTemperatureRise": 40.0,
          "ambientTemperature": 25.0}),
 "vienna": ("vienna", {"lineToLineVoltage": {"minimum": 380, "nominal": 400, "maximum": 420}, "lineFrequency": 50.0,
          "outputDcVoltage": 800.0, "switchingFrequency": 70e3, "currentRippleRatio": 0.3, "powerFactor": 0.99,
          "efficiency": 0.97, "viennaVariant": "viennaI", "switchType": "tType", "synchronousRectifier": False,
          "phaseCount": 1, "samplingStrategy": "peakOfLineOnly",
          "operatingPoints": [op([800.0], [12.5], 70e3)]}),
 "commonModeChoke": ("common_mode_choke", {"operatingVoltage": {"nominal": 230}, "operatingCurrent": 6.0,
          "lineFrequency": 50.0, "minimumImpedance": [{"frequency": 150e3, "impedance": {"magnitude": 1000.0}}],
          "targetInsertionLoss": [{"frequency": 1e6, "insertionLoss": 30.0}], "lineImpedance": 50.0,
          "maximumDcResistance": 0.05, "maximumLeakageInductance": 5e-6, "ambientTemperature": 25.0}),
 "differentialModeChoke": ("differential_mode_choke", {"inputVoltage": {"nominal": 230}, "operatingCurrent": 6.0,
          "peakCurrent": 8.0, "configuration": "singlePhase", "lineFrequency": 50.0, "minimumInductance": 100e-6,
          "filterCapacitance": 1e-6, "minimumImpedance": [{"frequency": 150e3, "impedance": {"magnitude": 50.0}}],
          "targetAttenuation": [{"frequency": 150e3, "attenuation": 40.0}], "switchingFrequency": 100e3,
          "maximumDcResistance": 0.05, "maximumCoreTemperatureRise": 40.0, "ambientTemperature": 25.0}),
 "currentTransformer": ("current_transformer", {"waveformLabel": "sinusoidal", "maximumPrimaryCurrentPeak": 10.0,
          "frequency": 50e3, "maximumDutyCycle": 0.5, "burdenResistor": 10.0, "diodeVoltageDrop": 0.7,
          "ambientTemperature": 25.0}),
}


# Properties MAS has no destination for: they must raise the schema-gap error (never be dropped).
SCHEMA_GAPS = {("commonModeChoke", "maximumDcResistance"), ("differentialModeChoke", "maximumDcResistance"),
               ("differentialModeChoke", "maximumCoreTemperatureRise"),
               ("powerFactorCorrection", "maximumCoreTemperatureRise")}

# Probe per property: ("effect", altered value) | ("constraint", violating value) | ("inactive", reason).
# Operating-point properties are written "operatingPoints[].<name>".
PROBES = {
    "buck": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 1.0),
             "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8)},
    "boost": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 1.5),
              "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8)},
    "flyback": {"diodeVoltageDrop": ("effect", 1.2), "maximumDrainSourceVoltage": ("constraint", 60.0),
                "maximumDutyCycle": ("effect", 0.35), "currentRippleRatio": ("effect", 0.2),
                "efficiency": ("effect", 0.8), "operatingPoints[].mode": ("effect", "discontinuousConductionMode")},
    "forward": {"diodeVoltageDrop": ("effect", 1.2), "currentRippleRatio": ("effect", 0.1),
                "dutyCycle": ("effect", 0.35), "maximumSwitchCurrent": ("constraint", 1.0),
                "efficiency": ("effect", 0.8)},
    "pushPull": {"diodeVoltageDrop": ("effect", 1.2), "currentRippleRatio": ("effect", 0.1),
                 "dutyCycle": ("effect", 0.35), "maximumSwitchCurrent": ("constraint", 0.5),
                 "maximumDrainSourceVoltage": ("constraint", 60.0), "efficiency": ("effect", 0.8)},
    "isolatedBuck": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 0.5),
                     "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8)},
    "isolatedBuckBoost": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 0.5),
                          "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8)},
    "sepic": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 0.5),
              "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8),
              "synchronousRectifier": ("effect", True), "coupledInductor": ("effect", True),
              "couplingCoefficient": ("inactive", "the schema uses it only when coupledInductor=true")},
    "zeta": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 0.5),
             "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8),
             "synchronousRectifier": ("effect", True), "coupledInductor": ("effect", True),
             "couplingCoefficient": ("inactive", "the schema uses it only when coupledInductor=true")},
    "cuk": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 0.5),
            "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8),
            "synchronous": ("constraint", False),
            "bidirectional": ("inactive", "only a reverse operating point depends on it (reverse + bidirectional=false is refused)"),
            "isolated": ("effect", True), "coupledInductor": ("effect", True),
            "turnsRatio": ("inactive", "the schema: ignored for non-isolated variants"),
            "couplingCoefficient": ("inactive", "the schema uses it only when coupledInductor=true"),
            "couplingCapacitanceSecondary": ("inactive", "the schema uses it only when isolated=true"),
            "operatingPoints[].powerFlow": ("effect", "reverse")},
    "fourSwitchBuckBoost": {"maximumSwitchCurrent": ("constraint", 1.0), "currentRippleRatio": ("effect", 0.1),
                            "outputVoltageRippleRatio": ("effect", 0.002), "efficiency": ("effect", 0.8),
                            "controlMode": ("constraint", "averageCurrent"),
                            "transitionMode": ("inactive", "the buck-boost band only; this 24 V -> 12 V point is in the buck region"),
                            "bidirectional": ("inactive", "a capability flag: the schema's operating points cannot request reverse flow"),
                            "phaseCount": ("effect", 2),
                            "transitionHysteresisRatio": ("inactive", "the band edge only; 24 V -> 12 V is far from it")},
    "weinberg": {"diodeVoltageDrop": ("effect", 1.2), "maximumSwitchCurrent": ("constraint", 1.0),
                 "currentRippleRatio": ("effect", 0.1), "efficiency": ("effect", 0.8),
                 "variant": ("effect", "bridge"), "synchronousRectifier": ("effect", True),
                 "couplingCoefficientInput": ("effect", 0.99), "couplingCoefficientMain": ("effect", 0.95)},
    "asymmetricHalfBridge": {"diodeVoltageDrop": ("effect", 1.2), "efficiency": ("effect", 0.8),
                             "rectifierType": ("effect", "centerTapped"), "useLeakageInductance": ("effect", False),
                             "leakageInductance": ("effect", 5e-6), "magnetizingInductance": ("effect", 800e-6),
                             "outputInductance": ("effect", 20e-6), "dcBlockingCapacitance": ("effect", 5e-6),
                             "maximumDutyCycle": ("constraint", 0.3), "inputVoltageStepRange": ("effect", 30.0),
                             "operatingPoints[].dutyCycle": ("effect", 0.3)},
    # resonantFrequency pins the band centre, so moving one band edge alone is a contradiction.
    "llcResonant": {"minSwitchingFrequency": ("constraint", 70e3), "maxSwitchingFrequency": ("constraint", 140e3),
                    "resonantFrequency": ("constraint", 150e3), "inductanceRatio": ("effect", 7.0),
                    "qualityFactor": ("effect", 0.5), "efficiency": ("effect", 0.8),
                    "bridgeType": ("effect", "fullBridge"), "rectifierType": ("effect", "centerTapped"),
                    "integratedResonantInductor": ("effect", False), "seriesInductance": ("effect", 60e-6),
                    "resonantCapacitance": ("effect", 60e-9),
                    "operatingPoints[].switchingFrequency": ("effect", "scale:1.1")},   # still inside the band
    "cllcResonant": {"minSwitchingFrequency": ("constraint", 210e3), "maxSwitchingFrequency": ("constraint", 190e3),
                     "qualityFactor": ("effect", 0.5), "efficiency": ("effect", 0.8),
                     "symmetricDesign": ("constraint", True), "bidirectional": ("inactive", "only a reverse operating point depends on it"),
                     "bridgeType": ("constraint", "halfBridge"), "integratedResonantInductor1": ("effect", True),
                     "integratedResonantInductor2": ("effect", True), "resonantInductorRatio": ("effect", 1.0),
                     "resonantCapacitorRatio": ("effect", 1.0), "operatingPoints[].powerFlow": ("effect", "reverse")},
    "clllcResonant": {"highVoltageBusVoltage": ("effect", {"minimum": 360, "nominal": 380, "maximum": 400}),
                      "lowVoltageBusVoltage": ("constraint", {"nominal": 40}),
                      "minSwitchingFrequency": ("constraint", 210e3), "maxSwitchingFrequency": ("constraint", 190e3),
                      "primaryResonantFrequency": ("constraint", 180e3), "inductanceRatioK": ("effect", 6.0),
                      "qualityFactor": ("inactive", "the schema: primarySeriesInductance/primaryResonantCapacitance override the Q derivation"),
                      "tankSymmetryRatio": ("constraint", 1.2), "efficiency": ("effect", 0.8),
                      "bridgeTypePrimary": ("constraint", "halfBridge"), "bridgeTypeSecondary": ("constraint", "halfBridge"),
                      "controlStrategy": ("constraint", "psm"), "integratedResonantInductors": ("effect", True),
                      # both are given: moving one alone detunes the tank off the operating frequency
                      "primarySeriesInductance": ("constraint", 40e-6), "primaryResonantCapacitance": ("constraint", 30e-9),
                      "operatingPoints[].powerFlowDirection": ("effect", "reverse"),
                      "operatingPoints[].phaseShiftDegrees": ("constraint", 20.0),
                      # the tank resonates at primaryResonantFrequency, which must be the operating frequency
                      "operatingPoints[].switchingFrequency": ("constraint", "scale:1.2"),
                      "operatingPoints[].outputVoltages": ("constraint", "scale:1.1")},   # must equal lowVoltageBusVoltage
    "seriesResonant": {"minSwitchingFrequency": ("constraint", 115e3), "maxSwitchingFrequency": ("constraint", 105e3),
                       "resonantFrequency": ("constraint", 100e3),
                       "qualityFactor": ("inactive", "the schema: seriesInductance/resonantCapacitance override the Q derivation"),
                       "efficiency": ("effect", 0.8), "bridgeType": ("effect", "halfBridge"),
                       "rectifierType": ("effect", "centerTappedDiode"), "isolated": ("constraint", False),
                       "useSynchronousRectifier": ("constraint", True),
                       # both are given: moving one alone detunes the tank off the operating frequency
                       "seriesInductance": ("constraint", 70e-6), "resonantCapacitance": ("constraint", 25e-9),
                       "operatingPoints[].switchingFrequency": ("constraint", "scale:1.2")},   # out of the band
    # seriesInductance = 0 means "use the transformer leakage", so useLeakageInductance=false contradicts it.
    "dualActiveBridge": {"efficiency": ("effect", 0.8), "seriesInductance": ("effect", 50e-6),
                         "useLeakageInductance": ("constraint", False), "perSecondaryLeakage": ("constraint", [1e-6, 2e-6]),
                         "operatingPoints[].modulationType": ("constraint", "DPS"),   # DPS needs D1 = D2 > 0
                         "operatingPoints[].innerPhaseShift1": ("effect", 10.0),
                         "operatingPoints[].innerPhaseShift2": ("effect", 10.0),
                         "operatingPoints[].innerPhaseShift3": ("effect", 40.0)},
    "phaseShiftedFullBridge": {"efficiency": ("effect", 0.8), "seriesInductance": ("effect", 5e-6),
                               "useLeakageInductance": ("constraint", False), "outputInductance": ("effect", 20e-6),
                               "rectifierType": ("effect", "centerTapped"), "maximumPhaseShift": ("constraint", 0.5),
                               "operatingPoints[].phaseShift": ("effect", 140.0)},
    "phaseShiftedHalfBridge": {"efficiency": ("effect", 0.8), "seriesInductance": ("effect", 5e-6),
                               "useLeakageInductance": ("constraint", False), "outputInductance": ("effect", 20e-6),
                               "rectifierType": ("effect", "centerTapped"), "maximumPhaseShift": ("constraint", 0.5),
                               "operatingPoints[].phaseShift": ("effect", 140.0)},
    "powerFactorCorrection": {"inputVoltage": ("effect", {"minimum": 180, "nominal": 220, "maximum": 260}),
                              "outputVoltage": ("effect", 380.0), "outputPower": ("effect", 400.0),
                              "lineFrequency": ("effect", 60.0), "switchingFrequency": ("effect", 80e3),
                              "currentRippleRatio": ("effect", 0.3), "efficiency": ("effect", 0.8),
                              "mode": ("effect", "criticalConductionMode"), "topologyVariant": ("effect", "sepic"),
                              "numberOfPhases": ("constraint", 2),
                              "wideBandgapSwitch": ("inactive", "the schema: required only for a CCM totem-pole"),
                              "bulkCapacitance": ("effect", 470e-6), "diodeVoltageDrop": ("effect", 1.5),
                              "maximumSwitchCurrent": ("constraint", 1.0), "ambientTemperature": ("effect", 40.0)},
    "vienna": {"lineToLineVoltage": ("effect", {"minimum": 360, "nominal": 380, "maximum": 400}),
               "lineFrequency": ("effect", 60.0), "outputDcVoltage": ("constraint", 700.0),
               # the top-level switchingFrequency and the operating points' must agree
               "switchingFrequency": ("constraint", 50e3), "currentRippleRatio": ("effect", 0.2),
               "operatingPoints[].switchingFrequency": ("constraint", "scale:1.2"),
               "operatingPoints[].outputVoltages": ("constraint", "scale:1.1"),   # must equal outputDcVoltage
               "powerFactor": ("effect", 0.9), "efficiency": ("effect", 0.8), "viennaVariant": ("constraint", "viennaII"),
               "switchType": ("constraint", "backToBackMosfet"), "synchronousRectifier": ("constraint", True),
               "phaseCount": ("effect", 2), "samplingStrategy": ("effect", "fullLineCycle")},
    "commonModeChoke": {"operatingVoltage": ("effect", {"nominal": 120}), "operatingCurrent": ("effect", 10.0),
                        "lineFrequency": ("effect", 60.0),
                        "minimumImpedance": ("effect", [{"frequency": 150e3, "impedance": {"magnitude": 2000.0}}]),
                        "targetInsertionLoss": ("effect", [{"frequency": 1e6, "insertionLoss": 40.0}]),
                        "lineImpedance": ("effect", 100.0), "maximumLeakageInductance": ("effect", 2e-6),
                        "ambientTemperature": ("effect", 40.0)},
    "differentialModeChoke": {"inputVoltage": ("inactive", "sizes the LC only through the load impedance, which a pinned "
                                               "minimumInductance above the LC value overrides"),
                              "operatingCurrent": ("effect", 10.0), "peakCurrent": ("effect", 12.0),
                              "configuration": ("effect", "singlePhaseBalanced"), "lineFrequency": ("effect", 60.0),
                              "minimumInductance": ("effect", 2e-3), "filterCapacitance": ("effect", 2e-6),
                              "minimumImpedance": ("effect", [{"frequency": 150e3, "impedance": {"magnitude": 80.0}}]),
                              "targetAttenuation": ("effect", [{"frequency": 150e3, "attenuation": 60.0}]),
                              "switchingFrequency": ("effect", 150e3), "ambientTemperature": ("effect", 40.0)},
    "currentTransformer": {"waveformLabel": ("effect", "unipolarRectangular"), "maximumPrimaryCurrentPeak": ("effect", 20.0),
                           "frequency": ("effect", 100e3),
                           "maximumDutyCycle": ("inactive", "the schema's duty applies to unipolar waveforms; this sample is sinusoidal"),
                           "burdenResistor": ("effect", 20.0), "diodeVoltageDrop": ("effect", 1.0),
                           "ambientTemperature": ("effect", 40.0)},
}
COMMON_EFFECTS = {"inputVoltage": ("effect", "scale:0.9"), "operatingPoints[].outputVoltages": ("effect", "scale:1.1"),
                  "operatingPoints[].outputCurrents": ("effect", "scale:1.3"),
                  "operatingPoints[].switchingFrequency": ("effect", "scale:1.2"),
                  "operatingPoints[].ambientTemperature": ("effect", 60.0),
                  "operatingPoints[].outputVoltagesType": ("constraint", "rms"),
                  "operatingPoints[].outputCurrentsType": ("constraint", "peak")}


def _schema_props(schema):
    j = json.load(open(os.path.join(SCHEMAS, "inputs", "topologies", schema + ".json")))
    top = set(j["properties"])
    opp = set()
    if "operatingPoints" in j["properties"]:
        base = json.load(open(os.path.join(SCHEMAS, "utils.json")))["$defs"]["baseOperatingPoint"]["properties"]
        ref = j["properties"]["operatingPoints"]["items"]["$ref"].split("/")[-1]
        d = j["$defs"][ref]
        opp |= set(d.get("properties", {}))
        if "allOf" in d or d.get("$ref", "").endswith("baseOperatingPoint"):
            opp |= set(base)
    return top, opp


def _without_gaps(schema, spec):
    s = copy.deepcopy(spec)
    for g in SCHEMA_GAPS:
        if g[0] == schema:
            s.pop(g[1], None)
    return s


def _design(topo, spec):
    """Designed MAS Inputs (+ the ngspice deck where the topology has one) as one comparable string."""
    if topo == "current_transformer":
        s = copy.deepcopy(spec)
        return json.dumps(PyMKF.process_current_transformer(s, 0.01, 0.0), sort_keys=True)
    out = json.dumps(PyMKF.process_converter(topo, spec, use_ngspice=False), sort_keys=True)
    if topo not in ("common_mode_choke", "differential_mode_choke"):
        out += PyMKF.generate_ngspice_circuit(topo, spec, [], 0.0, 0, 0, "", {})["netlist"]
    return out


def _altered(spec, name, value):
    s = copy.deepcopy(spec)
    if name.startswith("operatingPoints[]."):
        key = name.split(".", 1)[1]
        for o in s["operatingPoints"]:
            v = o[key]
            if isinstance(value, str) and value.startswith("scale:"):
                k = float(value.split(":")[1])
                o[key] = [x * k for x in v] if isinstance(v, list) else v * k
            else:
                o[key] = value
    else:
        v = s[name]
        if isinstance(value, str) and value.startswith("scale:"):
            k = float(value.split(":")[1])
            s[name] = {b: x * k for b, x in v.items()} if isinstance(v, dict) else v * k
        else:
            s[name] = value
    return s


@pytest.mark.parametrize("schema", sorted(SAMPLES))
def test_schema_walk(schema):
    topo, spec = SAMPLES[schema]
    top, opp = _schema_props(schema)
    # 1. the sample sets every schema property
    assert not (top - set(spec)), f"{schema}: sample misses {sorted(top - set(spec))}"
    ops = spec.get("operatingPoints", [])
    op_fields = {k for o in ops for k in o}
    assert not (opp - op_fields), f"{schema}: sample operating points miss {sorted(opp - op_fields)}"
    # schema gaps raise the gap error, naming the field (each one on its own)
    spec_no_gaps = _without_gaps(schema, spec)
    for g in SCHEMA_GAPS:
        if g[0] == schema:
            with pytest.raises(PyMKF.EngineError, match=g[1] + ".*schema gap"):
                _design(topo, dict(spec_no_gaps, **{g[1]: spec[g[1]]}))
    spec = spec_no_gaps
    # 2. every property mapped
    mapped = PyMKF.adapt_converter_spec(topo, spec)["fieldMap"]
    for p in spec:
        assert p in mapped, f"{schema}.{p} not mapped"
    if topo not in ("common_mode_choke", "differential_mode_choke", "current_transformer"):
        for p in op_fields:
            assert "operatingPoints[]." + p in mapped, f"{schema}.operatingPoints[].{p} not mapped"
    # 3. the full spec designs
    base = _design(topo, spec)
    # 4. every property probed
    probes = dict(COMMON_EFFECTS)
    probes.update(PROBES[schema])
    names = [p for p in spec if p != "operatingPoints"] + ["operatingPoints[]." + p for p in op_fields]
    for name in names:
        assert name in probes, f"{schema}: no probe for {name}"
        kind, value = probes[name]
        if kind == "inactive":
            continue
        altered = _altered(spec, name, value)
        if kind == "constraint":
            with pytest.raises(PyMKF.EngineError):
                _design(topo, altered)
        else:
            try:
                changed = _design(topo, altered) != base
            except PyMKF.EngineError as e:
                pytest.fail(f"{schema}.{name} = {value!r} should change the design, raised: {e}")
            assert changed, f"{schema}.{name} = {value!r} changed nothing (silently dropped?)"
