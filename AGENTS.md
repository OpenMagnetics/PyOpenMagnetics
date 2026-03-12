# AGENTS.md â€” PyOpenMagnetics AI Assistant Guide

> **This file is the SINGLE SOURCE OF TRUTH for any AI agent using PyOpenMagnetics.**
> Every instruction was derived from reading the C++ source code
> (`converter.cpp`, `magnetics.cpp`, `cores.cpp`, `wires.cpp`, `settings.cpp`,
> `database.cpp`, `CoreAdviser.h/.cpp`, `MagneticAdviser.h/.cpp`, `MAS.hpp`,
> `Flyback.h/.cpp`, all converter model headers, and all adviser files)
> and **validated by running the library**.
>
> When this document contradicts the `.pyi` stubs or bundled examples,
> **trust this document**.

---

## â›” THE #1 RULE â€” DO NOT USE MANUAL CALCULATIONS

When a user asks you to design a magnetic component for a power converter:

1. **ALWAYS** use `design_magnetics_from_converter()` first (Method A â€” single call)
2. If Method A fails (e.g., ngspice cannot initialize), fall back to
   `process_converter()` â†’ `calculate_advised_magnetics()` (Method B)
3. **NEVER** calculate turns ratios, inductance, core sizes, or wire gauges manually
4. **NEVER** fall back to textbook formulas â€” fix the API call instead

The MKF engine handles complex magnetic field distributions, temperature-dependent
material properties, geometrical fringing effects, and real commercial core database
constraints that manual formulas cannot replicate.

---

## 1. Installation

```bash
pip install PyOpenMagnetics
```

If the `.whl` is provided as base64-encoded parts:
```python
import base64
with open("pyopenmagnetics-1.3.0.whl.base64.partaa", "rb") as f:
    part_a = f.read()
with open("pyopenmagnetics-1.3.0.whl.base64.partab", "rb") as f:
    part_b = f.read()
whl_data = base64.b64decode(part_a + part_b)
with open("pyopenmagnetics.whl", "wb") as f:
    f.write(whl_data)
# Then: pip install pyopenmagnetics.whl
```

---

## 2. Import â€” CRITICAL (Most Agents Fail Here)

The package has **no `__init__.py`**. A bare `import PyOpenMagnetics` gives an
**empty namespace with 0 functions**. You MUST use `importlib`:

```python
import importlib.util, os, glob

pkg_dir = os.path.join(
    os.path.dirname(__import__('PyOpenMagnetics').__path__[0]),
    'PyOpenMagnetics'
)
so_files = glob.glob(os.path.join(pkg_dir, 'PyOpenMagnetics.cpython-*'))
assert so_files, f"No .so/.pyd found in {pkg_dir}"

spec = importlib.util.spec_from_file_location('PyOpenMagnetics', so_files[0])
PyOM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PyOM)

# MANDATORY â€” must call before any other function
PyOM.load_databases({})
```

**Verify:**
```python
assert len(dir(PyOM)) > 100, "Module not loaded properly"
assert hasattr(PyOM, 'design_magnetics_from_converter')
print(f"Materials: {len(PyOM.get_core_material_names())}")   # ~409
print(f"Shapes: {len(PyOM.get_core_shape_names(True))}")     # ~1301
```

---

## 3. Method A: `design_magnetics_from_converter()` (Preferred â€” Single Call)

This goes directly from converter specifications to complete, ranked magnetic
component designs in a single call.

### ngspice Is Bundled

ngspice is shipped inside the wheel at `.ngspice/lib/libngspice.so`. No
separate install needed. The C++ code **ignores** the `use_ngspice` parameter:
`(void)useNgspice;` â€” it always uses ngspice internally.

In sandboxed environments where `dlopen` is restricted, ngspice may fail to
initialize â€” use Method B with `use_ngspice=False` in that case.

### Signature (use POSITIONAL args â€” the .pyi has WRONG keyword names!)

```python
result = PyOM.design_magnetics_from_converter(
    topology_name,    # str â€” REQUIRED
    converter_json,   # dict â€” REQUIRED (BASE class schema, see Section 5)
    max_results,      # int â€” 1-10
    core_mode_json,   # str â€” "available cores" or "standard cores"
    use_ngspice,      # bool â€” IGNORED (always True internally)
    weights_json      # dict or None
)
```

### âš ï¸ The .pyi Stub Has WRONG Keyword Names

`.pyi` says: `topology=`, `converter=`, `core_mode=`, `weights=`.
Actual pybind11: `topology_name=`, `converter_json=`, `core_mode_json=`, `weights_json=`.
**Safest: use positional arguments.**

---

### ðŸš¨ Pass Python Dicts â€” NEVER json.dumps()!

The C++ pybind11 binding accepts **Python dicts directly**. `json.dumps()` turns
your dict into a **string** â†’ the C++ parser gets a string instead of an object
â†’ `"Input JSON does not conform to schema!"`.

```python
# âŒ WRONG â€” json.dumps() causes schema error
result = PyOM.design_magnetics_from_converter("flyback", json.dumps(converter), ...)
result = PyOM.design_magnetics_from_converter("flyback", converter, 3, json.dumps("STANDARD_CORES"), ...)

# âœ… CORRECT â€” pass Python dict and plain string
result = PyOM.design_magnetics_from_converter("flyback", converter, 3, "available cores", True, None)
```

### ðŸš¨ NEVER Abandon Method A After a Schema Error!

If `design_magnetics_from_converter` throws `"Input JSON does not conform to schema!"`,
the fix is to correct the JSON â€” **NOT** to fall back to `calculate_advised_cores` or
manual math. Common fixes:
1. Remove `json.dumps()` from all arguments
2. Use `"available cores"` (lowercase + space), not `"STANDARD_CORES"`
3. Use positional arguments, not keyword arguments
4. For offline flyback: use the Advanced schema with `desiredInductance`

---

## 4. The THREE Things That MUST Be Correct (All Verified)

### 4.1 `core_mode_json` Must Be LOWERCASE WITH SPACE

From `CoreAdviser.h` `from_json`:
```cpp
if (j == "available cores") x = CoreAdviserModes::AVAILABLE_CORES;
else if (j == "standard cores") x = CoreAdviserModes::STANDARD_CORES;
else if (j == "custom cores") x = CoreAdviserModes::CUSTOM_CORES;
else throw std::runtime_error("Input JSON does not conform to schema!");
```

| âŒ WRONG | âœ… CORRECT |
|---|---|
| `"AVAILABLE_CORES"` | `"available cores"` |
| `"STANDARD_CORES"` | `"standard cores"` |
| `"Available Cores"` | `"available cores"` |
| `0` (integer) | `"available cores"` |

- `"available cores"` â€” WE commercial cores (~1301 shapes, 60â€“120+ sec)
- `"standard cores"` â€” generic shapes (faster, fewer options)

### 4.2 Flyback `operatingPoints[].mode` - Optional When currentRippleRatio Is Set

The `mode` field is **optional** if `currentRippleRatio` is provided. The C++ code
will auto-infer the mode: CCM if ripple < 1.0, DCM if ripple >= 1.0.

If you omit both `mode` AND `currentRippleRatio`, you'll get an error:
`"Either current ripple ratio or mode is needed for the Flyback OperatingPoint Mode"`

Valid mode values:
- `"Continuous Conduction Mode"` (CCM — most common for >20W)
- `"Discontinuous Conduction Mode"` (DCM)
- `"Boundary Mode Operation"` (BCM)
- `"Quasi Resonant Mode"` (QR)

Other topologies (Buck, Boost, Forward, LLC) do **NOT** need a mode field.

### 4.3 Use BASE Class Schema (NOT AdvancedFlyback)

`design_magnetics_from_converter()` uses `OpenMagnetics::Flyback` (base).
`process_converter()` uses `OpenMagnetics::AdvancedFlyback`.

| Field | Method A (Base) | Method B (Advanced) |
|---|---|---|
| `desiredInductance` | âŒ Causes schema error | âœ… Required |
| `desiredTurnsRatios` | âŒ Causes schema error | âœ… Required |
| `desiredDutyCycle` | âŒ Causes schema error | âœ… Optional |
| `currentRippleRatio` | âœ… REQUIRED (Flyback/Boost/Forward) | âœ… Optional |
| `mode` in operatingPoints | Optional (auto-inferred if currentRippleRatio set) | Not needed |

---

## 5. Converter JSON Schemas â€” All Topologies (Verified from MAS.hpp)

### 5.1 Flyback â€” Method A (BASE class)

```python
flyback_base = {
    "currentRippleRatio": 0.4,          # REQUIRED (j.at)
    "diodeVoltageDrop": 0.5,            # REQUIRED (j.at)
    "efficiency": 0.88,                 # REQUIRED (j.at)
    "inputVoltage": {                   # REQUIRED (j.at)
        "minimum": 185.0,
        "nominal": 220.0,              # recommended
        "maximum": 265.0
    },
    "operatingPoints": [{               # REQUIRED (j.at)
        "ambientTemperature": 25.0,     # REQUIRED (j.at)
        "outputVoltages": [12.0],       # REQUIRED (j.at) â€” PLURAL
        "outputCurrents": [2.0],        # REQUIRED (j.at) â€” PLURAL
        "switchingFrequency": 100000.0, # optional (get_stack_optional)
        "mode": "Continuous Conduction Mode"  # Optional if currentRippleRatio is set (auto-inferred)
    }],
    "maximumDutyCycle": 0.45,           # optional
    "maximumDrainSourceVoltage": 800.0  # optional
}
```

### 5.2 Flyback â€” Method B (AdvancedFlyback)

```python
flyback_advanced = {
    "inputVoltage": {"minimum": 185, "maximum": 265},
    "desiredInductance": 800e-6,         # AdvancedFlyback only
    "desiredTurnsRatios": [13.5],        # AdvancedFlyback only
    "desiredDutyCycle": [[0.45, 0.45]],  # AdvancedFlyback only
    "maximumDutyCycle": 0.45,
    "efficiency": 0.88,
    "diodeVoltageDrop": 0.5,
    "currentRippleRatio": 0.4,
    "operatingPoints": [{
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 25
    }]
}
```

### 5.3 Buck â€” Method A (BASE class)

```python
buck_base = {
    "diodeVoltageDrop": 0.5,            # REQUIRED (j.at)
    "inputVoltage": {"minimum": 10.0, "maximum": 14.0},  # REQUIRED
    "operatingPoints": [{
        "ambientTemperature": 25.0,     # REQUIRED
        "outputVoltage": 3.3,           # REQUIRED â€” âš ï¸ SINGULAR!
        "outputCurrent": 5.0,           # REQUIRED â€” âš ï¸ SINGULAR!
        "switchingFrequency": 500000.0  # REQUIRED (j.at)
    }]
}
```

### 5.4 Boost â€” Method A (BASE class)

```python
boost_base = {
    "currentRippleRatio": 0.3,          # REQUIRED (j.at)
    "diodeVoltageDrop": 0.7,            # REQUIRED (j.at)
    "efficiency": 0.92,                 # REQUIRED (j.at)
    "inputVoltage": {"minimum": 5.0, "maximum": 5.0},  # REQUIRED
    "operatingPoints": [{
        "ambientTemperature": 25.0,     # REQUIRED
        "outputVoltage": 12.0,          # REQUIRED â€” âš ï¸ SINGULAR!
        "outputCurrent": 1.0,           # REQUIRED â€” âš ï¸ SINGULAR!
        "switchingFrequency": 100000.0  # REQUIRED (j.at)
    }]
}
```

### 5.5 Forward (Single-Switch, Two-Switch, Active-Clamp) â€” Method A

```python
forward_base = {
    "currentRippleRatio": 0.4,          # REQUIRED (j.at)
    "diodeVoltageDrop": 0.5,            # REQUIRED (j.at)
    "inputVoltage": {"minimum": 36.0, "maximum": 72.0},
    "operatingPoints": [{
        "ambientTemperature": 25.0,     # REQUIRED (j.at)
        "outputVoltages": [5.0],        # REQUIRED (j.at) â€” PLURAL
        "outputCurrents": [10.0],       # REQUIRED (j.at) â€” PLURAL
        "switchingFrequency": 200000.0  # REQUIRED (j.at) for Forward!
    }]
    # optional: "efficiency", "dutyCycle", "maximumSwitchCurrent"
}
```
Use topology strings: `"single_switch_forward"`, `"two_switch_forward"`, `"active_clamp_forward"`.

### 5.6 LLC — Method A (BASE class)

```python
llc_base = {
    "inputVoltage": {"minimum": 380.0, "maximum": 420.0},  # REQUIRED (j.at)
    "minSwitchingFrequency": 100000.0,  # REQUIRED (j.at)
    "maxSwitchingFrequency": 300000.0,  # REQUIRED (j.at)
    "operatingPoints": [{               # REQUIRED (j.at)
        "ambientTemperature": 25.0,
        "outputVoltages": [12.0],       # REQUIRED — PLURAL
        "outputCurrents": [5.0],        # REQUIRED — PLURAL
        "switchingFrequency": 200000.0  # Operating frequency
    }],
    # optional fields:
    "efficiency": 0.95,                 # optional
    "qualityFactor": 0.5,               # optional
    "resonantFrequency": 150000.0       # optional
}
```


### 5.7 PushPull â€” Same Schema as Forward

### 5.8 Singular vs Plural Field Names (Critical!)

| Topology | outputVoltage(s) | outputCurrent(s) |
|---|---|---|
| Flyback | `outputVoltages` (PLURAL, list) | `outputCurrents` (PLURAL, list) |
| Forward | `outputVoltages` (PLURAL, list) | `outputCurrents` (PLURAL, list) |
| PushPull | `outputVoltages` (PLURAL, list) | `outputCurrents` (PLURAL, list) |
| LLC | `outputVoltages` (PLURAL, list) | `outputCurrents` (PLURAL, list) |
| Buck | `outputVoltage` (SINGULAR, float) | `outputCurrent` (SINGULAR, float) |
| Boost | `outputVoltage` (SINGULAR, float) | `outputCurrent` (SINGULAR, float) |
| DualActiveBridge | `outputVoltage` (SINGULAR) | `outputCurrent` (SINGULAR) |

### 5.9 How to Estimate Flyback Parameters

If user says "220V to 12V, 2A" without detail:
```
Vin_dc_min â‰ˆ 185 Ã— âˆš2 Ã— 0.9 â‰ˆ 235V
Dmax = 0.45, Î· = 0.88
n = (12+0.5)Ã—0.55 / (235Ã—0.45Ã—0.88) â‰ˆ 0.074
turnsRatio = 1/n â‰ˆ 13.5   â†’ for desiredTurnsRatios (Method B only)
Lm â‰ˆ 800 ÂµH                â†’ for desiredInductance (Method B only)
```

---

## 6. Complete Working Examples

### Method A: `design_magnetics_from_converter()` (single call)

```python
import importlib.util, os, glob, json

# Load module
pkg_dir = os.path.join(
    os.path.dirname(__import__('PyOpenMagnetics').__path__[0]),
    'PyOpenMagnetics'
)
so_files = glob.glob(os.path.join(pkg_dir, 'PyOpenMagnetics.cpython-*'))
spec = importlib.util.spec_from_file_location('PyOpenMagnetics', so_files[0])
PyOM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PyOM)
PyOM.load_databases({})

# Define converter (BASE Flyback schema â€” NO desiredInductance!)
flyback = {
    "currentRippleRatio": 0.4,
    "diodeVoltageDrop": 0.5,
    "efficiency": 0.88,
    "inputVoltage": {"minimum": 185.0, "nominal": 220.0, "maximum": 265.0},
    "maximumDutyCycle": 0.45,
    "operatingPoints": [{
        "ambientTemperature": 25.0,
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000.0,
        "mode": "Continuous Conduction Mode"   # Optional if currentRippleRatio is set (auto-inferred)
    }]
}

# Design (takes 60-120s with "available cores")
result = PyOM.design_magnetics_from_converter(
    "flyback", flyback, 1, "available cores", True, None
)

if isinstance(result, dict) and "error" in result:
    print(f"Method A failed: {result['error']}")
    # â†’ Use Method B
else:
    d = result[0]
    mas_obj, score = (d[0], d[1]) if isinstance(d, (list, tuple)) else (d, "N/A")
    core = mas_obj["magnetic"]["core"]["functionalDescription"]
    coil = mas_obj["magnetic"]["coil"]["functionalDescription"]
    print(f"Core:  {core['shape'].get('name','?') if isinstance(core['shape'], dict) else core['shape']}")
    print(f"Material: {core['material'].get('name','?') if isinstance(core['material'], dict) else core['material']}")
    for w in coil:
        print(f"  {w.get('name','?')}: {w.get('numberTurns','?')} turns")
```

### Method B: `process_converter()` â†’ `calculate_advised_magnetics()` (no ngspice needed)

```python
# Step 1: Process converter (AdvancedFlyback schema)
flyback_adv = {
    "inputVoltage": {"minimum": 185, "maximum": 265},
    "desiredInductance": 800e-6,
    "desiredTurnsRatios": [13.5],
    "desiredDutyCycle": [[0.45, 0.45]],
    "maximumDutyCycle": 0.45,
    "efficiency": 0.88,
    "diodeVoltageDrop": 0.5,
    "currentRippleRatio": 0.4,
    "operatingPoints": [{
        "outputVoltages": [12.0],
        "outputCurrents": [2.0],
        "switchingFrequency": 100000,
        "ambientTemperature": 25
    }]
}
processed = PyOM.process_converter("flyback", flyback_adv, use_ngspice=False)
assert "error" not in processed

# Step 2: Feed into adviser (with optional weights)
mas_inputs = {
    "designRequirements": processed["designRequirements"],
    "operatingPoints":    processed["operatingPoints"]
}
designs = PyOM.calculate_advised_magnetics(
    mas_inputs, 1, "available cores",
    {"efficiency": 2.0, "cost": 1.0, "dimensions": 0.5}  # optional weights
)

# Step 3: Parse
d = designs[0]
mas_obj, score = (d[0], d[1]) if isinstance(d, (list, tuple)) else (d, "N/A")
core = mas_obj["magnetic"]["core"]["functionalDescription"]
coil = mas_obj["magnetic"]["coil"]["functionalDescription"]
print(f"Core: {core['shape'].get('name','?')}, Material: {core['material'].get('name','?')}")
for w in coil:
    print(f"  {w['name']}: {w['numberTurns']} turns, {w.get('numberParallels',1)} parallels")
```

---

## 7. Weights (Priorities)

Both `design_magnetics_from_converter()` and `calculate_advised_magnetics()` accept
an optional weights dict. The keys must be **lowercase** MagneticFilters enum values:

```python
weights = {
    "efficiency": 2.0,    # prioritize low losses
    "cost": 1.0,          # consider cost
    "dimensions": 0.5     # size is less important
}
```

Valid weight keys (from `MAS.hpp` `MagneticFilters` `from_json`):
- `"cost"` â€” minimize core/wire cost
- `"dimensions"` â€” minimize physical size
- `"efficiency"` â€” minimize total losses

Pass as the 4th argument to `calculate_advised_magnetics()` or 6th to
`design_magnetics_from_converter()`. Pass `None` for default equal weights.

---

## 8. Settings

Control global behavior with the settings API:

```python
# Get current settings
settings = PyOM.get_settings()

# Modify settings
PyOM.set_settings({
    "useOnlyCoresInStock": True,         # only use cores marked in stock
    "painterNumberPointsX": 100,         # plot X resolution
    "painterNumberPointsY": 100,         # plot Y resolution
    "coilAllowMarginTape": True,         # allow margin tape in coil designs
    "coilAllowInsulatedWire": True,      # allow insulated wire
    "magneticFieldMirroringDimension": 0 # simulation accuracy (0=fast, higher=more accurate)
})

# Reset to defaults
PyOM.reset_settings()
```

---

## 9. Database Access

> âš ï¸ **Naming convention**: single-item lookup functions use the `find_*_by_name()` prefix,
> NOT `get_*_by_name()`. `get_core_shape_by_name()` does **not exist** and will raise `AttributeError`.

### Core Shapes
```python
names    = PyOM.get_core_shape_names(True)        # âœ… verified â€” True=include toroidal
families = PyOM.get_core_shape_families()          # âœ… verified â€” NO argument (bool arg â†’ TypeError)
shape    = PyOM.find_core_shape_by_name("E 25/13/7")  # âœ… verified
```

### Core Materials
```python
mat_names = PyOM.get_core_material_names()         # âœ… verified
material  = PyOM.find_core_material_by_name("3C95")  # âœ… verified (.pyi confirmed)
```

### Wires
```python
wire_names = PyOM.get_wire_names()                 # âœ… verified
wire       = PyOM.find_wire_by_name("Round 0.5 - Grade 1")  # âœ… verified (.pyi confirmed)
```

### Bobbins
```python
bobbin = PyOM.find_bobbin_by_name("E 25/13/7")    # âœ… verified (.pyi confirmed)
```

### âŒ Wrong names â€” do NOT use these
```python
PyOM.get_core_shape_by_name(...)      # AttributeError â€” does not exist
PyOM.get_core_material_by_name(...)   # AttributeError â€” does not exist
PyOM.get_wire_by_name(...)            # AttributeError â€” does not exist
PyOM.get_bobbin_by_name(...)          # AttributeError â€” does not exist
PyOM.get_core_shape_families(True)    # TypeError â€” takes no arguments
```

---

## 10. Post-Design Analysis (All Verified)

### Inductance Calculation
```python
inductance = PyOM.calculate_inductance(magnetic)
# Returns dict with:
#   magnetizingInductance â†’ {magnetizingInductance, coreReluctance, gappingReluctance, ...}
```

### Core Losses
```python
models = {"coreLosses": "IGSE"}  # or "STEINMETZ", "ROSHEN", etc.
losses = PyOM.calculate_core_losses(core, coil, operating_point, models)
```

### Winding Losses
```python
winding_losses = PyOM.calculate_winding_losses(magnetic, operating_point, temperature)
```

### Full Simulation
```python
sim_result = PyOM.simulate(mas)
```

### Wire Utilities
```python
# Skin depth at frequency
delta = PyOM.calculate_effective_skin_depth("copper", 100000, 25)

# DC resistance per meter for a given wire diameter
rdc = PyOM.calculate_dc_resistance_per_meter("copper", 0.5e-3, 25)
```

### SPICE Export
```python
subcircuit = PyOM.export_magnetic_as_subcircuit(magnetic)
# Returns SPICE subcircuit string
```

---

## 11. Supported Topologies

| Topology string | Method A class | Singular/Plural | Notes |
|---|---|---|---|
| `"flyback"` | `Flyback` | PLURAL + **mode required** | Most common |
| `"buck"` | `Buck` | **SINGULAR** | |
| `"boost"` | `Boost` | **SINGULAR** | |
| `"single_switch_forward"` | `SingleSwitchForward` | PLURAL | switchingFreq REQUIRED |
| `"two_switch_forward"` | `TwoSwitchForward` | PLURAL | switchingFreq REQUIRED |
| `"active_clamp_forward"` | `ActiveClampForward` | PLURAL | switchingFreq REQUIRED |
| `"push_pull"` | `PushPull` | PLURAL | Same as Forward |
| `"llc"` | `Llc` | PLURAL | |
| `"isolated_buck"` | `IsolatedBuck` | PLURAL | |
| `"isolated_buck_boost"` | `IsolatedBuckBoost` | PLURAL | |
| Others (`"cllc"`, `"dab"`, `"psfb"`, `"pshb"`) | internal fallback | varies | |

Per-topology thin wrappers for `process_converter`:
`process_flyback()`, `process_buck()`, `process_boost()`,
`process_single_switch_forward()`, `process_two_switch_forward()`,
`process_active_clamp_forward()`, `process_push_pull()`,
`process_isolated_buck()`, `process_isolated_buck_boost()`,
`process_current_transformer(json, turns_ratio, secondary_resistance=0.0)`

---

## 12. Result Structure

Both methods return a list of `[mas_dict, score]` tuples:

```python
d = result[0]                          # First (best) design
mas_obj = d[0]                         # MAS dict
score   = d[1]                         # float â€” higher is better

# Core info
core_fd = mas_obj["magnetic"]["core"]["functionalDescription"]
shape    = core_fd["shape"]            # dict with "name", dimensions, etc.
material = core_fd["material"]         # dict with "name", properties, etc.
gapping  = core_fd["gapping"]          # list of gap dicts

# Coil info
coil_fd = mas_obj["magnetic"]["coil"]["functionalDescription"]
for winding in coil_fd:
    name     = winding["name"]          # "primary", "secondary", etc.
    turns    = winding["numberTurns"]   # int
    parallels = winding.get("numberParallels", 1)
    wire     = winding.get("wire", {})  # wire specification

# Design requirements used
dr = mas_obj["inputs"]["designRequirements"]
mag_ind = dr["magnetizingInductance"]   # {nominal, minimum, maximum}
turns_ratios = dr["turnsRatios"]        # list of ratios

# Operating points used (with full waveforms)
ops = mas_obj["inputs"]["operatingPoints"]
```

---

## 13. Error Handling â€” DO NOT FALL BACK TO MANUAL MODE

| Error | Cause | Fix |
|---|---|---|
| `"Input JSON does not conform to schema!"` (instant) | Used `json.dumps()` on converter or core_mode | Pass Python dict directly â€” NOT `json.dumps(dict)` |
| `"Input JSON does not conform to schema!"` (instant) | Wrong `core_mode_json` | Use `"available cores"` (lowercase + space!) |
| `"Input JSON does not conform to schema!"` (instant) | Missing both `mode` and `currentRippleRatio` | Add either `mode` OR `currentRippleRatio` (mode auto-inferred if ripple set) |
| `"Input JSON does not conform to schema!"` (instant) | Used `desiredInductance` with Method A | Remove it â€” base class doesn't accept it |
| `"ngspice is not available"` | Sandbox restriction | Use Method B with `use_ngspice=False` |
| `"key 'currentRippleRatio' not found"` | Missing required field | Add to JSON |
| `"key 'outputVoltage' not found"` | Used plural for Buck/Boost | Use singular: `outputVoltage`, `outputCurrent` |
| `"key 'outputVoltages' not found"` | Used singular for Flyback/Forward | Use plural: `outputVoltages`, `outputCurrents` |
| `TypeError: incompatible function arguments` | Wrong keyword names | Use positional args |
| Empty namespace (0 functions) | Bare `import PyOpenMagnetics` | Use `importlib` (Section 2) |
| `get_core_shape_names()` TypeError | Missing bool arg | Use `get_core_shape_names(True)` |

---

## 14. Quick-Reference Checklists

### Method A: `design_magnetics_from_converter()`

- [ ] Used `importlib` to load `.so` (NOT bare `import`)
- [ ] Called `load_databases({})` after loading
- [ ] Topology is **lowercase** (`"flyback"`, not `"Flyback"`)
- [ ] `core_mode_json` is `"available cores"` (lowercase + space!)
- [ ] JSON uses **BASE class** schema (NO `desiredInductance`, NO `desiredTurnsRatios`)
- [ ] For Flyback: `currentRippleRatio` present (mode is optional, auto-inferred)
- [ ] For Buck/Boost: `outputVoltage`/`outputCurrent` are **SINGULAR**
- [ ] For Forward: `switchingFrequency` is **REQUIRED** in operatingPoints
- [ ] Using **positional arguments** (keyword names in .pyi are wrong)
- [ ] Passing **Python dicts directly** â€” NOT `json.dumps()` (causes schema error)
- [ ] If error â†’ fix JSON and retry, then Method B â€” NEVER manual calculations

### Method B: `process_converter()` â†’ `calculate_advised_magnetics()`

- [ ] JSON uses **Advanced** schema (WITH `desiredInductance`, `desiredTurnsRatios`)
- [ ] `use_ngspice=False` if ngspice can't init, `True` otherwise
- [ ] Pass `processed["designRequirements"]` + `processed["operatingPoints"]` to adviser
- [ ] Core mode also uses `"available cores"` (same lowercase convention)
- [ ] Weights use lowercase: `"efficiency"`, `"cost"`, `"dimensions"`

---

## 15. Known Issues & Notes

1. **`use_ngspice` is ignored by `design_magnetics_from_converter`** â€” `(void)useNgspice;`
   in source. ngspice is bundled in the wheel. In restricted sandboxes, use Method B.

2. **`.pyi` has wrong keyword names** â€” use positional args or `topology_name=`,
   `converter_json=`, `core_mode_json=`, `weights_json=`.

3. **Two different Flyback classes** â€” `Flyback` (base, Method A) vs
   `AdvancedFlyback` (Method B). Different JSON schemas. Never mix them.

4. **`get_core_shape_names()`** requires boolean arg: `True`=include toroidal.

5. **Design computation is CPU-intensive** â€” `"available cores"` searches 1301+
   shapes (60â€“120+ sec). Use `"standard cores"` for speed.

6. **All enum string values are lowercase** â€” `"available cores"`, `"standard cores"`,
   `"efficiency"`, `"cost"`, `"dimensions"`, etc. The only exception is
   `FlybackModes` which uses Title Case: `"Continuous Conduction Mode"`.

7. **`process_converter` returns two keys** â€” `designRequirements` (with
   `magnetizingInductance`, `turnsRatios`, `name`, `topology`) and
   `operatingPoints` (with full excitation waveforms per winding).

8. **Do NOT `json.dumps()` the arguments** â€” the pybind11 binding accepts Python
   dicts directly. `json.dumps(converter)` turns the dict into a string, which
   the C++ JSON parser rejects with a schema error.

9. **NEVER abandon Method A after a schema error** â€” the error means your JSON
   is wrong, not that the function is broken. Fix the JSON and retry. Do NOT
   fall back to `calculate_advised_cores` or manual textbook formulas.