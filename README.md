# PyOpenMagnetics - Python Wrapper for OpenMagnetics

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyOpenMagnetics** is a Python wrapper for [MKF (Magnetics Knowledge Foundation)](https://github.com/OpenMagnetics/MKF), the simulation engine of [OpenMagnetics](https://github.com/OpenMagnetics), providing a comprehensive toolkit for designing and analyzing magnetic components such as transformers and inductors.

## Features

- 🧲 **Core Database**: Access to extensive database of core shapes, materials, and manufacturers
- 🔌 **Winding Design**: Automatic winding calculations with support for various wire types (round, litz, rectangular, planar)
- 📊 **Loss Calculations**: Core losses (Steinmetz), winding losses (DC, skin effect, proximity effect)
- 🎯 **Design Adviser**: Automated recommendations for optimal magnetic designs
- 📈 **Signal Processing**: Harmonic analysis, waveform processing
- 🖼️ **Visualization**: SVG plotting of cores, windings, magnetic fields
- 🔧 **SPICE Export**: Export magnetic components as SPICE subcircuits

## Installation

### From PyPI (recommended)

```bash
pip install PyOpenMagnetics
```

### From Source

```bash
git clone https://github.com/OpenMagnetics/PyOpenMagnetics.git
cd PyOpenMagnetics
pip install .
```

## Quick Start

### Basic Example: Creating a Core

```python
import PyOpenMagnetics

# Find a core shape by name
shape = PyOpenMagnetics.find_core_shape_by_name("E 42/21/15")

# Find a core material by name
material = PyOpenMagnetics.find_core_material_by_name("3C95")

# Create a core with gapping
core_data = {
    "functionalDescription": {
        "shape": shape,
        "material": material,
        "gapping": [{"type": "subtractive", "length": 0.001}],  # 1mm gap
        "numberStacks": 1
    }
}

# Calculate complete core data
core = PyOpenMagnetics.calculate_core_data(core_data, False)
print(f"Effective area: {core['processedDescription']['effectiveParameters']['effectiveArea']} m²")
```

### Design Adviser: Get Magnetic Recommendations

```python
import PyOpenMagnetics

# Define design requirements
inputs = {
    "designRequirements": {
        "magnetizingInductance": {
            "minimum": 100e-6,  # 100 µH minimum
            "nominal": 110e-6   # 110 µH nominal
        },
        "turnsRatios": [{"nominal": 5.0}]  # 5:1 turns ratio
    },
    "operatingPoints": [
        {
            "name": "Nominal",
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {
                    "name": "Primary",
                    "frequency": 100000,  # 100 kHz
                    "current": {
                        "waveform": {
                            "data": [0, 1.0, 0],
                            "time": [0, 5e-6, 10e-6]
                        }
                    },
                    "voltage": {
                        "waveform": {
                            "data": [50, 50, -50, -50],
                            "time": [0, 5e-6, 5e-6, 10e-6]
                        }
                    }
                }
            ]
        }
    ]
}

# Process inputs (adds harmonics and validation)
processed_inputs = PyOpenMagnetics.process_inputs(inputs)

# Get magnetic recommendations
# core_mode: "available cores" (stock cores) or "standard cores" (all standard shapes)
magnetics = PyOpenMagnetics.calculate_advised_magnetics(processed_inputs, 5, "standard cores")

for i, mag in enumerate(magnetics):
    if "magnetic" in mag:
        core = mag["magnetic"]["core"]["functionalDescription"]
        print(f"{i+1}. {core['shape']['name']} - {core['material']['name']}")
```

### Calculate Core Losses

```python
import PyOpenMagnetics

# Define core and operating point
core_data = {...}  # Your core definition
operating_point = {
    "name": "Nominal",
    "conditions": {"ambientTemperature": 25},
    "excitationsPerWinding": [
        {
            "frequency": 100000,
            "magneticFluxDensity": {
                "processed": {
                    "peakToPeak": 0.2,  # 200 mT peak-to-peak
                    "offset": 0
                }
            }
        }
    ]
}

losses = PyOpenMagnetics.calculate_core_losses(core_data, operating_point, "IGSE")
print(f"Core losses: {losses['coreLosses']} W")
```

### Winding a Coil

```python
import PyOpenMagnetics

# Define coil requirements
coil_functional_description = [
    {
        "name": "Primary",
        "numberTurns": 50,
        "numberParallels": 1,
        "wire": "Round 0.5 - Grade 1"
    },
    {
        "name": "Secondary",
        "numberTurns": 10,
        "numberParallels": 3,
        "wire": "Round 1.0 - Grade 1"
    }
]

# Wind the coil on the core
result = PyOpenMagnetics.wind(core_data, coil_functional_description, bobbin_data, [1, 1], [])
print(f"Winding successful: {result.get('windingResult', 'unknown')}")
```

## Flyback Converter Wizard

PyOpenMagnetics includes a complete flyback converter design wizard. See `flyback.py` for a full example:

```python
from flyback import design_flyback, create_mas_inputs, get_advised_magnetics

# Define flyback specifications
specs = {
    "input_voltage_min": 90,
    "input_voltage_max": 375,
    "outputs": [{"voltage": 12, "current": 2, "diode_drop": 0.5}],
    "switching_frequency": 100000,
    "max_duty_cycle": 0.45,
    "efficiency": 0.85,
    "current_ripple_ratio": 0.4,
    "force_dcm": False,
    "safety_margin": 0.85,
    "ambient_temperature": 40,
    "max_drain_source_voltage": None,
}

# Calculate magnetic requirements
design = design_flyback(specs)
print(f"Required inductance: {design['min_inductance']*1e6:.1f} µH")
print(f"Turns ratio: {design['turns_ratios'][0]:.2f}")

# Create inputs for PyOpenMagnetics
inputs = create_mas_inputs(specs, design)

# Get recommended magnetics
magnetics = get_advised_magnetics(inputs, max_results=5)
```

## API Reference

### Database Access

| Function | Description |
|----------|-------------|
| `get_core_materials()` | Get all available core materials |
| `get_core_shapes()` | Get all available core shapes |
| `get_wires()` | Get all available wires |
| `get_bobbins()` | Get all available bobbins |
| `find_core_material_by_name(name)` | Find core material by name |
| `find_core_shape_by_name(name)` | Find core shape by name |
| `find_wire_by_name(name)` | Find wire by name |

### Core Calculations

| Function | Description |
|----------|-------------|
| `calculate_core_data(core, process)` | Calculate complete core data |
| `calculate_core_gapping(core, gapping)` | Calculate gapping configuration |
| `calculate_inductance_from_number_turns_and_gapping(...)` | Calculate inductance |
| `calculate_core_losses(core, operating_point, model)` | Calculate core losses |

### Winding Functions

| Function | Description |
|----------|-------------|
| `wind(core, coil, bobbin, pattern, layers)` | Wind coils on a core |
| `calculate_winding_losses(...)` | Calculate total winding losses |
| `calculate_ohmic_losses(...)` | Calculate DC losses |
| `calculate_skin_effect_losses(...)` | Calculate skin effect losses |
| `calculate_proximity_effect_losses(...)` | Calculate proximity effect losses |

### Design Adviser

| Function | Description |
|----------|-------------|
| `calculate_advised_cores(inputs, max_results)` | Get recommended cores |
| `calculate_advised_magnetics(inputs, max, mode)` | Get complete designs |
| `process_inputs(inputs)` | Process and validate inputs |

### Visualization

| Function | Description |
|----------|-------------|
| `plot_core(core, ...)` | Generate SVG of core |
| `plot_sections(magnetic, ...)` | Plot winding sections |
| `plot_layers(magnetic, ...)` | Plot winding layers |
| `plot_turns(magnetic, ...)` | Plot individual turns |
| `plot_field(magnetic, ...)` | Plot magnetic field |

### Settings

| Function | Description |
|----------|-------------|
| `get_settings()` | Get current settings |
| `set_settings(settings)` | Configure settings |
| `reset_settings()` | Reset to defaults |

### SPICE Export

| Function | Description |
|----------|-------------|
| `export_magnetic_as_subcircuit(magnetic, ...)` | Export as SPICE model |

## Core Materials

PyOpenMagnetics includes materials from major manufacturers:

- **TDK/EPCOS**: N27, N49, N87, N95, N97, etc.
- **Ferroxcube**: 3C90, 3C94, 3C95, 3F3, 3F4, etc.
- **Fair-Rite**: Various ferrite materials
- **Magnetics Inc.**: Powder cores (MPP, High Flux, Kool Mu)
- **Micrometals**: Iron powder cores

## Core Shapes

Supported shape families include:

- **E cores**: E, EI, EFD, EQ, ER
- **ETD/EC cores**: ETD, EC
- **PQ/PM cores**: PQ, PM
- **RM cores**: RM, RM/ILP
- **Toroidal**: Various sizes
- **Pot cores**: P, PT
- **U/UI cores**: U, UI, UR
- **Planar**: E-LP, EQ-LP, etc.

## Wire Types

- **Round enamelled wire**: Various AWG and IEC sizes
- **Litz wire**: Multiple strand configurations
- **Rectangular wire**: For high-current applications
- **Foil**: For planar magnetics
- **Planar PCB**: For integrated designs

## Configuration

Use `set_settings()` to configure:

```python
settings = PyOpenMagnetics.get_settings()
settings["coilAllowMarginTape"] = True
settings["coilWindEvenIfNotFit"] = False
settings["painterNumberPointsX"] = 50
PyOpenMagnetics.set_settings(settings)
```

## Contributing

Contributions are welcome! Please see the [OpenMagnetics](https://github.com/OpenMagnetics) organization for contribution guidelines.

## Documentation

### Quick Start
- **[llms.txt](llms.txt)** - Comprehensive API reference optimized for AI assistants and quick lookup
- **[examples/](examples/)** - Practical example scripts for common design workflows
- **[PyOpenMagnetics.pyi](PyOpenMagnetics.pyi)** - Type stubs for IDE autocompletion

### Tutorials
- **[notebooks/](notebooks/)** - Interactive Jupyter notebook tutorials with visualizations
  - [Getting Started](notebooks/01_getting_started.ipynb) - Introduction to PyOpenMagnetics
  - [Buck Inductor](notebooks/02_buck_inductor.ipynb) - Complete inductor design workflow
  - [Core Losses](notebooks/03_core_losses.ipynb) - In-depth core loss analysis

### Reference
- **[docs/errors.md](docs/errors.md)** - Common errors and solutions
- **[docs/performance.md](docs/performance.md)** - Performance optimization guide
- **[docs/compatibility.md](docs/compatibility.md)** - Python/platform version compatibility

### Validation
- **[api/validation.py](api/validation.py)** - Runtime JSON schema validation for inputs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [MKF](https://github.com/OpenMagnetics/MKF) - C++ magnetics library
- [MAS](https://github.com/OpenMagnetics/MAS) - Magnetic Agnostic Structure schema
- [OpenMagnetics Web](https://openmagnetics.com) - Online design tool

## References

- Maniktala, S. "Switching Power Supplies A-Z", 2nd Edition
- Basso, C. "Switch-Mode Power Supplies", 2nd Edition
- McLyman, C. "Transformer and Inductor Design Handbook"

## Support

For questions and support:
- 🐛 [GitHub Issues](https://github.com/OpenMagnetics/PyOpenMagnetics/issues)
- 💬 [Discussions](https://github.com/OpenMagnetics/PyOpenMagnetics/discussions)
- 📧 Contact the maintainers