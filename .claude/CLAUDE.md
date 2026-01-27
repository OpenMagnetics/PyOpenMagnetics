# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PyOpenMagnetics** is a Python library for magnetic component design - transformers, inductors, and chokes for power electronics. It wraps the OpenMagnetics MKF C++ engine and provides multiple interfaces:

- **Fluent Design API** - `Design.flyback().vin_ac(85, 265).output(12, 5).solve()`
- **Low-level C++ Bindings** - Direct access to MKF engine via `PyOpenMagnetics` module
- **MCP Server** - AI assistant integration for natural language design
- **Streamlit GUI** - Visual interface for hardware engineers

## Quick Start

```python
# Fluent API (recommended for new designs)
from api.design import Design

result = Design.flyback() \
    .vin_ac(85, 265) \
    .output(12, 5) \
    .fsw(100e3) \
    .solve(verbose=True)

print(f"Best design: {result[0].core} with {result[0].material}")
print(f"Total loss: {result[0].total_loss_w:.2f} W")
```

```python
# Low-level API (for advanced use cases)
import PyOpenMagnetics

# Get core recommendations
inputs = {"designRequirements": {...}, "operatingPoints": [...]}
processed = PyOpenMagnetics.process_inputs(inputs)
magnetics = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
```

## Architecture

```
User Interfaces
├── api/design.py        Fluent Design API (Design.flyback(), Design.buck(), etc.)
├── api/mcp/             MCP Server for AI assistants
└── api/gui/             Streamlit GUI (run: streamlit run api/gui/app.py)
        │
        ▼
PyOpenMagnetics Module
├── Database Access      get_core_materials(), find_core_shape_by_name(), get_wires()
├── Core Calculations    calculate_core_data(), calculate_inductance_from_number_turns_and_gapping()
├── Loss Models          calculate_core_losses() [STEINMETZ, IGSE, MSE, BARG, ROSHEN, ALBACH]
├── Winding Engine       wind(), wind_by_sections(), wind_by_layers()
├── Design Adviser       process_inputs(), calculate_advised_cores(), calculate_advised_magnetics()
├── Simulation           simulate(), magnetic_autocomplete()
└── Visualization        plot_core(), plot_coil_2d(), plot_field_2d()
        │
        ▼
MKF C++ Engine (via pybind11)
        │
        ▼
MAS JSON Schema (Magnetic Agnostic Structure)
```

## Build Commands

```bash
# Install from source (builds C++ extension via pybind11)
pip install .

# Build wheel
python -m build

# Cross-platform wheel building
python -m cibuildwheel --output-dir wheelhouse
```

**Build requirements**: CMake 3.15+, C++23 compiler, Node.js 18+, quicktype (for schema generation)

## Testing

```bash
# Run all tests
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_core.py -v

# Run all examples (17 examples across 5 categories)
./scripts/run_examples.sh

# Quick validation
./scripts/pre_commit_check.sh
```

**Test modules**: `test_core.py`, `test_core_adviser.py`, `test_magnetic_adviser.py`, `test_winding.py`, `test_inputs.py`, `test_examples_integration.py`

## Source Structure

```
PyMKF/
├── api/
│   ├── design.py           # Fluent Design API (main entry point)
│   ├── MAS.py              # Auto-generated dataclasses from MAS schema
│   ├── validation.py       # JSON schema validation utilities
│   ├── mcp/                # MCP Server for AI assistants
│   │   ├── server.py       # MCP server entry point
│   │   └── tools.py        # design_magnetic, query_database tools
│   ├── gui/                # Streamlit GUI
│   │   └── app.py          # GUI entry point
│   ├── expert/             # Magnetic Expert knowledge base
│   │   └── knowledge.py    # Application templates, trade-offs
│   ├── bridges/            # External tool integration
│   │   └── femmt.py        # FEMMT FEM simulation export
│   └── architect/          # Code analysis tools
│
├── examples/               # 17 working examples (all passing)
│   ├── consumer/           # USB PD chargers, laptop adapters
│   ├── automotive/         # 48V DC-DC, gate drivers
│   ├── industrial/         # DIN rail PSU, medical, VFD chokes
│   ├── telecom/            # PoE, rectifiers
│   └── advanced/           # Custom simulation, NSGA2 optimization
│
├── src/                    # C++ pybind11 bindings
│   ├── module.cpp          # Main binding definitions
│   ├── database.cpp        # Core/material/wire database
│   ├── advisers.cpp        # Design recommendation algorithms
│   ├── core.cpp            # Core geometry calculations
│   ├── winding.cpp         # Winding placement engine
│   ├── losses.cpp          # Core and winding loss models
│   ├── simulation.cpp      # Full electromagnetic simulation
│   └── plotting.cpp        # SVG visualization
│
├── tests/                  # pytest test suite
├── scripts/                # Utility scripts
│   ├── run_examples.sh     # Run all examples
│   ├── pre_commit_check.sh # Pre-commit validation
│   └── block_push.sh       # Block pushes to origin (FREE/PRO split)
│
├── llms.txt                # Comprehensive API reference for AI assistants
├── PyOpenMagnetics.pyi     # Type stubs for IDE autocompletion
└── CLAUDE.md               # This file
```

## Key Concepts

### MAS Schema (Magnetic Agnostic Structure)
Standardized JSON structures for magnetic components:
- **Inputs**: Design requirements + operating points
- **Magnetic**: Core + Coil assembly
- **Outputs**: Simulation results (losses, temperature, inductance)
- **Mas**: Complete specification (Inputs + Magnetic + Outputs)

### Data Flow
```
User specs → Design API → MAS JSON → C++ Engine → MAS JSON → DesignResult objects
```

### Supported Topologies
| Topology | Method | Use Case |
|----------|--------|----------|
| Flyback | `Design.flyback()` | Isolated SMPS <150W |
| Buck | `Design.buck()` | Non-isolated step-down |
| Boost | `Design.boost()` | Non-isolated step-up, PFC |
| Forward | `process_single_switch_forward()` | Isolated, higher power |
| LLC | `Design.llc()` | High efficiency, resonant |
| Push-Pull | `process_push_pull()` | Low voltage input |
| Inductor | `Design.inductor()` | Standalone inductors |

### Core Materials
| Manufacturer | Materials |
|--------------|-----------|
| TDK/EPCOS | N27, N49, N87, N95, N97, PC40, PC95 |
| Ferroxcube | 3C90, 3C94, 3C95, 3C96, 3F3, 3F4, 3F35 |
| Fair-Rite | 67, 77, 78 |
| Magnetics Inc | MPP, High Flux, Kool Mu, XFlux |
| Micrometals | Iron powder: -2, -8, -18, -26, -52 |

### Core Shape Families
E, EI, EFD, EQ, ER, ETD, EC, PQ, PM, RM, T (toroidal), P, PT, U, UI, LP (planar)

## Working with the API

### Always Process Inputs First
```python
# REQUIRED before adviser functions - adds harmonics data
processed = PyOpenMagnetics.process_inputs(inputs)
magnetics = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
```

### Handle Return Values
Functions return dicts or JSON strings. Parse correctly:
```python
result = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")

# Result may be dict with "data" key or JSON string
if isinstance(result, str):
    magnetics = json.loads(result)
elif isinstance(result, dict):
    data = result.get("data", result)
    if isinstance(data, str):
        magnetics = json.loads(data)
    else:
        magnetics = data if isinstance(data, list) else [data]
```

### Check for Errors
```python
result = PyOpenMagnetics.calculate_core_data(data, False)
if isinstance(result, str) and result.startswith("Exception:"):
    print(f"Error: {result}")
```

## Examples Structure

All 17 examples follow the pattern:
```python
"""
{Application Name} - {Topology} Design

Application: {Real-world description}
Real-world equivalents: {Actual products}

Specifications:
- Input: {voltage range}
- Output: {voltage} @ {current} ({power})
- Frequency: {switching frequency}
"""

from api.design import Design

def design_{name}():
    design = (Design.flyback()
        .vin_ac(85, 265)
        .output(12, 5)
        .fsw(100e3)
        .efficiency(0.88)
        .max_height(20)
        .prefer("efficiency"))

    results = design.solve(max_results=5, verbose=True,
                          output_dir="examples/_output/{name}")
    return results

if __name__ == "__main__":
    best = design_{name}()
```

## Common Tasks

### Design a Flyback Transformer
```python
from api.design import Design

design = Design.flyback() \
    .vin_ac(85, 265) \         # Universal AC input
    .output(12, 5) \           # 12V @ 5A = 60W
    .fsw(100e3) \              # 100 kHz switching
    .efficiency(0.88) \        # Target efficiency
    .max_height(25) \          # Size constraint
    .prefer("efficiency")      # Optimization priority

results = design.solve(max_results=MAX_RESULTS, verbose=True)
```

### Design a Buck Inductor
```python
design = Design.buck() \
    .vin(10, 14) \             # 12V +/- tolerance
    .vout(3.3) \               # Output voltage
    .iout(10) \                # Output current
    .fsw(500e3) \              # Switching frequency
    .ripple(0.3)               # 30% current ripple

results = design.solve()
```

### Query Database
```python
import PyOpenMagnetics

# Materials
materials = PyOpenMagnetics.get_core_material_names()
material = PyOpenMagnetics.find_core_material_by_name("3C95")
steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 100000)

# Shapes
shapes = PyOpenMagnetics.get_core_shape_names()
shape = PyOpenMagnetics.find_core_shape_by_name("E 42/21/15")

# Wires
wires = PyOpenMagnetics.get_wire_names()
wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
```

### Calculate Losses
```python
models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}

# Core losses
losses = PyOpenMagnetics.calculate_core_losses(core, coil, inputs, models)
print(f"Core loss: {losses['coreLosses']:.3f} W")
print(f"B_peak: {losses['magneticFluxDensityPeak']*1000:.1f} mT")

# Winding losses
winding_losses = PyOpenMagnetics.calculate_winding_losses(magnetic, operating_point, 85)
print(f"Winding loss: {winding_losses['windingLosses']:.3f} W")
```

## CI/CD

- Tests run on Ubuntu 22.04, Windows 2022, macOS 14 with Python 3.10-3.12
- Builds require Node.js 18+ and quicktype for schema code generation
- Uses `manylinux_2_28` images with gcc-toolset-13 for C++23 support on Linux

## Type Information

- **PyOpenMagnetics.pyi** - Type stubs for IDE autocompletion
- **llms.txt** - Comprehensive API reference with examples (for AI assistants)
- **api/MAS.py** - Auto-generated dataclass definitions from MAS schema
- **api/validation.py** - JSON schema validation utilities

## Git Safety

**IMPORTANT**: Push to origin is blocked due to FREE/PRO version split.
- Pre-push hook installed in `.git/hooks/pre-push`
- All pushes to `origin` remote are blocked
- Use different remote for development

## Related Documentation

- **llms.txt** - Full API reference with all function signatures and examples
- **skills.md** - Development roadmap and skill implementation status
- **examples/README.md** - Examples overview and categories
