# PyOpenMagnetics - Complete AI Assistant Guide

> **📍 Location**: This file is bundled with PyOpenMagnetics and can be found at:
> - In the package: `PyOpenMagnetics/AGENTS.md`
> - GitHub: https://github.com/OpenMagnetics/PyOpenMagnetics/blob/main/AGENTS.md

## ⚠️ IMPORTANT: Avoid Manual Mode

**ALWAYS use the PyOpenMagnetics API methods rather than manual calculations.**

❌ **Don't do this:**
- Calculate turns ratios, inductance, or gaps manually using textbook formulas
- Hardcode core selections based on power ratings alone
- Assume standard formulas apply without validation

✅ **Do this instead:**
- Use `process_flyback()`, `process_buck()`, etc. to calculate specifications automatically
- Use `calculate_advised_magnetics()` to get ranked design recommendations
- Use `design_magnetics_from_converter()` for complete converter-to-magnetic design

**Why:** The MKF engine accounts for:
- Complex magnetic field distributions
- Temperature-dependent material properties
- Geometrical fringing effects
- Core database constraints
- Optimal gap calculations for target inductance

If API calls fail, **check the Troubleshooting section below** and fix the API usage rather than falling back to manual mode.

## Overview

PyOpenMagnetics is a Python wrapper for the OpenMagnetics MKF (Magnetics Knowledge Foundation) C++ engine. It provides comprehensive tools for designing, simulating, and optimizing magnetic components (transformers, inductors, chokes) for power electronics.

**Architecture:**
```
User Application
    ↓
PyOpenMagnetics (Python API)
    ↓
MKF C++ Engine (via pybind11)
    ↓
MAS JSON Schema (data structures)
```

---

## Installation

```bash
pip install PyOpenMagnetics
```

### ⚠️ CRITICAL: Module Import Instructions

**The standard `import PyOpenMagnetics` may not work** due to the compiled extension module (.so/.pyd file) structure. You have three options:

**Option 1: Direct importlib loading (Recommended)**
```python
import importlib.util

# Find the .so file path (adjust for your Python version and platform)
so_path = '/path/to/site-packages/PyOpenMagnetics/PyOpenMagnetics.cpython-311-x86_64-linux-gnu.so'

spec = importlib.util.spec_from_file_location('PyOpenMagnetics', so_path)
PyOpenMagnetics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PyOpenMagnetics)

# Now use normally
PyOpenMagnetics.load_databases({})
```

**Option 2: Create __init__.py in package directory**
Create this file in `site-packages/PyOpenMagnetics/__init__.py`:
```python
import os
import importlib.util

so_file = os.path.join(os.path.dirname(__file__), 
                       'PyOpenMagnetics.cpython-311-x86_64-linux-gnu.so')
spec = importlib.util.spec_from_file_location('PyOpenMagnetics', so_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

for attr_name in dir(module):
    if not attr_name.startswith('_'):
        globals()[attr_name] = getattr(module, attr_name)
```

**Option 3: Load databases explicitly**
```python
import PyOpenMagnetics
PyOpenMagnetics.load_databases({})  # Required if databases not auto-loaded
```

**Verifying installation:**
```python
PyOpenMagnetics.load_databases({})
print(f"Materials: {len(PyOpenMagnetics.get_core_materials())}")
print(f"Shapes: {len(PyOpenMagnetics.get_core_shapes())}")
# Should show: Materials: 400+, Shapes: 1300+
```

**Accessing this guide after installation:**
```python
import PyOpenMagnetics
import inspect
import os

# Get the path to AGENTS.md
module_path = os.path.dirname(inspect.getfile(PyOpenMagnetics))
agents_md_path = os.path.join(module_path, "AGENTS.md")
print(f"AGENTS.md location: {agents_md_path}")
```

---

## Complete API Reference by Category

### 1. DATABASE ACCESS FUNCTIONS

#### Core Materials
```python
# List all materials
materials = PyOpenMagnetics.get_core_materials()  # Returns list of full material objects
names = PyOpenMagnetics.get_core_material_names()  # Returns list of names only

# Filter by manufacturer
ferroxcube = PyOpenMagnetics.get_core_material_names_by_manufacturer("Ferroxcube")
tdk = PyOpenMagnetics.get_core_material_names_by_manufacturer("TDK")
magnetics = PyOpenMagnetics.get_core_material_names_by_manufacturer("Magnetics")

# Find specific material
material = PyOpenMagnetics.find_core_material_by_name("3C95")

# Get material properties
mu = PyOpenMagnetics.get_material_permeability("3C95", temperature=25, dc_bias=0, frequency=100000)
rho = PyOpenMagnetics.get_material_resistivity("3C95", temperature=25)
steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients(material, frequency=100000)
# Returns: {k, alpha, beta, minimumFrequency, maximumFrequency, ct0, ct1, ct2}

# Temperature-dependent parameters
params = PyOpenMagnetics.get_core_temperature_dependant_parameters(core, temperature=80)
# Returns: {magneticFluxDensitySaturation, initialPermeability, effectivePermeability, 
#           reluctance, permeance, resistivity}
```

#### Core Shapes
```python
# List all shapes
shapes = PyOpenMagnetics.get_core_shapes()  # Full shape objects
names = PyOpenMagnetics.get_core_shape_names(include_toroidal=True)  # Names only
families = PyOpenMagnetics.get_core_shape_families()  # ['E', 'ETD', 'PQ', 'RM', 'T', ...]

# Find specific shape
shape = PyOpenMagnetics.find_core_shape_by_name("E 42/21/15")
shape = PyOpenMagnetics.find_core_shape_by_name("ETD 34")
shape = PyOpenMagnetics.find_core_shape_by_name("PQ 26/20")

# Get shape data
shape_data = PyOpenMagnetics.get_shape_data(shape)
```

#### Wires
```python
# List all wires
wires = PyOpenMagnetics.get_wires()  # Full wire objects
names = PyOpenMagnetics.get_wire_names()  # Names only

# Wire types and standards
types = PyOpenMagnetics.get_available_wire_types()  # ['round', 'litz', 'rectangular', 'foil']
standards = PyOpenMagnetics.get_available_wire_standards()  # ['IEC 60317', 'NEMA MW 1000', ...]

# Find wires
wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
wire = PyOpenMagnetics.find_wire_by_dimension(0.0005, "round", "IEC 60317")

# Get wire data
wire_data = PyOpenMagnetics.get_wire_data(wire)
wire_data_by_name = PyOpenMagnetics.get_wire_data_by_name("Round 0.5 - Grade 1")
wire_data_by_standard = PyOpenMagnetics.get_wire_data_by_standard_name("some_standard_name")

# Wire dimensions
outer_d = PyOpenMagnetics.get_wire_outer_diameter_enamelled_round(wire)
outer_dims = PyOpenMagnetics.get_outer_dimensions(wire)  # Works for any type
outer_d_litz = PyOpenMagnetics.get_wire_outer_diameter_bare_litz(wire)
outer_d_insulated_litz = PyOpenMagnetics.get_wire_outer_diameter_insulated_litz(wire)
outer_d_rect_h = PyOpenMagnetics.get_wire_outer_height_rectangular(wire)
outer_d_rect_w = PyOpenMagnetics.get_wire_outer_width_rectangular(wire)

# Get equivalent wire (different grade/size)
equiv_wire = PyOpenMagnetics.get_equivalent_wire(wire, target_grade="Grade 2")

# Get strand by standard (for litz)
strand = PyOpenMagnetics.get_strand_by_standard_name("IEC 60317 Grade 1 0.1mm")
conducting_d = PyOpenMagnetics.get_wire_conducting_diameter_by_standard_name("IEC 60317 Grade 1 0.1mm")
```

#### Wire Materials
```python
materials = PyOpenMagnetics.get_wire_materials()
names = PyOpenMagnetics.get_wire_material_names()
material = PyOpenMagnetics.find_wire_material_by_name("Copper")
```

#### Bobbins
```python
bobbins = PyOpenMagnetics.get_bobbins()
names = PyOpenMagnetics.get_bobbin_names()
bobbin = PyOpenMagnetics.find_bobbin_by_name("E 42/21/15 Bobbin")
bobbin_data = PyOpenMagnetics.calculate_bobbin_data(bobbin)
```

#### Insulation Materials
```python
materials = PyOpenMagnetics.get_insulation_materials()
names = PyOpenMagnetics.get_insulation_material_names()
material = PyOpenMagnetics.find_insulation_material_by_name("Kapton")
```

---

### 2. CORE CALCULATIONS

```python
# Calculate complete core data (adds processedDescription, geometricalDescription)
core = PyOpenMagnetics.calculate_core_data(core_functional_description, include_material_data=False)

# Get effective parameters
Ae = core["processedDescription"]["effectiveParameters"]["effectiveArea"]  # m²
le = core["processedDescription"]["effectiveParameters"]["effectiveLength"]  # m
Ve = core["processedDescription"]["effectiveParameters"]["effectiveVolume"]  # m³

# Geometrical description
geom = PyOpenMagnetics.calculate_core_geometrical_description(core)

# Processed description
processed = PyOpenMagnetics.calculate_core_processed_description(core)

# Maximum magnetic energy
E_max = PyOpenMagnetics.calculate_core_maximum_magnetic_energy(core, operating_point)

# Saturation current (requires complete magnetic)
I_sat = PyOpenMagnetics.calculate_saturation_current(magnetic, temperature=25)
```

---

### 3. INDUCTANCE CALCULATIONS

```python
# Available models: "ZHANG", "MUEHLETHALER", "PARTRIDGE", "EFFECTIVE_AREA", 
#                   "EFFECTIVE_LENGTH", "STENGLEIN", "BALAKRISHNAN", "CLASSIC"
models = {"reluctance": "ZHANG"}

# Calculate inductance from turns and gap
L = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
    core, coil, operating_point, models
)

# Calculate turns from inductance and gap
N = PyOpenMagnetics.calculate_number_turns_from_gapping_and_inductance(
    core, inputs, models
)

# Calculate gap from turns and inductance
core_with_gap = PyOpenMagnetics.calculate_gapping_from_number_turns_and_inductance(
    core, coil, inputs,
    gapping_type="SUBTRACTIVE",  # or "ADDITIVE", "DISTRIBUTED"
    decimals=4
)

# Calculate number of turns from voltage and frequency
N = PyOpenMagnetics.calculate_number_turns(core, operating_point, models)

# Gap reluctance
gap_result = PyOpenMagnetics.calculate_gap_reluctance(gap_data, "ZHANG")
# Returns: {reluctance, fringingFactor}

# Inductance matrix (for multi-winding)
L_matrix = PyOpenMagnetics.calculate_inductance_matrix(magnetic, operating_point)
```

---

### 4. LOSS CALCULATIONS

#### Core Losses
```python
# Available models: "STEINMETZ", "IGSE", "MSE", "BARG", "ROSHEN", "ALBACH", "PROPRIETARY"
models = {
    "coreLosses": "IGSE",
    "reluctance": "ZHANG", 
    "coreTemperature": "MANIKTALA"
}

losses = PyOpenMagnetics.calculate_core_losses(core, coil, inputs, models)
# Returns:
# {
#   coreLosses: float (Watts),
#   magneticFluxDensityPeak: float (Tesla),
#   magneticFluxDensityAcPeak: float (Tesla),
#   voltageRms: float (Volts),
#   currentRms: float (Amperes),
#   apparentPower: float (VA),
#   maximumCoreTemperature: float (Celsius),
#   maximumCoreTemperatureRise: float (Kelvin)
# }

# Get model documentation
model_info = PyOpenMagnetics.get_core_losses_model_information(material)
```

#### Winding Losses
```python
# Complete winding losses (DC + skin + proximity)
winding_losses = PyOpenMagnetics.calculate_winding_losses(magnetic, operating_point, temperature=25)
# Returns:
# {
#   windingLosses: float (total Watts),
#   windingLossesPerWinding: [float, ...],
#   ohmicLosses: {...},
#   skinEffectLosses: {...},
#   proximityEffectLosses: {...}
# }

# Individual components
ohmic = PyOpenMagnetics.calculate_ohmic_losses(coil, operating_point, temperature)
skin = PyOpenMagnetics.calculate_skin_effect_losses(coil, winding_losses, temperature)

# Proximity effect (requires field calculation first)
field = PyOpenMagnetics.calculate_magnetic_field_strength_field(operating_point, magnetic)
prox = PyOpenMagnetics.calculate_proximity_effect_losses(coil, temperature, winding_losses, field)
```

#### Wire-Level Losses
```python
# Per-meter calculations
R_dc = PyOpenMagnetics.calculate_dc_resistance_per_meter(wire, temperature)
P_dc = PyOpenMagnetics.calculate_dc_losses_per_meter(wire, current, temperature)
P_skin = PyOpenMagnetics.calculate_skin_ac_losses_per_meter(wire, current, temperature)
R_ac = PyOpenMagnetics.calculate_skin_ac_resistance_per_meter(wire, current, temperature)

# AC factor (Rac/Rdc)
Fr = PyOpenMagnetics.calculate_skin_ac_factor(wire, current, temperature)

# Effective current density
J_eff = PyOpenMagnetics.calculate_effective_current_density(wire, current, temperature)

# Skin depth
delta = PyOpenMagnetics.calculate_effective_skin_depth("copper", current, temperature)

# Per-winding DC resistance
R_dc_winding = PyOpenMagnetics.calculate_dc_resistance_per_winding(coil, temperature)

# Resistance matrix
R_matrix = PyOpenMagnetics.calculate_resistance_matrix(coil, operating_point, temperature)
```

---

### 5. WINDING ENGINE

```python
# Main winding function - places turns in winding window
coil_wound = PyOpenMagnetics.wind(
    coil,                        # Coil with functional description
    repetitions=2,               # Pattern repetitions
    proportion_per_winding=[0.5, 0.5],  # Window share per winding
    pattern=[0, 1],              # Interleaving: P-S-P-S (winding indices)
    margin_pairs=[[0.001, 0.001]]  # Margin tape [left, right] per winding in meters
)
# Result contains:
# - functionalDescription (input)
# - sectionsDescription (coarse level)
# - layersDescription (layer level)
# - turnsDescription (individual turns with coordinates)

# Alternative winding approaches
coil_sections = PyOpenMagnetics.wind_by_sections(
    coil, repetitions, proportions, pattern, insulation_thickness
)
coil_layers = PyOpenMagnetics.wind_by_layers(coil, insulation_layers, insulation_thickness)
coil_turns = PyOpenMagnetics.wind_by_turns(coil)

# Planar (PCB) winding
coil_planar = PyOpenMagnetics.wind_planar(
    coil, stack_up, border_distance, wire_spacing, insulation, core_distance
)

# Check if winding fits
fits = PyOpenMagnetics.are_sections_and_layers_fitting(coil)

# Get layers by winding index
primary_layers = PyOpenMagnetics.get_layers_by_winding_index(coil, 0)
secondary_layers = PyOpenMagnetics.get_layers_by_winding_index(coil, 1)

# Get layers by section
layers = PyOpenMagnetics.get_layers_by_section(coil, section_index=0)

# Get sections description
sections = PyOpenMagnetics.get_sections_description_conduction(coil)
```

---

### 6. DESIGN ADVISER

```python
# Process inputs (REQUIRED before adviser - adds harmonics for loss calculation)
inputs = {
    "designRequirements": {
        "magnetizingInductance": {"nominal": 100e-6, "minimum": 90e-6, "maximum": 110e-6},
        "turnsRatios": [{"nominal": 5.0}],
        "leakageInductance": [{"maximum": 5e-6}],
        "insulation": {
            "insulationType": "Functional",  # or "Basic", "Supplementary", "Reinforced"
            "pollutionDegree": "P2",
            "overvoltageCategory": "OVC-II"
        }
    },
    "operatingPoints": [operating_point]
}
processed = PyOpenMagnetics.process_inputs(inputs)

# Get recommended cores only
weights = {"COST": 1.0, "EFFICIENCY": 1.0, "DIMENSIONS": 0.5}
cores = PyOpenMagnetics.calculate_advised_cores(
    processed,
    weights,
    max_results=10,
    core_mode="STANDARD_CORES"  # or "AVAILABLE_CORES"
)

# Get complete magnetic designs
result = PyOpenMagnetics.calculate_advised_magnetics(
    processed,
    max_results=5,
    core_mode="STANDARD_CORES"  # or "AVAILABLE_CORES"
)
# Result structure: {"data": [{"mas": {...}, "scoring": float, "scoringPerFilter": {...}}, ...]}

# From custom catalog
catalog_result = PyOpenMagnetics.calculate_advised_magnetics_from_catalog(
    processed, catalog_magnetics, max_results=5
)

# From cache (faster for repeated queries)
cache_result = PyOpenMagnetics.calculate_advised_magnetics_from_cache(
    processed, max_results=5
)
```

---

### 7. CONVERTER TOPOLOGY PROCESSORS

PyOpenMagnetics includes built-in support for common power converter topologies:

> **⚠️ IMPORTANT API NOTES:**
> 
> **1. Function Discrepancy:** `process_flyback()` may return schema errors. Use `process_converter("flyback", ...)` instead:
> ```python
> # If this fails with schema error:
> # inputs = PyOpenMagnetics.process_flyback(flyback_specs)
> 
> # Use this instead:
> inputs = PyOpenMagnetics.process_converter("flyback", flyback_specs, False)
> ```
> 
> **2. Case-Sensitive `core_mode`:** The `core_mode` parameter in `calculate_advised_magnetics()` MUST be lowercase:
> ```python
> # WRONG - returns empty results or error:
> result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "STANDARD_CORES")
> 
> # CORRECT:
> result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "standard cores")
> # Valid values: "standard cores" or "available cores"
> ```
> 
> **3. Double Brackets for `desiredDutyCycle`:** Must be nested list `[[value]]` not `[value]`:
> ```python
> flyback_specs = {
>     "desiredDutyCycle": [[0.45]],  # ✓ Correct
>     # "desiredDutyCycle": [0.45],   # ✗ Wrong - causes schema error
> }
> ```

#### Flyback Converter
```python
flyback = {
    "inputVoltage": {"minimum": 85, "nominal": 120, "maximum": 265},
    "diodeVoltageDrop": 0.7,
    "efficiency": 0.85,
    "maximumDrainSourceVoltage": 600,
    "maximumDutyCycle": 0.5,
    "operatingPoints": [{
        "outputVoltages": [12, 5],
        "outputCurrents": [2.0, 0.5],
        "switchingFrequency": 100000,
        "ambientTemperature": 40,
        "mode": "CCM"  # or "DCM", "BCM"
    }],
    "desiredInductance": 150e-6,
    "desiredTurnsRatios": [8.0, 19.2],
    "desiredDutyCycle": [[0.45, 0.45]]
}
inputs = PyOpenMagnetics.process_flyback(flyback)
```

> **💡 Tip:** If `process_flyback()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("flyback", flyback_specs, use_ngspice=False)
> ```

#### Buck Converter
```python
buck = {
    "inputVoltage": {"minimum": 8, "nominal": 12, "maximum": 14},
    "diodeVoltageDrop": 0.0,  # Synchronous
    "efficiency": 0.95,
    "currentRippleRatio": 0.3,
    "operatingPoints": [{
        "outputVoltage": 3.3,
        "outputCurrent": 5.0,
        "switchingFrequency": 500000,
        "ambientTemperature": 25
    }],
    "desiredInductance": 4.7e-6
}
inputs = PyOpenMagnetics.process_buck(buck)
```

> **💡 Tip:** If `process_buck()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("buck", buck_specs, use_ngspice=False)
> ```

#### Boost Converter
```python
boost = {
    "inputVoltage": {"minimum": 85, "nominal": 120, "maximum": 265},
    "diodeVoltageDrop": 1.0,
    "efficiency": 0.98,
    "currentRippleRatio": 0.2,
    "operatingPoints": [{
        "outputVoltage": 400,
        "outputCurrent": 2.5,
        "switchingFrequency": 65000,
        "ambientTemperature": 40
    }],
    "desiredInductance": 250e-6
}
inputs = PyOpenMagnetics.process_boost(boost)
```

> **💡 Tip:** If `process_boost()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("boost", boost_specs, use_ngspice=False)
> ```

#### Single-Switch Forward
```python
single_switch_forward = {
    "inputVoltage": {"minimum": 36, "nominal": 48, "maximum": 72},
    "diodeVoltageDrop": 0.5,
    "efficiency": 0.90,
    "currentRippleRatio": 0.3,
    "operatingPoints": [{
        "outputVoltages": [5],
        "outputCurrents": [10],
        "switchingFrequency": 250000,
        "ambientTemperature": 50
    }],
    "desiredInductance": 50e-6,
    "desiredTurnsRatios": [9.6, 9.6],  # [demagnetization, output]
    "desiredOutputInductances": [10e-6]
}
inputs = PyOpenMagnetics.process_single_switch_forward(single_switch_forward)
```

> **💡 Tip:** If `process_single_switch_forward()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("single_switch_forward", forward_specs, use_ngspice=False)
> ```

#### Two-Switch Forward
```python
two_switch_forward = {
    "inputVoltage": {"minimum": 300, "nominal": 400, "maximum": 420},
    "diodeVoltageDrop": 0.7,
    "efficiency": 0.92,
    "dutyCycle": 0.45,
    "currentRippleRatio": 0.25,
    "operatingPoints": [{
        "outputVoltages": [24],
        "outputCurrents": [20],
        "switchingFrequency": 100000,
        "ambientTemperature": 55
    }],
    "desiredInductance": 200e-6,
    "desiredTurnsRatios": [16.7],
    "desiredOutputInductances": [25e-6]
}
inputs = PyOpenMagnetics.process_two_switch_forward(two_switch_forward)
```

> **💡 Tip:** If `process_two_switch_forward()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("two_switch_forward", forward_specs, use_ngspice=False)
> ```

#### Active Clamp Forward
```python
active_clamp_forward = {
    "inputVoltage": {"minimum": 36, "nominal": 48, "maximum": 60},
    "diodeVoltageDrop": 0.5,
    "efficiency": 0.93,
    "currentRippleRatio": 0.2,
    "operatingPoints": [{
        "outputVoltages": [12],
        "outputCurrents": [8],
        "switchingFrequency": 350000,
        "ambientTemperature": 45
    }],
    "desiredInductance": 30e-6,
    "desiredTurnsRatios": [4.0],
    "desiredOutputInductances": [5e-6]
}
inputs = PyOpenMagnetics.process_active_clamp_forward(active_clamp_forward)
```

> **💡 Tip:** If `process_active_clamp_forward()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("active_clamp_forward", forward_specs, use_ngspice=False)
> ```

#### Push-Pull
```python
push_pull = {
    "inputVoltage": {"minimum": 22, "nominal": 24, "maximum": 28},
    "diodeVoltageDrop": 0.7,
    "efficiency": 0.90,
    "dutyCycle": 0.45,
    "currentRippleRatio": 0.3,
    "maximumDrainSourceVoltage": 100,
    "operatingPoints": [{
        "outputVoltage": 48,
        "outputCurrent": 5,
        "switchingFrequency": 100000,
        "ambientTemperature": 40
    }],
    "desiredInductance": 100e-6,
    "desiredTurnsRatios": [1.0],
    "desiredOutputInductance": 50e-6
}
inputs = PyOpenMagnetics.process_push_pull(push_pull)
```

> **💡 Tip:** If `process_push_pull()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("push_pull", push_pull_specs, use_ngspice=False)
> ```

#### Isolated Buck
```python
isolated_buck = {
    "inputVoltage": {"minimum": 280, "nominal": 310, "maximum": 375},
    "diodeVoltageDrop": 0.7,
    "efficiency": 0.91,
    "currentRippleRatio": 0.25,
    "operatingPoints": [{
        "outputVoltages": [15],
        "outputCurrents": [3],
        "switchingFrequency": 200000,
        "ambientTemperature": 35
    }],
    "desiredInductance": 80e-6,
    "desiredTurnsRatios": [20.0]
}
inputs = PyOpenMagnetics.process_isolated_buck(isolated_buck)
```

> **💡 Tip:** If `process_isolated_buck()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("isolated_buck", isolated_buck_specs, use_ngspice=False)
> ```

#### Isolated Buck-Boost
```python
isolated_buck_boost = {
    "inputVoltage": {"minimum": 18, "nominal": 24, "maximum": 36},
    "diodeVoltageDrop": 0.5,
    "efficiency": 0.88,
    "currentRippleRatio": 0.3,
    "operatingPoints": [{
        "outputVoltages": [24],
        "outputCurrents": [2],
        "switchingFrequency": 150000,
        "ambientTemperature": 30
    }],
    "desiredInductance": 60e-6,
    "desiredTurnsRatios": [1.0]
}
inputs = PyOpenMagnetics.process_isolated_buck_boost(isolated_buck_boost)
```

> **💡 Tip:** If `process_isolated_buck_boost()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("isolated_buck_boost", isolated_bb_specs, use_ngspice=False)
> ```

#### LLC Resonant Converter
```python
llc = {
    "inputVoltage": {"minimum": 400, "maximum": 400},
    "desiredInductance": 100e-6,
    "desiredTurnsRatios": [1.0],
    "minSwitchingFrequency": 80000,
    "maxSwitchingFrequency": 120000,
    "operatingPoints": [{
        "outputVoltages": [48.0],
        "outputCurrents": [5.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 25
    }]
}
inputs = PyOpenMagnetics.process_converter("llc", llc, use_ngspice=False)
```

#### Current Transformer
```python
current_transformer = {
    "primaryCurrent": {
        "waveform": {"data": [0, 10, 10, 0], "time": [0, 1e-6, 5e-6, 6e-6]},
        "frequency": 100000
    },
    "operatingPoints": [{
        "burdenResistance": 10,
        "ambientTemperature": 25
    }]
}
turns_ratio = 100
secondary_resistance = 5.0
inputs = PyOpenMagnetics.process_current_transformer(
    current_transformer, turns_ratio, secondary_resistance
)
```

> **💡 Tip:** If `process_current_transformer()` returns schema errors, use the generic `process_converter()`:
> ```python
> inputs = PyOpenMagnetics.process_converter("current_transformer", ct_specs, use_ngspice=False)
> ```

#### Generic Converter Processor
```python
# Use process_converter for any topology with custom specs
result = PyOpenMagnetics.process_converter(
    topology="flyback",  # or "buck", "boost", "llc", etc.
    converter_specs={...},
    use_ngspice=True  # Use SPICE simulation for waveforms (slower but accurate)
)
```

---

### 8. SIMULATION

```python
# Full simulation
models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
mas = PyOpenMagnetics.simulate(inputs, magnetic, models)
# Returns Mas with outputs populated

# Autocomplete partial structures
magnetic = PyOpenMagnetics.magnetic_autocomplete(partial_magnetic, config)
mas = PyOpenMagnetics.mas_autocomplete(partial_mas, config)

# Extract operating point from SPICE simulation
op = PyOpenMagnetics.extract_operating_point(
    spice_file, 
    num_windings=2, 
    frequency=100000, 
    target_inductance=100e-6, 
    column_mapping={...}
)

# Export to SPICE
subcircuit = PyOpenMagnetics.export_magnetic_as_subcircuit(magnetic)
```

---

### 9. INSULATION COORDINATION

```python
# Calculate safety distances per IEC standards
insulation = PyOpenMagnetics.calculate_insulation(inputs)
# Returns:
# {
#   creepageDistance: float (meters),
#   clearance: float (meters),
#   withstandVoltage: float (Volts),
#   distanceThroughInsulation: float (meters),
#   errorMessage: "" if successful
# }

# Get isolation side from winding index
isolation_side = PyOpenMagnetics.get_isolation_side_from_index(coil, winding_index=0)
```

---

### 10. VISUALIZATION

```python
# Core views
svg_core = PyOpenMagnetics.plot_core(core, use_colors=True)
svg_core_2d = PyOpenMagnetics.plot_core(core, axis=1, winding_windows=None, use_colors=True)

# Coil views
svg_coil = PyOpenMagnetics.plot_coil(coil, use_colors=True)

# Magnetic field visualization
svg_field = PyOpenMagnetics.plot_magnetic_field(magnetic, operating_point, use_colors=True)
svg_field_2d = PyOpenMagnetics.plot_magnetic_field(magnetic, operating_point, axis=1, use_colors=True)

# Electric field
svg_electric = PyOpenMagnetics.plot_electric_field(magnetic, operating_point)

# Individual components
svg_wire = PyOpenMagnetics.plot_wire(wire, use_colors=True)
svg_bobbin = PyOpenMagnetics.plot_bobbin(bobbin, use_colors=True)

# Winding descriptions
svg_sections = PyOpenMagnetics.plot_sections(magnetic, use_colors=True)
svg_layers = PyOpenMagnetics.plot_layers(magnetic, use_colors=True)
svg_turns = PyOpenMagnetics.plot_turns(magnetic, use_colors=True)

# Field maps
svg_field_map = PyOpenMagnetics.plot_field_map(magnetic, operating_point)
```

---

### 11. SIGNAL PROCESSING

```python
# Calculate harmonics from waveform
harmonics = PyOpenMagnetics.calculate_harmonics(waveform_data)

# Sample waveform
sampled = PyOpenMagnetics.calculate_sampled_waveform(waveform, num_samples=100)

# RMS power
P_rms = PyOpenMagnetics.calculate_rms_power(voltage_waveform, current_waveform)

# Instantaneous power
P_inst = PyOpenMagnetics.calculate_instantaneous_power(voltage_waveform, current_waveform)

# Processed data (basic)
processed = PyOpenMagnetics.calculate_basic_processed_data(waveform)

# Full processed data
processed = PyOpenMagnetics.calculate_processed_data(waveform)
```

---

### 12. SETTINGS AND CONFIGURATION

```python
# Get current settings
settings = PyOpenMagnetics.get_settings()

# Modify settings
settings["coilAllowMarginTape"] = True
settings["coilWindEvenIfNotFit"] = False
settings["useOnlyCoresInStock"] = True
settings["painterNumberPointsX"] = 100
settings["painterNumberPointsY"] = 100
PyOpenMagnetics.set_settings(settings)

# Reset to defaults
PyOpenMagnetics.reset_settings()

# Get physical constants
constants = PyOpenMagnetics.get_constants()
mu_0 = constants["vacuumPermeability"]

# Get default models
defaults = PyOpenMagnetics.get_default_models()

# Logging
PyOpenMagnetics.set_log_level("DEBUG")  # or "INFO", "WARNING", "ERROR"
logs = PyOpenMagnetics.get_logs()
PyOpenMagnetics.clear_logs()

# Enable/disable string sink for logging
PyOpenMagnetics.enable_string_sink()
PyOpenMagnetics.disable_string_sink()
```

---

### 13. DATABASE MANAGEMENT

```python
# Load databases (automatic on import, but can be called explicitly)
PyOpenMagnetics.load_databases()
PyOpenMagnetics.read_databases()

# Load specific data
PyOpenMagnetics.load_core_materials()
PyOpenMagnetics.load_core_shapes()
PyOpenMagnetics.load_wires()

# Check if databases are empty
is_empty_materials = PyOpenMagnetics.is_core_material_database_empty()
is_empty_shapes = PyOpenMagnetics.is_core_shape_database_empty()
is_empty_wires = PyOpenMagnetics.is_wire_database_empty()

# Clear databases/cache
PyOpenMagnetics.clear_databases()
PyOpenMagnetics.clear_magnetic_cache()

# Clear logs
PyOpenMagnetics.clear_logs()
```

---

### 14. MAS (MAGNETIC AGNOSTIC STRUCTURE) OPERATIONS

```python
# Load MAS from file
mas = PyOpenMagnetics.load_mas("design.json")

# Load multiple MAS files
magnetics = PyOpenMagnetics.load_magnetics("folder_path/")
magnetics = PyOpenMagnetics.load_magnetics_from_file("file.json")

# Read MAS data
mas_data = PyOpenMagnetics.read_mas(mas_dict)

# Extract column names from data
names = PyOpenMagnetics.extract_column_names(data)
map_names = PyOpenMagnetics.extract_map_column_names(data)
```

---

### 15. UTILITY FUNCTIONS

```python
# Check if design fits
fits = PyOpenMagnetics.check_if_fits(magnetic, inputs)

# Delimit and compact data
delimited = PyOpenMagnetics.delimit_and_compact(data)

# Resolve dimension with tolerance
dimension = PyOpenMagnetics.resolve_dimension_with_tolerance(
    nominal_value, tolerance_percent
)

# Add margin to section
PyOpenMagnetics.add_margin_to_section_by_index(coil, section_index, margin_left, margin_right)

# Log message
PyOpenMagnetics.log_message("Custom message", "INFO")
```

---

## Data Structures Reference

### Core Specification
```python
core = {
    "functionalDescription": {
        "type": "two-piece set",  # "two-piece set", "toroidal", "closed shape"
        "shape": shape_object_or_name,  # e.g., "E 42/21/15" or full shape dict
        "material": material_object_or_name,  # e.g., "3C95" or full material dict
        "gapping": [
            {"type": "subtractive", "length": 0.001},  # 1mm gap
            {"type": "additive", "length": 0.0005}     # 0.5mm spacer
        ],
        "numberStacks": 1  # Number of stacked cores
    }
}
```

### Coil/Winding Specification
```python
coil = {
    "bobbin": bobbin_data,  # Optional
    "functionalDescription": [
        {
            "name": "Primary",
            "numberTurns": 40,
            "numberParallels": 1,
            "wire": "Round 0.4 - Grade 1",  # Wire name or full wire dict
            "isolationSide": "primary"  # "primary", "secondary", "tertiary"
        },
        {
            "name": "Secondary",
            "numberTurns": 5,
            "numberParallels": 2,
            "wire": "Round 0.8 - Grade 1",
            "isolationSide": "secondary"
        }
    ]
}
```

### Operating Point (Waveforms)
```python
operating_point = {
    "name": "Nominal",
    "conditions": {
        "ambientTemperature": 25,  # Celsius
        "altitude": 0  # meters
    },
    "excitationsPerWinding": [
        {
            "name": "Primary",
            "frequency": 100000,  # Hz
            "current": {
                "waveform": {
                    "data": [0.2, 1.8, 1.8, 0.2],  # Current samples [A]
                    "time": [0, 4.5e-6, 4.5e-6, 10e-6]  # Time samples [s]
                }
            },
            "voltage": {
                "waveform": {
                    "data": [311, 311, 0, 0],  # Voltage samples [V]
                    "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                }
            }
        }
    ]
}
```

### Design Requirements
```python
design_requirements = {
    "magnetizingInductance": {
        "nominal": 100e-6,  # Henries
        "minimum": 90e-6,
        "maximum": 110e-6
    },
    "turnsRatios": [
        {"nominal": 4.0, "minimum": 3.8, "maximum": 4.2}  # N_pri / N_sec
    ],
    "leakageInductance": [
        {"maximum": 5e-6}  # Optional
    ],
    "insulation": {
        "insulationType": "Functional",  # "Basic", "Functional", "Supplementary", "Reinforced"
        "pollutionDegree": "P2",  # "P1", "P2", "P3"
        "overvoltageCategory": "OVC-II",  # "OVC-I", "OVC-II", "OVC-III", "OVC-IV"
        "standards": ["IEC 61558-1"],
        "altitude": {"maximum": 2000}  # meters
    }
}
```

### Complete Magnetic
```python
magnetic = {
    "core": core,  # Core specification dict
    "coil": coil   # Coil specification dict
}
```

### MAS (Magnetic Agnostic Structure)
```python
mas = {
    "inputs": {
        "designRequirements": design_requirements,
        "operatingPoints": [operating_point]
    },
    "magnetic": magnetic,
    "outputs": {  # Populated after simulation
        "coreLosses": 0.5,  # Watts
        "windingLosses": 1.2,  # Watts
        "temperatureRise": 40  # Kelvin
    }
}
```

---

## Common Materials Reference

### Ferrite Materials (High Frequency, 100kHz-1MHz)
| Material | Manufacturer | μi | Bsat (mT) | Use Case |
|----------|--------------|-----|-----------|----------|
| 3C90 | Ferroxcube | 2300 | 380 | General purpose |
| 3C95 | Ferroxcube | 3000 | 380 | Power applications |
| 3C96 | Ferroxcube | 2000 | 400 | High frequency |
| 3F3 | Ferroxcube | 2000 | 400 | 200-500 kHz |
| 3F4 | Ferroxcube | 900 | 350 | >500 kHz |
| N87 | TDK/EPCOS | 2200 | 390 | Power ferrite |
| N97 | TDK/EPCOS | 2300 | 400 | High temp |
| PC40 | TDK | 2300 | 390 | Low loss |
| PC95 | TDK | 3300 | 380 | High μ, low loss |

### Powder Core Materials (High DC Bias)
| Material | Manufacturer | μi | Bsat (T) | Loss | Cost |
|----------|--------------|-----|----------|------|------|
| MPP | Magnetics Inc | 14-550 | 0.7 | Lowest | Highest |
| High Flux | Magnetics Inc | 14-160 | 1.5 | Low | High |
| Kool Mu | Magnetics Inc | 26-125 | 1.0 | Medium | Medium |
| XFlux | Magnetics Inc | 26-90 | 1.6 | Higher | Low |
| -26 | Micrometals | 75 | 1.4 | High | Lowest |
| -52 | Micrometals | 75 | 1.3 | Medium | Low |

### Core Shape Families
| Family | Description | Typical Use |
|--------|-------------|-------------|
| E, EI | Standard E-cores | General purpose |
| EFD | Flat E-cores | Low profile |
| ETD, EC | Round center leg | Power transformers |
| PQ | Optimized power | High power density |
| PM | Power module | Medium power |
| RM | Rectangular module | Compact designs |
| T | Toroidal | Low leakage, EMI |
| P, PT | Pot cores | High inductance |
| U, UI | U-cores | Large power |
| LP | Planar | PCB integration |

---

## Best Practices

### 1. Always Process Inputs First
```python
# WRONG
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "STANDARD_CORES")

# RIGHT
processed = PyOpenMagnetics.process_inputs(inputs)
result = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
```

### 2. Handle Result Format Properly
```python
result = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")

if isinstance(result, dict) and "data" in result:
    data = result["data"]
    if isinstance(data, str):
        print(f"Error: {data}")
    elif not data:
        print("No suitable designs found")
    else:
        for item in data:
            mas = item["mas"]
            score = item["scoring"]
            magnetic = mas["magnetic"]
```

### 3. Check Saturation
```python
losses = PyOpenMagnetics.calculate_core_losses(core, coil, inputs, models)
B_peak = losses["magneticFluxDensityPeak"]

if B_peak > 0.35:  # For ferrite
    print("⚠ High flux density - risk of saturation")
elif B_peak > 0.25:
    print("⚠ Moderate flux density - verify margin")
else:
    print("✓ Safe flux density")
```

### 4. Consider Temperature
```python
# Calculate at max operating temperature
temp = 100  # °C
winding_losses = PyOpenMagnetics.calculate_winding_losses(magnetic, op, temp)
params = PyOpenMagnetics.get_core_temperature_dependant_parameters(core, temp)
B_sat_at_temp = params["magneticFluxDensitySaturation"]
```

### 5. Use Appropriate Wire for Frequency
```python
# Low frequency (<50kHz): Standard round wire
wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")

# High frequency (>100kHz): Consider litz wire
litz_wires = [w for w in PyOpenMagnetics.get_wire_names() if "litz" in w.lower()]

# Very high current: Use rectangular wire
rect_wire = PyOpenMagnetics.find_wire_by_dimension(0.002, "rectangular", "IEC 60317")
```

---

## Error Handling

```python
try:
    result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "STANDARD_CORES")
    
    if isinstance(result, dict):
        if "data" in result:
            data = result["data"]
            if isinstance(data, str):
                # Error message
                print(f"Adviser error: {data}")
            elif isinstance(data, list):
                # Success
                for item in data:
                    mas = item.get("mas", item)
                    score = item.get("scoring", 0)
        elif "error" in result:
            print(f"Error: {result['error']}")
    else:
        print(f"Unexpected result type: {type(result)}")
        
except Exception as e:
    print(f"Exception: {e}")
```

---

## Example Files

- `examples/flyback_design.py` - Complete flyback transformer design
- `examples/flyback_220v_12v_1a.py` - 220V to 12V @ 1A flyback
- `examples/buck_inductor.py` - Buck converter inductor
- `examples/plot_flyback_design.py` - Visualization example
- `tests/test_converter_endpoints.py` - All topology tests
- `tests/test_core.py` - Core database and calculation tests
- `tests/test_winding.py` - Wire and bobbin tests

---

## References

- **llms.txt** - Complete API reference in project root
- **PyOpenMagnetics.pyi** - Type stubs for IDE support
- **MAS Schema**: github.com/OpenMagnetics/MAS
- **MKF Engine**: github.com/OpenMagnetics/MKF
- **OpenMagnetics Web**: openmagnetics.com

---

## Simulation and Analysis

### Complete Simulation Workflow

```python
import PyOpenMagnetics
import json

# 1. Create or load magnetic design
magnetic = {
    "core": {
        "functionalDescription": {
            "type": "two-piece set",
            "shape": "E 42/21/15",
            "material": "3C95",
            "gapping": [{"type": "subtractive", "length": 0.001}],
            "numberStacks": 1
        }
    },
    "coil": {
        "functionalDescription": [
            {
                "name": "Primary",
                "numberTurns": 40,
                "numberParallels": 1,
                "wire": "Round 0.4 - Grade 1",
                "isolationSide": "primary"
            },
            {
                "name": "Secondary",
                "numberTurns": 10,
                "numberParallels": 1,
                "wire": "Round 0.8 - Grade 1",
                "isolationSide": "secondary"
            }
        ]
    }
}

# 2. Create operating point
operating_point = {
    "name": "Nominal",
    "conditions": {"ambientTemperature": 40},
    "excitationsPerWinding": [
        {
            "name": "Primary",
            "frequency": 100000,
            "current": {
                "processed": {
                    "label": "Triangular",
                    "dutyCycle": 0.45,
                    "offset": 0.5,
                    "peakToPeak": 0.4
                }
            }
        }
    ]
}

# 3. Create inputs
inputs = {
    "designRequirements": {
        "magnetizingInductance": {"nominal": 1000e-6},
        "turnsRatios": [{"nominal": 4.0}]
    },
    "operatingPoints": [operating_point]
}

# 4. Process inputs
processed = PyOpenMagnetics.process_inputs(inputs)
if isinstance(processed, dict) and "data" in processed:
    processed = processed["data"]

# 5. Calculate core losses
models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
core_losses = PyOpenMagnetics.calculate_core_losses(
    magnetic["core"],
    magnetic["coil"],
    processed,
    models
)
print(f"Core losses: {core_losses.get('coreLosses', 0):.3f} W")
print(f"Peak flux density: {core_losses.get('magneticFluxDensityPeak', 0)*1000:.1f} mT")

# 6. Calculate winding losses
winding_losses = PyOpenMagnetics.calculate_winding_losses(
    magnetic,
    operating_point,
    temperature=80
)
print(f"Winding losses: {winding_losses.get('windingLosses', 0):.3f} W")

# 7. Verify inductance
L_actual = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
    magnetic["core"],
    magnetic["coil"],
    operating_point,
    {"reluctance": "ZHANG"}
)
print(f"Actual inductance: {L_actual*1e6:.1f} µH")

# 8. Check saturation
I_sat = PyOpenMagnetics.calculate_saturation_current(magnetic, temperature=100)
print(f"Saturation current: {I_sat:.2f} A")
```

### Advanced Simulation Features

```python
# Temperature-dependent simulation
for temp in [25, 50, 75, 100]:
    params = PyOpenMagnetics.get_core_temperature_dependant_parameters(
        magnetic["core"], 
        temperature=temp
    )
    B_sat = params["magneticFluxDensitySaturation"]
    mu_eff = params["effectivePermeability"]
    print(f"T={temp}°C: B_sat={B_sat*1000:.0f} mT, μ_eff={mu_eff:.0f}")

# Harmonic analysis
harmonics = PyOpenMagnetics.calculate_harmonics(
    {"data": [0, 1, 0, -1, 0], "time": [0, 2.5e-6, 5e-6, 7.5e-6, 10e-6]}
)

# Signal processing
P_rms = PyOpenMagnetics.calculate_rms_power(voltage_waveform, current_waveform)
P_inst = PyOpenMagnetics.calculate_instantaneous_power(voltage_waveform, current_waveform)
```

---

## Visualization and Plotting

### Basic Plotting Functions

```python
import PyOpenMagnetics

# Plot core only
result = PyOpenMagnetics.plot_core(core, use_colors=True)
if result.get('success'):
    svg_content = result['svg']
    with open('core.svg', 'w') as f:
        f.write(svg_content)

# Plot complete magnetic (core + windings)
result = PyOpenMagnetics.plot_magnetic(magnetic)
if result.get('success'):
    with open('magnetic.svg', 'w') as f:
        f.write(result['svg'])

# Plot wire
wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
result = PyOpenMagnetics.plot_wire(wire)
if result.get('success'):
    with open('wire.svg', 'w') as f:
        f.write(result['svg'])

# Plot bobbin
result = PyOpenMagnetics.plot_bobbin(magnetic)
if result.get('success'):
    with open('bobbin.svg', 'w') as f:
        f.write(result['svg'])
```

### Field Visualization

```python
# Magnetic field plot (requires operating point with current)
operating_point = {
    "name": "Field Plot",
    "conditions": {"ambientTemperature": 25},
    "excitationsPerWinding": [
        {
            "name": "Primary",
            "frequency": 100000,
            "current": {
                "processed": {
                    "label": "Triangular",
                    "dutyCycle": 0.45,
                    "offset": 0.5,
                    "peakToPeak": 0.2
                }
            }
        }
    ]
}

result = PyOpenMagnetics.plot_magnetic_field(magnetic, operating_point)
if result.get('success'):
    with open('magnetic_field.svg', 'w') as f:
        f.write(result['svg'])

# Electric field plot (requires voltage)
operating_point_with_voltage = {
    "name": "Electric Field",
    "conditions": {"ambientTemperature": 25},
    "excitationsPerWinding": [
        {
            "name": "Primary",
            "frequency": 100000,
            "current": {
                "processed": {
                    "label": "Triangular",
                    "dutyCycle": 0.45,
                    "offset": 0.5,
                    "peakToPeak": 0.2
                }
            },
            "voltage": {
                "processed": {
                    "label": "Rectangular",
                    "dutyCycle": 0.45,
                    "offset": 100,
                    "peakToPeak": 200
                }
            }
        }
    ]
}

result = PyOpenMagnetics.plot_electric_field(magnetic, operating_point_with_voltage)
if result.get('success'):
    with open('electric_field.svg', 'w') as f:
        f.write(result['svg'])
```

### Complete Visualization Workflow

```python
def visualize_complete_design(magnetic, operating_point, output_dir="output"):
    """Generate all visualizations for a design."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    visualizations = [
        ("core", lambda: PyOpenMagnetics.plot_core(magnetic["core"])),
        ("magnetic", lambda: PyOpenMagnetics.plot_magnetic(magnetic)),
        ("magnetic_field", lambda: PyOpenMagnetics.plot_magnetic_field(magnetic, operating_point)),
        ("electric_field", lambda: PyOpenMagnetics.plot_electric_field(magnetic, operating_point)),
    ]
    
    for name, plot_func in visualizations:
        try:
            result = plot_func()
            if result.get('success'):
                filename = os.path.join(output_dir, f"{name}.svg")
                with open(filename, 'w') as f:
                    f.write(result['svg'])
                print(f"✓ Saved: {filename}")
            else:
                print(f"✗ {name} failed: {result.get('error')}")
        except Exception as e:
            print(f"✗ {name} error: {e}")
```

---

## Converter-Based Design (converter.h Methods)

PyOpenMagnetics provides high-level converter-based design functions that automatically process converter specifications and generate magnetic designs. These are the Python bindings for the methods in `converter.h`.

### process_converter() - Generic Converter Processor

Process any converter topology to generate Inputs for magnetic design.

```python
# Generic converter processor
result = PyOpenMagnetics.process_converter(
    topology="flyback",  # Topology name
    converter={
        "inputVoltage": {"minimum": 85, "maximum": 265},
        "desiredInductance": 1e-3,
        "desiredTurnsRatios": [10.0],
        "operatingPoints": [{
            "outputVoltages": [12.0],
            "outputCurrents": [2.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 40
        }]
    },
    use_ngspice=True  # Use SPICE simulation for accurate waveforms
)

# Returns: {"designRequirements": {...}, "operatingPoints": [...]}
# On error: {"error": "error message"}
```

**Supported Topologies:**
- `"flyback"` - Flyback converter (isolated, energy storing)
- `"buck"` - Buck converter (step-down)
- `"boost"` - Boost converter (step-up)
- `"single_switch_forward"` - Single-switch forward
- `"two_switch_forward"` - Two-switch forward
- `"active_clamp_forward"` - Active clamp forward
- `"push_pull"` - Push-pull converter
- `"isolated_buck"` - Isolated buck
- `"isolated_buck_boost"` - Isolated buck-boost
- `"llc"` - LLC resonant converter
- `"current_transformer"` - Current sensing transformer

### design_magnetics_from_converter() - Complete Design Pipeline

**This is the most powerful function for converter design!** It combines converter processing with the magnetic adviser to go directly from converter specs to ranked magnetic designs.

```python
# Complete converter-to-magnetic design pipeline
result = PyOpenMagnetics.design_magnetics_from_converter(
    topology="flyback",
    converter={
        "inputVoltage": {"minimum": 185, "maximum": 265},
        "desiredInductance": 800e-6,
        "desiredTurnsRatios": [13.5],
        "maximumDutyCycle": 0.45,
        "efficiency": 0.88,
        "diodeVoltageDrop": 0.5,
        "operatingPoints": [{
            "outputVoltages": [12.0],
            "outputCurrents": [2.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 40
        }]
    },
    max_results=5,           # Return top 5 designs
    core_mode="STANDARD_CORES",  # or "AVAILABLE_CORES"
    use_ngspice=True,        # Use SPICE for accurate waveforms
    weights={                # Optional scoring weights
        "COST": 1.0,
        "EFFICIENCY": 2.0,
        "DIMENSIONS": 0.5
    }
)

# Returns: {"data": [{"mas": {...}, "scoring": float, "scoringPerFilter": {...}}, ...]}
# Each result contains:
# - "mas": Complete MAS object with magnetic design
# - "scoring": Overall score (higher is better)
# - "scoringPerFilter": Individual filter scores
```

### Complete Example: Flyback Design with design_magnetics_from_converter()

```python
import PyOpenMagnetics
import json

# Define flyback converter specifications
flyback_specs = {
    "inputVoltage": {
        "minimum": 185,    # V AC minimum
        "maximum": 265     # V AC maximum
    },
    "desiredInductance": 800e-6,     # 800 µH magnetizing inductance
    "desiredTurnsRatios": [13.5],    # Np/Ns for 12V output
    "maximumDutyCycle": 0.45,
    "efficiency": 0.88,
    "diodeVoltageDrop": 0.5,
    "operatingPoints": [{
        "outputVoltages": [12.0],    # 12V output
        "outputCurrents": [2.0],     # 2A output
        "switchingFrequency": 100000, # 100 kHz
        "ambientTemperature": 40
    }]
}

# Design magnetics directly from converter specs
print("Designing magnetics from converter specifications...")
result = PyOpenMagnetics.design_magnetics_from_converter(
    topology="flyback",
    converter=flyback_specs,
    max_results=3,
    core_mode="STANDARD_CORES",
    use_ngspice=False,  # Use analytical for speed
    weights={
        "COST": 1.0,
        "EFFICIENCY": 2.0,  # Prioritize efficiency
        "DIMENSIONS": 0.5
    }
)

# Process results
if isinstance(result, dict) and "data" in result:
    designs = result["data"]
    print(f"\n✓ Found {len(designs)} suitable designs\n")
    
    for i, design in enumerate(designs):
        mas = design["mas"]
        magnetic = mas["magnetic"]
        score = design["scoring"]
        
        core = magnetic["core"]
        shape = core["functionalDescription"]["shape"]["name"]
        material = core["functionalDescription"]["material"]["name"]
        
        print(f"Design #{i+1}: {shape} / {material}")
        print(f"  Score: {score:.3f}")
        
        # Get winding info
        if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
            for winding in magnetic["coil"]["functionalDescription"]:
                name = winding.get("name", "Winding")
                turns = winding.get("numberTurns", "?")
                print(f"  {name}: {turns} turns")
        
        # Calculate losses
        models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
        try:
            losses = PyOpenMagnetics.calculate_core_losses(
                core, magnetic["coil"], mas["inputs"], models
            )
            print(f"  Core losses: {losses.get('coreLosses', 0):.3f} W")
        except:
            pass
        
        print()
else:
    print("No designs found or error occurred")
```

### Topology-Specific Processors

For convenience, PyOpenMagnetics also provides dedicated functions for each topology:

```python
# Flyback
flyback_inputs = PyOpenMagnetics.process_flyback({
    "inputVoltage": {"minimum": 85, "maximum": 265},
    "desiredInductance": 1e-3,
    "desiredTurnsRatios": [10.0],
    "operatingPoints": [{
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 40
    }]
})

# Buck
buck_inputs = PyOpenMagnetics.process_buck({
    "inputVoltage": {"minimum": 8, "maximum": 14},
    "desiredInductance": 4.7e-6,
    "currentRippleRatio": 0.3,
    "operatingPoints": [{
        "outputVoltage": 3.3,
        "outputCurrent": 5.0,
        "switchingFrequency": 500000,
        "ambientTemperature": 25
    }]
})

# Boost
boost_inputs = PyOpenMagnetics.process_boost({
    "inputVoltage": {"minimum": 85, "maximum": 265},
    "desiredInductance": 250e-6,
    "currentRippleRatio": 0.2,
    "operatingPoints": [{
        "outputVoltage": 400,
        "outputCurrent": 2.5,
        "switchingFrequency": 65000,
        "ambientTemperature": 40
    }]
})

# Other topologies
forward_inputs = PyOpenMagnetics.process_single_switch_forward({...})
forward2_inputs = PyOpenMagnetics.process_two_switch_forward({...})
active_clamp_inputs = PyOpenMagnetics.process_active_clamp_forward({...})
push_pull_inputs = PyOpenMagnetics.process_push_pull({...})
isolated_buck_inputs = PyOpenMagnetics.process_isolated_buck({...})
isolated_bb_inputs = PyOpenMagnetics.process_isolated_buck_boost({...})
ct_inputs = PyOpenMagnetics.process_current_transformer({...}, turns_ratio=100)
```

### When to Use Each Method

**Use `design_magnetics_from_converter()` when:**
- You want a complete design from converter specs to magnetic designs
- You need ranked/scored design recommendations
- You want the fastest path from specs to buildable design

**Use `process_converter()` when:**
- You want to customize the magnetic design process
- You need to modify the inputs before running the adviser
- You want to use the magnetic adviser with custom weights/filters

**Use topology-specific processors when:**
- You know the exact topology
- You want cleaner, more readable code
- You don't need the flexibility of the generic processor

---

## SPICE Export

```python
# Export magnetic as SPICE subcircuit
subcircuit = PyOpenMagnetics.export_magnetic_as_subcircuit(magnetic)

# Save to file
with open('transformer.spice', 'w') as f:
    f.write(subcircuit)

# The subcircuit can be used in SPICE simulators like LTspice, ngspice, etc.
```

---

## Quick Reference Card

```python
import PyOpenMagnetics as PyOM

# Database
materials = PyOM.get_core_material_names()
shapes = PyOM.get_core_shape_names()
wires = PyOM.get_wire_names()

# Find items
mat = PyOM.find_core_material_by_name("3C95")
shape = PyOM.find_core_shape_by_name("E 42/21/15")
wire = PyOM.find_wire_by_name("Round 0.5 - Grade 1")

# Design
processed = PyOM.process_inputs(inputs)
result = PyOM.calculate_advised_magnetics(processed, 5, "standard cores")  # Note: lowercase!

# Losses
models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}
core_losses = PyOM.calculate_core_losses(core, coil, inputs, models)
winding_losses = PyOM.calculate_winding_losses(magnetic, op, 80)

# Visualization
result = PyOM.plot_core(core, use_colors=True)
if result.get('success'):
    svg = result['svg']

# SPICE Export
spice = PyOM.export_magnetic_as_subcircuit(magnetic)
```

---

## Troubleshooting & Common Issues

This section documents common problems encountered when using PyOpenMagnetics and their solutions.

### 0. Empty Results from `calculate_advised_magnetics()`

**Problem:** Function returns `{"data": []}` or no designs found despite valid inputs.

**Cause:** The `core_mode` parameter is case-sensitive and must be lowercase.

**Solution:**
```python
# WRONG - returns empty results:
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "STANDARD_CORES")

# CORRECT:
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "standard cores")
# Alternative: "available cores"
```

**Check:** Verify the result format:
```python
if isinstance(result, dict) and "data" in result:
    if isinstance(result["data"], list) and len(result["data"]) > 0:
        print(f"Found {len(result['data'])} designs")
    else:
        print("No designs found - check core_mode case!")
```

---

### 1. Import Issues

**Problem:** `AttributeError: module 'PyOpenMagnetics' has no attribute 'process_flyback'`

**Cause:** The PyOpenMagnetics package is a C++ extension module (.so file) without a proper Python `__init__.py` file.

**Solution:** See the **Module Import Instructions** section in Installation above, or create an `__init__.py` file:

```python
# In: site-packages/PyOpenMagnetics/__init__.py
import os
import importlib.util

# Get the path to the .so file
so_file = os.path.join(os.path.dirname(__file__), 
                       'PyOpenMagnetics.cpython-311-x86_64-linux-gnu.so')

# Load the module
spec = importlib.util.spec_from_file_location('PyOpenMagnetics', so_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Export all attributes
for attr_name in dir(module):
    if not attr_name.startswith('_'):
        globals()[attr_name] = getattr(module, attr_name)
```

**Alternative:** Load the module directly using importlib:

```python
import importlib.util

spec = importlib.util.spec_from_file_location(
    'PyOpenMagnetics', 
    '/path/to/PyOpenMagnetics.cpython-311-x86_64-linux-gnu.so'
)
PyOpenMagnetics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PyOpenMagnetics)
```

### 2. Case-Sensitive Parameters

**Problem:** `Exception: Input JSON does not conform to schema!`

**Cause:** The `core_mode` parameter in `calculate_advised_magnetics()` is case-sensitive.

**Solution:** Use lowercase for core_mode:

```python
# WRONG:
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "STANDARD_CORES")

# CORRECT:
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "standard cores")
```

Valid values are:
- `"standard cores"` - Use standard catalog cores
- `"available cores"` - Use only cores marked as available/in stock

### 3. Converter Schema Errors (All Topologies)

**Problem:** Any `process_*()` function (`process_flyback()`, `process_buck()`, `process_boost()`, etc.) returns `"Input JSON does not conform to schema!"` even with all required fields.

**Cause:** Topology-specific functions have stricter schema validation than the generic `process_converter()`.

**Solution - Use `process_converter()` as fallback for ALL converters:**
```python
# If this fails:
inputs = PyOpenMagnetics.process_flyback(flyback_specs)

# Use this instead (works reliably):
flyback_minimal = {
    "inputVoltage": {"minimum": 185, "maximum": 265},
    "diodeVoltageDrop": 0.7,
    "efficiency": 0.88,
    "desiredInductance": 800e-6,
    "desiredTurnsRatios": [18.0],
    "desiredDutyCycle": [[0.45]],  # Note: double brackets!
    "operatingPoints": [{
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 40
    }]
}

inputs = PyOpenMagnetics.process_converter("flyback", flyback_minimal, False)
```

**Alternative - Include ALL required fields for `process_flyback()`:**

```python
flyback_specs = {
    # Required by basic Flyback schema:
    "inputVoltage": {"minimum": 185, "maximum": 265},
    "diodeVoltageDrop": 0.7,
    "currentRippleRatio": 0.3,  # REQUIRED!
    "efficiency": 0.85,
    
    # Required by AdvancedFlyback:
    "desiredInductance": 500e-6,      # REQUIRED!
    "desiredTurnsRatios": [15.0],     # REQUIRED!
    "desiredDutyCycle": [[0.45]],     # REQUIRED! (note: double brackets)
    "maximumDutyCycle": 0.45,         # Optional but recommended
    
    "operatingPoints": [{
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 40
    }]
}

inputs = PyOpenMagnetics.process_flyback(flyback_specs)
```

**Important:** The `desiredDutyCycle` field must be a nested list `[[duty_cycle]]`, not just `[duty_cycle]`.

### 4. Understanding Result Types

**Problem:** Difficulty parsing results from `calculate_advised_magnetics()`

**Solution:** Results are returned as dictionaries with a `data` key:

```python
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "standard cores")

if isinstance(result, dict) and "data" in result:
    designs = result["data"]
    
    if isinstance(designs, str):
        # Error message returned as string
        print(f"Error: {designs}")
    elif isinstance(designs, list):
        # Success - list of design dictionaries
        for design in designs:
            mas = design["mas"]
            score = design["scoring"]
            magnetic = mas["magnetic"]
            # ... process design
```

### 5. Generic Converter Processor Reference

**Quick Reference:** Use `process_converter()` as a universal fallback for all topologies:

```python
# Universal pattern for ALL converter topologies:
inputs = PyOpenMagnetics.process_converter(
    topology="<topology_name>",  # See list below
    converter=<converter_specs>,  # Topology-specific dict
    use_ngspice=False             # False = analytical (faster), True = SPICE (accurate)
)
```

**Supported topology names:**
- `"flyback"` - Flyback converter
- `"buck"` - Buck converter (step-down)
- `"boost"` - Boost converter (step-up)
- `"single_switch_forward"` - Single-switch forward
- `"two_switch_forward"` - Two-switch forward  
- `"active_clamp_forward"` - Active clamp forward
- `"push_pull"` - Push-pull converter
- `"isolated_buck"` - Isolated buck
- `"isolated_buck_boost"` - Isolated buck-boost
- `"llc"` - LLC resonant converter
- `"current_transformer"` - Current sensing transformer

**Example usage for different topologies:**
```python
# Buck converter
inputs = PyOpenMagnetics.process_converter("buck", buck_specs, False)

# Boost converter  
inputs = PyOpenMagnetics.process_converter("boost", boost_specs, False)

# Forward converter
inputs = PyOpenMagnetics.process_converter("single_switch_forward", forward_specs, False)

# LLC resonant
inputs = PyOpenMagnetics.process_converter("llc", llc_specs, False)
```

### 6. Database Loading

**Problem:** Empty database queries or "database empty" errors.

**Solution:** Databases are typically auto-loaded on import. If not, use:

```python
# Check if databases are loaded
if PyOpenMagnetics.is_core_material_database_empty():
    # Load databases (requires empty JSON config)
    PyOpenMagnetics.load_databases({})

# Verify
print(f"Materials: {len(PyOpenMagnetics.get_core_materials())}")
print(f"Shapes: {len(PyOpenMagnetics.get_core_shapes())}")
print(f"Wires: {len(PyOpenMagnetics.get_wires())}")
```

### 6. Function Argument Types

**Problem:** `TypeError: function(): incompatible function arguments`

**Cause:** PyOpenMagnetics uses pybind11 which requires exact argument types.

**Solution:** Use positional arguments instead of keyword arguments:

```python
# For design_magnetics_from_converter():
# WRONG (kwargs):
result = PyOpenMagnetics.design_magnetics_from_converter(
    topology="flyback",
    converter=flyback_specs,
    max_results=5
)

# CORRECT (positional):
result = PyOpenMagnetics.design_magnetics_from_converter(
    "flyback",           # topology_name
    flyback_specs,       # converter_json
    5,                   # max_results
    "standard cores",    # core_mode_json
    False,               # use_ngspice
    None                 # weights_json
)
```

### 7. Waveform Data Format

**Problem:** Issues with operating point excitations

**Solution:** Waveforms must include both `data` (amplitude values) and `time` (timestamp values) arrays:

```python
operating_point = {
    "name": "Nominal",
    "conditions": {"ambientTemperature": 40},
    "excitationsPerWinding": [
        {
            "name": "Primary",
            "frequency": 100000,
            "current": {
                "waveform": {
                    "data": [0.2, 1.8, 1.8, 0.2],  # Current in Amps
                    "time": [0, 4.5e-6, 4.5e-6, 10e-6]  # Time in seconds
                }
            }
        }
    ]
}
```

### 8. Processing Inputs

**Best Practice:** Always use `process_inputs()` after `process_flyback()` to ensure harmonics are calculated:

```python
# Step 1: Process flyback specs
flyback_specs = {...}
inputs = PyOpenMagnetics.process_flyback(flyback_specs)

# Step 2: Process inputs (calculates harmonics for loss analysis)
processed = PyOpenMagnetics.process_inputs(inputs)

# Step 3: Get design recommendations
result = PyOpenMagnetics.calculate_advised_magnetics(
    processed, 
    5, 
    "standard cores"
)
```

### 9. Complete Working Example

```python
import PyOpenMagnetics

# Define flyback converter specifications
flyback_specs = {
    "inputVoltage": {"minimum": 185, "maximum": 265},
    "diodeVoltageDrop": 0.7,
    "currentRippleRatio": 0.3,
    "efficiency": 0.85,
    "desiredInductance": 500e-6,
    "desiredTurnsRatios": [15.0],
    "desiredDutyCycle": [[0.45]],
    "maximumDutyCycle": 0.45,
    "operatingPoints": [{
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 40
    }]
}

# Process flyback converter
inputs = PyOpenMagnetics.process_flyback(flyback_specs)

# Get automatic design recommendations
result = PyOpenMagnetics.calculate_advised_magnetics(
    inputs,
    5,  # max_results
    "standard cores"  # core_mode (lowercase!)
)

# Process results
if isinstance(result, dict) and "data" in result:
    designs = result["data"]
    if isinstance(designs, list):
        print(f"Found {len(designs)} designs")
        for i, design in enumerate(designs):
            mas = design["mas"]
            score = design["scoring"]
            magnetic = mas["magnetic"]
            
            core = magnetic["core"]["functionalDescription"]
            print(f"\nDesign #{i+1} (Score: {score:.2f}):")
            print(f"  Core: {core['shape']['name']} / {core['material']['name']}")
```

### 10. Debugging Tips

1. **Enable logging:**
```python
PyOpenMagnetics.set_log_level("DEBUG")
```

2. **Check database status:**
```python
print(f"Materials empty: {PyOpenMagnetics.is_core_material_database_empty()}")
print(f"Shapes empty: {PyOpenMagnetics.is_core_shape_database_empty()}")
```

3. **Validate JSON structure:**
```python
import json

# Pretty-print inputs to verify structure
print(json.dumps(inputs, indent=2, default=str))
```

4. **Check function signatures:**
```python
# Use help() or check PyOpenMagnetics.pyi type stubs
help(PyOpenMagnetics.calculate_advised_magnetics)
```
```
## MAS Data Structures Reference

This section documents the Magnetic Agnostic Structure (MAS) JSON formats used by PyOpenMagnetics. Understanding these structures is essential for working with converter inputs and design outputs.

### 1. Inputs Structure

The `Inputs` structure is the main input to `calculate_advised_magnetics()`:

```python
inputs = {
    "designRequirements": {
        "application": None,                    # Optional: application type
        "insulation": None,                     # Optional: insulation requirements
        "isolationSides": ["primary", "secondary"],  # Isolation sides for windings
        "leakageInductance": None,              # Optional: leakage inductance limits
        "magnetizingInductance": {              # REQUIRED
            "nominal": 0.001,                   # Target inductance in Henries
            "minimum": None,                    # Optional: minimum acceptable
            "maximum": None,                    # Optional: maximum acceptable
            "excludeMinimum": None,
            "excludeMaximum": None
        },
        "market": None,
        "maximumDimensions": None,              # Optional: size constraints
        "maximumWeight": None,                  # Optional: weight constraints
        "name": None,
        "operatingTemperature": None,
        "strayCapacitance": None,
        "subApplication": None,
        "terminalType": None,
        "topology": "Flyback Converter",        # Auto-set by process_flyback()
        "turnsRatios": [                        # REQUIRED for multi-winding
            {
                "nominal": 15.0,                # Turns ratio (Np/Ns)
                "minimum": None,
                "maximum": None,
                "excludeMinimum": None,
                "excludeMaximum": None
            }
        ],
        "wiringTechnology": None
    },
    "operatingPoints": [                        # List of operating conditions
        {
            "conditions": {
                "ambientTemperature": 40.0,     # °C
                "ambientRelativeHumidity": None,
                "cooling": None,
                "name": None
            },
            "excitationsPerWinding": [          # Current/voltage waveforms
                {
                    "name": "Primary",
                    "frequency": 100000,        # Hz
                    "current": {
                        "harmonics": {          # Auto-calculated by process_inputs()
                            "amplitudes": [...],
                            "frequencies": [...]
                        }
                    },
                    "voltage": None             # Optional
                }
            ]
        }
    ]
}
```

### 2. Design Results Structure

Output from `calculate_advised_magnetics()`:

```python
result = {
    "data": [                                   # List of ranked designs
        {
            "mas": {                            # Complete MAS object
                "inputs": {...},                # Design requirements used
                "magnetic": {                   # The actual magnetic design
                    "core": {...},              # Core specification
                    "coil": {...}               # Coil/winding specification
                },
                "outputs": {                    # Calculated after simulation
                    "coreLosses": 0.5,          # Watts
                    "windingLosses": 1.2,       # Watts
                    "temperatureRise": 40       # Kelvin
                }
            },
            "scoring": 2.0,                     # Overall design score (higher is better)
            "scoringPerFilter": {               # Individual filter scores
                "MagnetizingInductance": 1.0,
                "WindingWindow": 1.0,
                "Saturation": 1.0
            }
        }
    ]
}
```

### 3. Core Specification Structure

```python
core = {
    "functionalDescription": {
        "type": "two-piece set",                # "two-piece set", "toroidal", "closed shape"
        "shape": {                              # Core shape definition
            "name": "E 42/21/15",               # Shape name
            "family": "e",                      # Shape family
            "dimensions": {...},                # Physical dimensions
            "magneticCircuit": "open"
        },
        "material": {                           # Core material
            "name": "3C95",                     # Material name
            "manufacturerInfo": {
                "name": "Ferroxcube"
            },
            "permeability": {...},              # Initial permeability vs temp/freq
            "saturation": [...],                # B-H saturation curve
            "volumetricLosses": {...}           # Core loss coefficients
        },
        "gapping": [                            # Air gap specification
            {
                "type": "subtractive",          # "subtractive", "additive", "distributed"
                "length": 0.001                 # Gap length in meters
            }
        ],
        "numberStacks": 1                       # Number of stacked cores
    },
    "processedDescription": {                   # Auto-calculated by calculate_core_data()
        "effectiveParameters": {
            "effectiveArea": 1.57e-4,           # Ae in m²
            "effectiveLength": 0.097,           # le in meters
            "effectiveVolume": 1.52e-5          # Ve in m³
        }
    }
}
```

### 4. Coil/Winding Specification

```python
coil = {
    "functionalDescription": [                  # List of windings
        {
            "name": "Primary",
            "numberTurns": 45,
            "numberParallels": 1,
            "wire": {                           # Wire specification
                "name": "Round 0.4 - Grade 1",  # or full wire dict
                "type": "round",                # "round", "litz", "rectangular", "foil"
                "standard": "IEC 60317",
                "conductingDiameter": 0.0004,
                "outerDiameter": 0.000442
            },
            "isolationSide": "primary"          # "primary", "secondary", "tertiary"
        },
        {
            "name": "Secondary",
            "numberTurns": 5,
            "numberParallels": 2,
            "wire": "Round 0.8 - Grade 1",
            "isolationSide": "secondary"
        }
    ],
    "sectionsDescription": {...},               # Auto-generated by wind()
    "layersDescription": {...},                 # Auto-generated by wind()
    "turnsDescription": {...}                   # Auto-generated by wind()
}
```

### 5. Operating Point with Waveforms

For manual waveform definition (not using process_flyback()):

```python
operating_point = {
    "name": "Nominal",
    "conditions": {
        "ambientTemperature": 25,               # °C
        "altitude": 0                           # meters
    },
    "excitationsPerWinding": [
        {
            "name": "Primary",
            "frequency": 100000,                # Hz
            "current": {
                "waveform": {                   # Time-domain waveform
                    "data": [0.2, 1.8, 1.8, 0.2],  # Current samples [A]
                    "time": [0, 4.5e-6, 4.5e-6, 10e-6]  # Time samples [s]
                }
                # OR use "harmonics" for frequency domain (auto-calculated)
            },
            "voltage": {
                "waveform": {
                    "data": [311, 311, 0, 0],   # Voltage samples [V]
                    "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                }
            }
        }
    ]
}
```

**Note:** When using `process_flyback()`, the operating points are automatically generated from your converter specifications. The `process_inputs()` function then calculates harmonics from the waveforms for accurate loss analysis.

### 6. Wire Specification Formats

**By Name (Simplest):**
```python
wire = "Round 0.5 - Grade 1"  # String name from database
```

**By Full Specification:**
```python
wire = {
    "type": "round",                            # "round", "litz", "rectangular", "foil"
    "standard": "IEC 60317",
    "name": "Round 0.5 - Grade 1",
    "conductingDiameter": 0.0005,               # Bare wire diameter (m)
    "outerDiameter": 0.000563,                  # With insulation (m)
    "material": "copper"
}
```

**Litz Wire:**
```python
wire = {
    "type": "litz",
    "name": "Litz 100x0.1",
    "numberConductors": 100,
    "outerDiameter": 0.0015,
    "strand": {
        "conductingDiameter": 0.0001,
        "outerDiameter": 0.00012
    }
}
```

### 7. Accessing Design Results

```python
# Get results from calculate_advised_magnetics()
result = PyOpenMagnetics.calculate_advised_magnetics(inputs, 5, "standard cores")

if isinstance(result, dict) and "data" in result:
    designs = result["data"]
    
    for i, design in enumerate(designs):
        mas = design["mas"]
        score = design["scoring"]
        magnetic = mas["magnetic"]
        
        # Core information
        core = magnetic["core"]["functionalDescription"]
        print(f"Design {i+1}: Score={score:.2f}")
        print(f"  Core: {core['shape']['name']} / {core['material']['name']}")
        print(f"  Gap: {core['gapping'][0]['length']*1e3:.2f} mm")
        
        # Winding information
        coil = magnetic["coil"]["functionalDescription"]
        for winding in coil:
            print(f"  {winding['name']}: {winding['numberTurns']} turns")
        
        # Losses (after simulation)
        if "outputs" in mas:
            outputs = mas["outputs"]
            print(f"  Core Losses: {outputs.get('coreLosses', 0):.3f} W")
            print(f"  Winding Losses: {outputs.get('windingLosses', 0):.3f} W")
```
