# PyOpenMagnetics Version Compatibility

This document describes version compatibility between PyOpenMagnetics, the MKF C++ engine, and Python.

## Current Version

| Component | Version | Release Date |
|-----------|---------|--------------|
| PyOpenMagnetics | 1.0.2 | January 2026 |
| MKF Engine | Latest | Fetched at build time |
| MAS Schema | Latest | Semantic versioning |

## Python Compatibility

| Python Version | PyOpenMagnetics Support | Notes |
|----------------|------------------------|-------|
| 3.8 | ❌ Not supported | EOL |
| 3.9 | ⚠️ Limited | May work, not tested |
| 3.10 | ✅ Supported | Tested |
| 3.11 | ✅ Supported | Tested |
| 3.12 | ✅ Supported | Primary development |
| 3.13 | ⚠️ Experimental | Not yet released |

## Platform Support

| Platform | Architecture | Status | Notes |
|----------|--------------|--------|-------|
| Linux (glibc 2.28+) | x86_64 | ✅ Full support | Primary platform |
| Linux (glibc 2.28+) | aarch64 | ⚠️ Experimental | Arm64 |
| macOS 12+ | x86_64 | ✅ Supported | Intel Macs |
| macOS 12+ | arm64 | ✅ Supported | Apple Silicon |
| Windows 10+ | x86_64 | ⚠️ Via WSL2 | Native not recommended |

## Build Dependencies

### Required (All Platforms)

| Dependency | Minimum Version | Purpose |
|------------|-----------------|---------|
| CMake | 3.20 | Build system |
| C++ Compiler | C++23 support | Compilation |
| Python dev headers | Match Python version | Binding generation |

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install \
    build-essential \
    cmake \
    g++ \
    libopenblas-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    python3-dev
```

### macOS

```bash
xcode-select --install
```

## MKF Engine Version

PyOpenMagnetics fetches the MKF engine at build time from:
- **Repository:** https://github.com/OpenMagnetics/MKF
- **Branch:** main (latest)

The MKF version is determined by the git commit at build time.

### Checking Versions

```python
import PyOpenMagnetics

# Get library info (if available)
try:
    info = PyOpenMagnetics.get_version_info()
    print(f"PyOpenMagnetics version: {info.get('version', 'N/A')}")
    print(f"MKF commit: {info.get('mkf_commit', 'N/A')}")
except AttributeError:
    print("Version info not available in this build")
```


## API Stability

### Stable APIs (Will Not Change)

```python
# Core creation and queries
PyOpenMagnetics.create_core(core_data)
PyOpenMagnetics.get_core_shape_names()
PyOpenMagnetics.get_core_material_names()

# Loss calculations
PyOpenMagnetics.calculate_core_losses(core, flux, frequency, temperature)
PyOpenMagnetics.calculate_winding_losses(coil, flux, operating_point)

# Settings
PyOpenMagnetics.get_settings()
PyOpenMagnetics.set_settings(settings)
PyOpenMagnetics.reset_settings()

# Advisers
PyOpenMagnetics.get_advised_cores(inputs, **options)
```

### Experimental APIs (May Change)

```python
# Plotting (depends on gnuplot availability)
PyOpenMagnetics.plot_magnetic(magnetic, path)

# Advanced simulation
PyOpenMagnetics.simulate(inputs, magnetic, models)

# Autocomplete features
PyOpenMagnetics.mas_autocomplete(partial_mas, config)
```

## Deprecation Policy

1. **Deprecation notice** - Added in version N
2. **Warning period** - Versions N, N+1 emit warnings
3. **Removal** - Version N+2 removes the API

### Currently Deprecated

None at this time.

## Upgrading

### From 0.9.x to 1.0.x

```python
# Settings API changed from pointer to reference (internal)
# No user-facing API changes

# Verify installation
import PyOpenMagnetics
print("Upgrade successful!")
```

### Wheel Availability

Pre-built wheels are provided for common platforms:

| Platform | Python Versions | Wheel Format |
|----------|----------------|--------------|
| manylinux_2_28 x86_64 | 3.10, 3.11, 3.12 | `.whl` |
| macosx_12_0 x86_64 | 3.10, 3.11, 3.12 | `.whl` |
| macosx_12_0 arm64 | 3.10, 3.11, 3.12 | `.whl` |

If no wheel is available for your platform, pip will attempt to build from source.

## Checking Your Environment

```python
#!/usr/bin/env python3
"""Check PyOpenMagnetics environment compatibility."""

import sys
import platform

print("=== Environment Check ===\n")

# Python version
py_version = sys.version_info
print(f"Python: {py_version.major}.{py_version.minor}.{py_version.micro}")
if py_version < (3, 10):
    print("  ⚠️ Python 3.10+ recommended")
elif py_version >= (3, 10):
    print("  ✅ Python version OK")

# Platform
print(f"Platform: {platform.system()} {platform.machine()}")

# Try import
try:
    import PyOpenMagnetics
    print("\n✅ PyOpenMagnetics imported successfully!")
    
    # Test basic operation
    shapes = PyOpenMagnetics.get_core_shape_names(include_toroidal=False)
    print(f"   Database loaded: {len(shapes)} shapes available")
    
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
except Exception as e:
    print(f"\n⚠️ Import OK but error during test: {e}")
```

## Reporting Compatibility Issues

When reporting issues, please include:

1. **Python version:** `python --version`
2. **Platform:** `python -c "import platform; print(platform.platform())"`
3. **PyOpenMagnetics version:** `pip show pyopenmagnetics`
4. **Installation method:** pip, source build, conda
5. **Error message:** Full traceback

File issues at: https://github.com/OpenMagnetics/PyOpenMagnetics/issues
