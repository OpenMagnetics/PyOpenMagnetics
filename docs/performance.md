# PyOpenMagnetics Performance Guide

This guide documents the computational cost of different PyOpenMagnetics operations and provides strategies for optimization.

## Operation Cost Overview

| Operation | Typical Time | Memory | Notes |
|-----------|-------------|--------|-------|
| `get_core_shape_names()` | ~1 ms | Low | Cached after first call |
| `get_core_material_names()` | ~1 ms | Low | Cached after first call |
| `create_core()` | ~5-20 ms | Low | Single core processing |
| `get_default_bobbin()` | ~2-10 ms | Low | |
| `calculate_core_losses()` | ~1-5 ms | Low | Single point calculation |
| `calculate_winding_losses()` | ~10-100 ms | Medium | Depends on winding complexity |
| `wind_coil_by_turns()` | ~20-100 ms | Medium | Depends on turns count |
| `simulate()` | ~50-500 ms | Medium | Full magnetic simulation |
| `get_advised_cores()` | ~1-30 s | High | Database search, expensive |
| `get_advised_magnetics()` | ~10-120 s | High | Most expensive operation |

## Expensive Operations

### 1. `get_advised_cores()` - Core Adviser

**Why it's expensive:** Searches database of 1000+ cores, calculates losses for each.

**Optimization strategies:**

```python
# ❌ Slow: Search entire database
cores = PyOpenMagnetics.get_advised_cores(inputs)

# ✅ Fast: Limit search space
PyOpenMagnetics.set_settings({
    "useOnlyCoresInStock": True,     # Skip out-of-stock
    "useToroidalCores": False,       # Skip toroids (slower to wind)
})

cores = PyOpenMagnetics.get_advised_cores(
    inputs,
    maximum_number_results=10,        # Stop after finding 10
    weights={                         # Prioritize quick criteria
        "cost": 3.0,
        "efficiency": 2.0,
        "volume": 1.0
    }
)

PyOpenMagnetics.reset_settings()
```

### 2. `get_advised_magnetics()` - Full Magnetic Adviser

**Why it's expensive:** Combines core search + winding optimization for each core.

**Optimization strategies:**

```python
# ❌ Slow: Full optimization
magnetics = PyOpenMagnetics.get_advised_magnetics_from_catalog(inputs)

# ✅ Fast: Two-stage optimization
# Stage 1: Find top cores quickly
cores = PyOpenMagnetics.get_advised_cores(inputs, maximum_number_results=5)

# Stage 2: Optimize winding for top cores only
magnetics = []
for core_result in cores[:3]:
    if 'core' in core_result:
        # Manual winding for selected cores
        coil = PyOpenMagnetics.wind_coil_by_turns(winding_spec, core_result['core'], bobbin)
        magnetics.append({"core": core_result['core'], "coil": coil})
```

### 3. `calculate_winding_losses()` - Winding Loss Analysis

**Why it's expensive:** Requires calculating proximity effects between all turns.

**Optimization strategies:**

```python
# Complexity scales with O(n²) where n = number of turns

# ❌ Slow: High turn count, complex model
losses = PyOpenMagnetics.calculate_winding_losses(
    coil_with_100_turns,
    magnetic_flux,
    operating_point,
    "albach"  # Most accurate but slowest
)

# ✅ Fast: Use simpler model for initial estimates
losses = PyOpenMagnetics.calculate_winding_losses(
    coil_with_100_turns,
    magnetic_flux,
    operating_point,
    "dowell"  # Faster analytical model
)

# ✅ Fast: Reduce turn count with litz wire
# Instead of 100 turns of solid wire, use fewer turns of litz
```

### 4. Parameter Sweeps

**Why they're expensive:** Each point requires a full calculation.

**Optimization strategies:**

```python
# ❌ Slow: Sequential calculations
results = []
for freq in frequencies:
    for temp in temperatures:
        for B in flux_densities:
            result = PyOpenMagnetics.calculate_core_losses(core, B, freq, temp)
            results.append(result)

# ✅ Fast: Minimize recalculation
# Create core once
core = PyOpenMagnetics.create_core(core_data)

# Use list comprehension (still sequential but cleaner)
results = [
    PyOpenMagnetics.calculate_core_losses(core, {"processed": {"peakToPeak": B*2}}, freq, temp)
    for freq in frequencies
    for temp in temperatures  
    for B in flux_densities
]

# ✅ Faster: Parallel processing (for independent calculations)
from concurrent.futures import ThreadPoolExecutor

def calc_loss(params):
    freq, temp, B = params
    return PyOpenMagnetics.calculate_core_losses(
        core, 
        {"processed": {"peakToPeak": B*2}}, 
        freq, 
        temp
    )

param_combinations = [(f, t, b) for f in frequencies for t in temperatures for b in flux_densities]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(calc_loss, param_combinations))
```

## Memory Optimization

### Waveform Data

```python
# ❌ Memory-heavy: Raw waveform data
waveform = {
    "waveform": {
        "data": list(range(10000)),  # 10k samples
        "time": [i * 1e-9 for i in range(10000)]
    }
}

# ✅ Memory-efficient: Processed parameters
waveform = {
    "processed": {
        "label": "Triangular",
        "peakToPeak": 0.3,
        "offset": 0,
        "dutyCycle": 0.5
    }
}
```

### Batch Processing

```python
# ❌ Memory-heavy: Store all results
all_results = []
for i in range(10000):
    result = PyOpenMagnetics.calculate_core_losses(...)
    all_results.append(result)  # Keeps growing

# ✅ Memory-efficient: Process and discard
def process_result(result):
    return result['coreLosses']  # Keep only what you need

total_loss = 0
for i in range(10000):
    result = PyOpenMagnetics.calculate_core_losses(...)
    total_loss += process_result(result)
    # result is garbage collected

average_loss = total_loss / 10000
```

## Caching Strategies

### Database Lookups

```python
# Database data is cached internally after first access
# First call: ~100ms (loads from disk)
shapes = PyOpenMagnetics.get_core_shape_names()

# Subsequent calls: ~1ms (from cache)
shapes = PyOpenMagnetics.get_core_shape_names()
```

### Reusable Objects

```python
# ❌ Slow: Recreate core for each calculation
for temp in temperatures:
    core = PyOpenMagnetics.create_core(core_data)  # Repeated work
    losses = PyOpenMagnetics.calculate_core_losses(core, flux, freq, temp)

# ✅ Fast: Create once, reuse
core = PyOpenMagnetics.create_core(core_data)  # Once
for temp in temperatures:
    losses = PyOpenMagnetics.calculate_core_losses(core, flux, freq, temp)
```

### Application-Level Caching

```python
import functools
import json

@functools.lru_cache(maxsize=1000)
def cached_core_losses(core_json: str, flux_json: str, freq: float, temp: float):
    """Cache core loss calculations."""
    core = json.loads(core_json)
    flux = json.loads(flux_json)
    return PyOpenMagnetics.calculate_core_losses(core, flux, freq, temp)

# Usage
core_json = json.dumps(core)
flux_json = json.dumps(magnetic_flux_density)

# First call: computes
result1 = cached_core_losses(core_json, flux_json, 100000, 80)

# Second call with same params: returns cached
result2 = cached_core_losses(core_json, flux_json, 100000, 80)
```

## Profiling Your Code

```python
import time

def profile_operation(name: str, func, *args, **kwargs):
    """Simple profiler for PyOpenMagnetics operations."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed*1000:.2f} ms")
    return result

# Usage
core = profile_operation(
    "create_core",
    PyOpenMagnetics.create_core,
    core_data
)

losses = profile_operation(
    "calculate_core_losses",
    PyOpenMagnetics.calculate_core_losses,
    core, flux, frequency, temperature
)
```

## Settings That Affect Performance

```python
# View current settings
settings = PyOpenMagnetics.get_settings()

# Performance-related settings
PyOpenMagnetics.set_settings({
    # Database filtering (reduces search space)
    "useOnlyCoresInStock": True,      # Skip out-of-stock cores
    "useToroidalCores": False,        # Skip toroids
    "useOnlyManufacturerRecommendedGaps": True,  # Standard gaps only
    
    # Calculation accuracy vs speed
    "coilAllowMarginTape": False,     # Simpler winding model
    "coilAllowInsulatedWire": True,   # Use standard wire
})

# Always reset after optimization runs
PyOpenMagnetics.reset_settings()
```

## Quick Reference: Speed Tips

1. **Limit search results** - Use `maximum_number_results` parameter
2. **Filter database** - Enable `useOnlyCoresInStock`, disable `useToroidalCores`
3. **Create objects once** - Reuse `core`, `bobbin`, `coil` objects
4. **Use processed waveforms** - Avoid raw sample data
5. **Choose appropriate models** - Use `dowell` vs `albach` based on accuracy needs
6. **Batch similar operations** - Group calculations with same core
7. **Profile first** - Identify actual bottlenecks before optimizing
