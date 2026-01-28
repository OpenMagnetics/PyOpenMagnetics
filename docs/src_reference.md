# PyOpenMagnetics C++ Bindings Reference

## Overview

The `src/` directory contains **24 files** (12 headers, 12 implementations) that create Python bindings for the OpenMagnetics C++ engine via pybind11. The module exposes **183 Python functions** organized into 11 categories.

**Module Name:** `PyOpenMagnetics`

## Architecture

```
User Python Code
       |
       v
module.cpp (pybind11 entry point)
       |
       v
[Python Bindings Registration]
       |-- database.cpp      (Load/cache designs)
       |-- core.cpp          (Material & geometry)
       |-- wire.cpp          (Wire database)
       |-- bobbin.cpp        (Coil support)
       |-- winding.cpp       (Wire placement)
       |-- advisers.cpp      (Design recommendation)
       |-- losses.cpp        (Loss calculations)
       |-- simulation.cpp    (Full EM simulation)
       |-- plotting.cpp      (SVG visualization)
       |-- settings.cpp      (Config & defaults)
       +-- utils.cpp         (Helper functions)
       |
       v
OpenMagnetics C++ Library (MKF engine)
       |
       v
MAS Objects (JSON-serializable design specs)
```

## File Reference

### 1. module.cpp - Entry Point
**Purpose:** Main pybind11 module definition
**Key:** `PYBIND11_MODULE(PyOpenMagnetics, m)` creates the module and registers all 11 binding namespaces.

### 2. common.h - Shared Infrastructure
**Purpose:** Global headers, pybind11/JSON includes, MAS library integration
**Key Declarations:**
```cpp
extern std::map<std::string, OpenMagnetics::Mas> masDatabase;  // In-memory MAS cache
```
**Dependencies:** Foundation for all other modules

### 3. database.h/cpp - Database Access & Caching
**Purpose:** Load and manage magnetic component databases; cache MAS objects

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `load_databases` | `databases_json` | void | Load all component databases |
| `read_databases` | `path`, `add_internal_data` | str | Read NDJSON files |
| `load_mas` | `key`, `mas_json`, `expand` | str | Cache MAS object |
| `load_magnetic` | `key`, `magnetic_json`, `expand` | str | Cache magnetic design |
| `read_mas` | `key` | json | Retrieve cached MAS |
| `load_core_materials` | `file` (optional) | size_t | Load materials database |
| `load_core_shapes` | `file` (optional) | size_t | Load shapes database |
| `load_wires` | `file` (optional) | size_t | Load wires database |
| `clear_databases` | - | void | Reset all caches |
| `is_core_material_database_empty` | - | bool | Check if empty |
| `is_core_shape_database_empty` | - | bool | Check if empty |
| `is_wire_database_empty` | - | bool | Check if empty |
| `load_magnetics_from_file` | `path`, `expand` | str | Load from NDJSON |
| `clear_magnetic_cache` | - | str | Clear cached magnetics |

### 4. core.h/cpp - Core Materials & Geometry
**Purpose:** Query core materials/shapes and perform core calculations

#### Material Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_core_materials` | - | json array | All available materials |
| `get_core_material_names` | - | json array | Material name list |
| `get_core_material_names_by_manufacturer` | `manufacturer` | json array | Filtered by manufacturer |
| `find_core_material_by_name` | `name` | json | Complete material data |
| `get_material_permeability` | `name`, `temp`, `dcBias`, `freq` | double | Permeability at conditions |
| `get_material_resistivity` | `name`, `temp` | double | Resistivity (Ohm*m) |
| `get_core_material_steinmetz_coefficients` | `name`, `freq` | json | k, alpha, beta coefficients |
| `get_core_temperature_dependant_parameters` | `core_data`, `temp` | json | Bsat, Hsat, permeability |

#### Shape Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_core_shapes` | - | json array | All shapes |
| `get_core_shape_families` | - | json array | Shape families (E, ETD, PQ...) |
| `get_core_shape_names` | `include_toroidal` | json array | Shape names |
| `find_core_shape_by_name` | `name` | json | Complete shape data |
| `calculate_shape_data` | `shape_json` | json | Derived shape properties |

#### Core Calculation Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `calculate_core_data` | `core_json`, `include_material` | json | Full core analysis |
| `calculate_core_processed_description` | `core_json` | json | Effective parameters |
| `calculate_core_geometrical_description` | `core_json` | json array | 3D geometry |
| `calculate_core_gapping` | `core_json` | json array | Gap configuration |
| `calculate_gap_reluctance` | `gap_data`, `model` | json | Gap reluctance |
| `calculate_inductance_from_number_turns_and_gapping` | `core`, `coil`, `op`, `models` | double | Inductance (H) |
| `calculate_number_turns_from_gapping_and_inductance` | `core`, `inputs`, `models` | double | Required turns |
| `calculate_gapping_from_number_turns_and_inductance` | `core`, `coil`, `inputs`, `gap_type`, `decimals`, `models` | json | Core with gaps |
| `calculate_core_maximum_magnetic_energy` | `core_json`, `op_json` | double | Max energy (J) |
| `calculate_saturation_current` | `magnetic_json`, `temp` | double | Saturation current (A) |

#### Availability Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_available_shape_families` | - | list[str] | All shape families |
| `get_available_core_materials` | `manufacturer` (opt) | list[str] | Materials list |
| `get_available_core_manufacturers` | - | list[str] | Manufacturers |
| `get_available_core_shapes` | - | list[str] | Shape names |
| `get_available_cores` | - | json array | Pre-configured cores |

### 5. wire.h/cpp - Wire Database & Calculations
**Purpose:** Query wire database and compute wire properties

#### Database Access
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_wires` | - | json array | All wires |
| `get_wire_names` | - | json array | Wire names |
| `get_wire_materials` | - | json array | Conductor materials |
| `find_wire_by_name` | `name` | json | Wire data |
| `find_wire_by_dimension` | `dim`, `type`, `standard` | json | Closest match |
| `get_wire_data_by_standard_name` | `standard_name` | json | e.g., "AWG 24" |

#### Dimension Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_wire_outer_diameter_bare_litz` | `diam`, `n_cond`, `grade`, `std` | double | Bare litz diameter |
| `get_wire_outer_diameter_served_litz` | `diam`, `n_cond`, `grade`, `n_layers`, `std` | double | Served diameter |
| `get_wire_outer_diameter_insulated_litz` | `diam`, `n_cond`, `n_layers`, `thick`, `grade`, `std` | double | Insulated diameter |
| `get_wire_outer_diameter_enamelled_round` | `diam`, `grade`, `std` | double | Enamelled diameter |
| `get_wire_outer_width_rectangular` | `width`, `grade`, `std` | double | Rectangular width |
| `get_wire_outer_height_rectangular` | `height`, `grade`, `std` | double | Rectangular height |
| `get_outer_dimensions` | `wire_json` | list[double] | [width, height] |

#### Coating Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_coating` | `wire_json` | json | Insulation data |
| `get_coating_thickness` | `wire_json` | double | Thickness (m) |
| `get_coating_relative_permittivity` | `wire_json` | double | Dielectric constant |
| `get_available_wire_types` | - | list[str] | round, litz, rectangular, foil |
| `get_available_wire_standards` | - | list[str] | IEC 60317, NEMA, etc. |

### 6. bobbin.h/cpp - Bobbin Management
**Purpose:** Query and create bobbins

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_bobbins` | - | json array | All bobbins |
| `get_bobbin_names` | - | json array | Bobbin names |
| `find_bobbin_by_name` | `name` | json | Bobbin data |
| `create_basic_bobbin` | `core_data`, `null_dims` | json | Auto-create from core |
| `create_basic_bobbin_by_thickness` | `core_data`, `thickness` | json | With specific thickness |
| `calculate_bobbin_data` | `magnetic_json` | json | Compute properties |
| `check_if_fits` | `bobbin`, `dimension`, `is_horiz` | bool | Validate fit |

### 7. winding.h/cpp - Winding Placement Engine
**Purpose:** Place wires in magnetic component windings

#### Winding Methods
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `wind` | `coil`, `reps`, `proportions`, `pattern`, `margins` | json | Main winding algorithm |
| `wind_planar` | `coil`, `stackup`, `borders`, `wire_dist`, `insul_thick`, `core_dist` | json | PCB winding |
| `wind_by_sections` | `coil`, `reps`, `proportions`, `pattern`, `insul_thick` | json | Section-based |
| `wind_by_layers` | `coil`, `insul_layers`, `insul_thick` | json | Layer-based |
| `wind_by_turns` | `coil` | json | Turn placement |
| `delimit_and_compact` | `coil` | json | Optimize space |

#### Analysis Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_layers_by_winding_index` | `coil`, `index` | json array | Layers for winding |
| `get_layers_by_section` | `coil`, `section` | json array | Layers in section |
| `are_sections_and_layers_fitting` | `coil` | bool | Validate space |
| `calculate_number_turns` | `n_primary`, `design_req` | list[int] | Turns per winding |

#### Insulation Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_insulation_materials` | - | json array | All insulation specs |
| `find_insulation_material_by_name` | `name` | json | Material data |
| `calculate_insulation` | `inputs_json` | json | Safety requirements |
| `get_available_winding_orientations` | - | list[str] | contiguous, overlapping |
| `get_available_coil_alignments` | - | list[str] | inner, outer, spread, centered |

### 8. advisers.h/cpp - Design Recommendation
**Purpose:** Recommend optimal core/magnetic designs

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `calculate_advised_cores` | `inputs`, `weights`, `max_results`, `core_mode` | json array | Recommended cores |
| `calculate_advised_magnetics` | `inputs`, `max_results`, `core_mode` | json array | Complete designs |
| `calculate_advised_magnetics_from_catalog` | `inputs`, `catalog`, `max_results` | json | From custom catalog |
| `calculate_advised_magnetics_from_cache` | `inputs`, `filter_flow`, `max_results` | json | From cached designs |

**Core Mode:** `AVAILABLE_CORES` or `STANDARD_CORES`
**Weights:** `COST`, `EFFICIENCY`, `DIMENSIONS`

### 9. losses.h/cpp - Loss Calculations
**Purpose:** Calculate core and winding losses

#### Core Losses
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `calculate_core_losses` | `core`, `coil`, `inputs`, `models` | json | Core loss + B_peak |
| `get_core_losses_model_information` | `material` | json | Model descriptions |
| `calculate_steinmetz_coefficients` | `data`, `ranges` | json | Fit k, alpha, beta |

**Loss Models:** STEINMETZ, IGSE, MSE, BARG, ROSHEN, ALBACH

#### Winding Losses
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `calculate_winding_losses` | `magnetic`, `op`, `temp` | json | Total winding loss |
| `calculate_ohmic_losses` | `coil`, `op`, `temp` | json | DC I²R losses |
| `calculate_proximity_effect_losses` | `coil`, `temp`, `output`, `field` | json | Proximity losses |
| `calculate_skin_effect_losses` | `coil`, `output`, `temp` | json | Skin losses |

#### Per-Meter Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `calculate_dc_resistance_per_meter` | `wire`, `temp` | double | DC R (Ohm/m) |
| `calculate_dc_losses_per_meter` | `wire`, `current`, `temp` | double | DC loss (W/m) |
| `calculate_skin_ac_factor` | `wire`, `current`, `temp` | double | Rac/Rdc ratio |
| `calculate_effective_skin_depth` | `material`, `current`, `temp` | double | Skin depth (m) |

### 10. simulation.h/cpp - Full EM Simulation
**Purpose:** Complete magnetic component simulation

#### Main Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `simulate` | `inputs`, `magnetic`, `models` | json | Full MAS with outputs |
| `export_magnetic_as_subcircuit` | `magnetic` | json | SPICE netlist |
| `mas_autocomplete` | `mas`, `config` | json | Fill missing fields |
| `magnetic_autocomplete` | `magnetic`, `config` | json | Complete magnetic |
| `process_inputs` | `inputs` | json | **CRITICAL:** Add harmonics |

#### Matrix Functions
| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `calculate_inductance_matrix` | `magnetic`, `freq`, `models` | json | Self & mutual L |
| `calculate_leakage_inductance` | `magnetic`, `freq`, `source_idx` | json | Leakage L |
| `calculate_dc_resistance_per_winding` | `coil`, `temp` | json array | DC R per winding |
| `calculate_resistance_matrix` | `magnetic`, `temp`, `freq` | json | AC R matrix |
| `calculate_stray_capacitance` | `coil`, `op`, `models` | json | Parasitic caps |

### 11. plotting.h/cpp - SVG Visualization
**Purpose:** Generate SVG visualizations

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `plot_core` | `magnetic`, `path` (opt) | json | Core cross-section |
| `plot_magnetic` | `magnetic`, `path` (opt) | json | Full assembly |
| `plot_magnetic_field` | `magnetic`, `op`, `path` (opt) | json | H-field visualization |
| `plot_electric_field` | `magnetic`, `op`, `path` (opt) | json | E-field visualization |
| `plot_wire` | `wire`, `path` (opt) | json | Wire cross-section |
| `plot_bobbin` | `magnetic`, `path` (opt) | json | Bobbin structure |

**Return:** `{success: bool, svg: str, error: str}`

### 12. settings.h/cpp - Configuration
**Purpose:** Global configuration and defaults

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `get_constants` | - | dict | Physical constants |
| `get_defaults` | - | dict | Default models & values |
| `get_settings` | - | json | Current settings |
| `set_settings` | `settings` | void | Update settings |
| `reset_settings` | - | void | Reset to defaults |
| `get_default_models` | - | json | Default model selections |

**Key Constants:** vacuumPermeability, vacuumPermittivity, residualGap, minimumNonResidualGap

### 13. utils.h/cpp - Utilities
**Purpose:** Signal processing and helper functions

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `resolve_dimension_with_tolerance` | `dim_json` | double | Extract nominal value |
| `calculate_basic_processed_data` | `waveform` | json | RMS, peak, offset |
| `calculate_harmonics` | `waveform`, `freq` | json | FFT analysis |
| `calculate_sampled_waveform` | `waveform`, `freq` | json | Resample uniformly |
| `calculate_instantaneous_power` | `excitation` | double | P(t) value |
| `calculate_rms_power` | `excitation` | double | Average power |
| `calculate_reflected_secondary` | `primary`, `turns_ratio` | json | Secondary reflection |
| `calculate_reflected_primary` | `secondary`, `turns_ratio` | json | Primary reflection |

---

## Module Dependencies

| Module | Depends On |
|--------|-----------|
| database | common |
| core | common |
| wire | common |
| bobbin | common, core, wire |
| winding | common, core, wire, bobbin |
| advisers | common, database, core, wire, bobbin, winding, settings |
| losses | common, core, winding, wire |
| simulation | common, core, winding, losses, settings |
| plotting | common, simulation |
| settings | common |
| utils | common, settings |

**Critical Path:** `advisers.cpp` depends on all other modules

---

## Function Count by Category

| Category | Count | Purpose |
|----------|-------|---------|
| Database | 15 | Data loading & caching |
| Advisers | 4 | Design recommendation |
| Core | 42 | Materials, shapes, calculations |
| Wire | 32 | Wire database & selection |
| Bobbin | 8 | Bobbin lookup & fitting |
| Winding | 23 | Coil placement & insulation |
| Losses | 22 | Core & winding loss models |
| Simulation | 16 | Full EM simulation & matrices |
| Plotting | 6 | SVG visualization |
| Settings | 6 | Configuration & constants |
| Utils | 9 | Signal processing |
| **TOTAL** | **183** | Complete magnetic design API |

---

## Key Design Patterns

1. **JSON-Based API:** All complex types use JSON for data exchange
2. **Error Handling:** Functions return `"Exception: ..."` strings on error
3. **Models Parameter:** Loss/reluctance models are pluggable via `models_json`
4. **Database Caching:** MAS objects stored in `masDatabase` for reuse
5. **process_inputs() Required:** Must call before adviser functions to add harmonics

---

## Usage Examples

### Load Databases and Query Materials
```python
import PyOpenMagnetics

# Load databases (typically done once at startup)
PyOpenMagnetics.load_core_materials()
PyOpenMagnetics.load_core_shapes()
PyOpenMagnetics.load_wires()

# Query materials
materials = PyOpenMagnetics.get_core_material_names()
n87 = PyOpenMagnetics.find_core_material_by_name("N87")
steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients("N87", 100000)
```

### Calculate Core Properties
```python
# Get shape and create core
shape = PyOpenMagnetics.find_core_shape_by_name("E 42/21/15")
core_data = PyOpenMagnetics.calculate_core_data(core_json, True)

# Calculate inductance
L = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
    core, coil, operating_point, models
)
```

### Run Full Simulation
```python
# CRITICAL: Always process inputs first
processed = PyOpenMagnetics.process_inputs(inputs)

# Get design recommendations
magnetics = PyOpenMagnetics.calculate_advised_magnetics(
    processed, 5, "STANDARD_CORES"
)

# Full simulation with losses
result = PyOpenMagnetics.simulate(processed, magnetic, models)
```

### Calculate Losses
```python
models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}

# Core losses
core_loss = PyOpenMagnetics.calculate_core_losses(core, coil, inputs, models)

# Winding losses
winding_loss = PyOpenMagnetics.calculate_winding_losses(magnetic, op, 85)
```

### Generate Visualizations
```python
# Plot core cross-section
result = PyOpenMagnetics.plot_core(magnetic)
if result["success"]:
    svg_content = result["svg"]

# Plot complete magnetic assembly
result = PyOpenMagnetics.plot_magnetic(magnetic, "/path/to/output.svg")
```
