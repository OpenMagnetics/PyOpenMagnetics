# PyOpenMagnetics Error Reference Guide

This document catalogs common errors encountered when using PyOpenMagnetics, their causes, and solutions.

## Table of Contents

- [Installation Errors](#installation-errors)
- [Import Errors](#import-errors)
- [Schema/Input Errors](#schemainput-errors)
- [Core Errors](#core-errors)
- [Winding Errors](#winding-errors)
- [Simulation Errors](#simulation-errors)
- [Performance Issues](#performance-issues)

---

## Installation Errors

### `ERROR: Failed building wheel for pyopenmagnetics`

**Cause:** Missing C++ compiler or build dependencies.

**Solution (Linux):**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake g++ libopenblas-dev libjpeg-dev libpng-dev libtiff-dev
pip install pyopenmagnetics
```

**Solution (macOS):**
```bash
xcode-select --install
brew install cmake openblas
pip install pyopenmagnetics
```

**Solution (Windows):**
Install Visual Studio Build Tools with C++ support, or use WSL.

### `ImportError: libopenblas.so.0: cannot open shared object file`

**Cause:** OpenBLAS library not installed.

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libopenblas-dev

# Fedora/RHEL
sudo dnf install openblas-devel

# macOS
brew install openblas
```

---

## Import Errors

### `ModuleNotFoundError: No module named 'PyOpenMagnetics'`

**Cause:** Package not installed or wrong Python environment.

**Solution:**
```bash
# Verify installation
pip show pyopenmagnetics

# If not installed
pip install pyopenmagnetics

# Check you're using the correct Python
which python
python -c "import PyOpenMagnetics; print('OK')"
```

### `ImportError: DLL load failed while importing PyOpenMagnetics`

**Cause:** Missing runtime libraries (Windows).

**Solution:**
1. Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Restart your terminal/IDE

---

## Schema/Input Errors

### `KeyError: 'designRequirements'`

**Cause:** Input dictionary missing required fields.

**Solution:**
```python
# Ensure inputs has all required fields
inputs = {
    "designRequirements": {
        "magnetizingInductance": {"nominal": 100e-6},
        "turnsRatios": []  # Empty for single-winding
    },
    "operatingPoints": [
        {
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [...]
        }
    ]
}
```

### `ValueError: Invalid shape name`

**Cause:** Shape name doesn't match database format.

**Solution:**
```python
# Get exact shape names from database
shapes = PyOpenMagnetics.get_core_shape_names()
print(shapes[:10])  # Check format

# Use exact format (case-sensitive, includes spaces)
# WRONG: "ETD39", "etd 39"
# RIGHT: "ETD 39/20/13"
```

### `TypeError: 'NoneType' object is not subscriptable`

**Cause:** Function returned None instead of expected data.

**Solution:**
```python
# Always check return values
result = PyOpenMagnetics.some_function(...)
if result is None:
    print("Operation failed - check inputs")
else:
    process(result)
```

---

## Core Errors

### `RuntimeError: Core shape 'XXX' not found in database`

**Cause:** Shape name not in standard database.

**Solution:**
```python
# List available shapes
shapes = PyOpenMagnetics.get_core_shape_names()
print(f"Found {len(shapes)} shapes")

# Search for similar names
search = "ETD"
matching = [s for s in shapes if search.lower() in s.lower()]
print(matching)
```

### `RuntimeError: Core material 'XXX' not found`

**Cause:** Material not in database.

**Solution:**
```python
# List available materials
materials = PyOpenMagnetics.get_core_material_names()
print(materials)

# Common material mappings:
# Ferroxcube: 3C90, 3C95, 3C97
# TDK/EPCOS: N87, N97, N49
# Magnetics Inc: MPP, High Flux, XFlux
```

### `ValueError: Gap length must be positive`

**Cause:** Invalid gap specification.

**Solution:**
```python
# Correct gap format
gapping = [
    {
        "type": "subtractive",
        "length": 0.001,  # 1mm gap - must be positive
        "area": None,     # Optional - calculated from core
    }
]

# For ungapped core
gapping = []
```

### `Error: Core saturation detected`

**Cause:** Flux density exceeds material saturation limit.

**Solution:**
1. Reduce operating flux density
2. Choose larger core
3. Add air gap to reduce effective permeability
4. Choose higher-saturation material

```python
# Check material saturation flux
material = PyOpenMagnetics.get_core_material("3C95")
b_sat = material.get('saturationFluxDensity', 0.5)
print(f"Saturation: {b_sat} T")
```

---

## Winding Errors

### `RuntimeError: Winding does not fit in bobbin`

**Cause:** Too many turns or wrong wire size for available window.

**Solution:**
```python
# Check window area
bobbin = PyOpenMagnetics.get_default_bobbin(core)
window = bobbin.get('windingWindows', [{}])[0]
print(f"Window area: {window.get('area', 0) * 1e6:.2f} mm²")

# Options:
# 1. Use smaller wire gauge
# 2. Use fewer turns
# 3. Use larger core
# 4. Enable force-fit setting
PyOpenMagnetics.set_settings({"coilWindEvenIfNotFit": True})
```

### `ValueError: Invalid wire specification`

**Cause:** Wire name not found or custom wire incorrectly formatted.

**Solution:**
```python
# Use standard wire names
wires = PyOpenMagnetics.get_wire_names()
print(wires[:20])

# Correct format for round wire
wire = "Round 1.0 - Grade 1"  # 1.0mm conductor diameter

# Correct format for litz wire
wire = "Litz 40x0.1 - Grade 1"  # 40 strands of 0.1mm
```

### `Warning: Skin depth smaller than wire radius`

**Cause:** Wire too thick for operating frequency.

**Solution:**
```python
import math

# Calculate skin depth
rho = 1.68e-8  # Copper resistivity (Ohm-m)
mu_0 = 4 * math.pi * 1e-7
frequency = 100000  # Hz

skin_depth = math.sqrt(rho / (math.pi * frequency * mu_0))
print(f"Skin depth at {frequency/1000} kHz: {skin_depth*1000:.3f} mm")

# Use wire diameter < 2 * skin_depth
# Or use litz wire for high frequency
```

---

## Simulation Errors

### `RuntimeError: No operating points defined`

**Cause:** Empty or missing operating points list.

**Solution:**
```python
# Ensure at least one operating point
inputs = {
    "operatingPoints": [
        {
            "name": "Nominal",
            "conditions": {"ambientTemperature": 40},
            "excitationsPerWinding": [
                {
                    "name": "Primary",
                    "frequency": 100000,
                    "current": {
                        "processed": {
                            "label": "Triangular",
                            "peakToPeak": 2.0,
                            "offset": 10.0,
                            "dutyCycle": 0.5
                        }
                    }
                }
            ]
        }
    ],
    "designRequirements": {...}
}
```

### `ValueError: Inconsistent number of windings`

**Cause:** Mismatch between coil windings and excitations.

**Solution:**
```python
# Number of excitationsPerWinding must match number of coil windings
coil_windings = 2  # e.g., primary + secondary

excitations = [
    {"name": "Primary", "frequency": 100000, ...},
    {"name": "Secondary", "frequency": 100000, ...}
]

assert len(excitations) == coil_windings
```

### `NaN or Inf in simulation results`

**Cause:** Numerical instability, often from extreme parameters.

**Solution:**
```python
# Check for reasonable parameter ranges
# Frequency: 10 Hz - 10 MHz
# Flux density: 0.001 - 1.0 T  
# Temperature: -40 to 200 °C
# Current: > 0 A

# Validate outputs
import math
result = PyOpenMagnetics.calculate_core_losses(...)
if math.isnan(result['coreLosses']) or math.isinf(result['coreLosses']):
    print("Invalid result - check input parameters")
```

---

## Performance Issues

### Slow `get_advised_cores` / `get_advised_magnetics`

**Cause:** Searching entire database with complex constraints.

**Solution:**
```python
# Limit search space
PyOpenMagnetics.set_settings({
    "useOnlyCoresInStock": True,  # Only in-stock cores
    "useToroidalCores": False,    # Exclude toroids
})

# Limit number of results
cores = PyOpenMagnetics.get_advised_cores(
    inputs,
    maximum_number_results=10  # Don't return all matches
)

# Reset settings after
PyOpenMagnetics.reset_settings()
```

### High memory usage

**Cause:** Large waveform data or many iterations.

**Solution:**
```python
# Use processed waveforms instead of raw samples
waveform = {
    "processed": {  # Efficient - just parameters
        "label": "Triangular",
        "peakToPeak": 2.0,
        "dutyCycle": 0.5
    }
}

# Avoid this for large datasets:
waveform = {
    "waveform": {
        "data": [1.0, 1.1, 1.2, ...],  # Thousands of points
        "time": [0, 1e-6, 2e-6, ...]
    }
}
```

### Repeated calculations are slow

**Cause:** Not utilizing caching.

**Solution:**
```python
# Create core once, reuse
core = PyOpenMagnetics.create_core(core_data)

# Reuse for multiple calculations
for freq in frequencies:
    result = PyOpenMagnetics.calculate_core_losses(core, flux, freq, temp)
```

---

## Getting Help

If you encounter an error not listed here:

1. **Check the full traceback** - the last line usually indicates the cause
2. **Validate your inputs** using the validation module:
   ```python
   from api.validation import print_validation_report
   print_validation_report(inputs, "inputs")
   ```
3. **Search GitHub Issues**: https://github.com/OpenMagnetics/PyOpenMagnetics/issues
4. **Create a minimal reproducible example** and open a new issue

## Debug Mode

Enable verbose output for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use PyOpenMagnetics settings
PyOpenMagnetics.set_settings({"verbose": True})
```
