# PyOpenMagnetics

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

**PyOpenMagnetics** is a Python wrapper for [MKF (Magnetics Knowledge Foundation)](https://github.com/OpenMagnetics/MKF), providing a comprehensive toolkit for designing magnetic components (transformers, inductors, chokes) for power electronics.

## Why PyOpenMagnetics?

| Traditional Approach | PyOpenMagnetics |
|---------------------|-----------------|
| 50+ lines of JSON configuration | `Design.flyback().vin_ac(85,265).output(12,5).solve()` |
| Manual waveform calculations | Automatic waveform synthesis |
| Trial-and-error core selection | AI-powered recommendations |
| Separate tools for each topology | Unified API for all converters |

## Features

### Core Engine
- **Database Access**: 500+ core shapes, 100+ materials, extensive wire library
- **Loss Models**: Steinmetz, IGSE, MSE, BARG, ROSHEN, ALBACH for core losses
- **Winding Analysis**: DC, skin effect, proximity effect losses
- **Design Adviser**: Automated optimal magnetic design recommendations
- **Visualization**: SVG plotting of cores, windings, magnetic fields

### Fluent Design API (NEW)
```python
from api.design import Design

# Design a 65W USB-C charger transformer
results = (Design.flyback()
    .vin_ac(85, 265)           # Universal AC input
    .output(20, 3.25)          # 20V @ 3.25A
    .fsw(100e3)                # 100kHz switching
    .prefer("efficiency")
    .solve())

print(f"Best: {results[0].core} + {results[0].material}")
print(f"Turns: {results[0].primary_turns}T / {results[0].secondary_turns}T")
print(f"Losses: {results[0].total_loss_w:.2f}W")
```

### Supported Topologies
| Isolated | Non-Isolated | Magnetics |
|----------|--------------|-----------|
| Flyback | Buck | Inductor |
| Forward | Boost | CM Choke |
| LLC | Buck-Boost | Current Transformer |
| DAB/CLLC | SEPIC | Gate Drive Transformer |

### Multi-Objective Optimization (NEW)
```python
from api.optimization import NSGAOptimizer

optimizer = NSGAOptimizer(
    objectives=["mass", "total_loss"],
    constraints={"inductance": (100e-6, 140e-6)}
)
optimizer.add_variable("turns", range=(20, 60))
optimizer.add_variable("core_size", range=(0.5, 2.0))

pareto_front = optimizer.run(generations=50)
# Returns Pareto-optimal designs trading off mass vs efficiency
```

### Expert Knowledge Base (NEW)
```python
from api.expert.knowledge import suggest_powder_core_material, POWDER_CORE_MATERIALS

# Get material recommendations for high DC bias application
suggestions = suggest_powder_core_material(
    dc_bias_amps=50,
    frequency_hz=100e3,
    priority="high_bias"  # or "low_loss", "cost", "balanced"
)
# Returns: ['CSC_Mega_Flux_60u', 'CSC_High_Flux_60u', ...]
```

## Installation

### From PyPI
```bash
pip install PyOpenMagnetics
```

### From Source
```bash
git clone https://github.com/OpenMagnetics/PyMKF.git
cd PyMKF
pip install .
```

### Development Install
```bash
pip install -e ".[dev]"
```

**Build Requirements**: CMake 3.15+, C++23 compiler, Node.js 18+

## Quick Start

### 1. Simple Inductor Design
```python
from api.design import Design

# 100µH inductor for buck converter
design = Design.buck().vin(12, 24).vout(5).iout(3).fsw(500e3)
results = design.solve()

for r in results[:3]:
    print(f"{r.core}: {r.primary_turns}T, {r.total_loss_w:.2f}W loss")
```

### 2. Flyback Transformer
```python
# Multi-output flyback for USB charger
design = (Design.flyback()
    .vin_ac(85, 265)
    .output(12, 2)      # 12V @ 2A
    .output(5, 0.5)     # 5V @ 0.5A (auxiliary)
    .fsw(100e3)
    .isolation("reinforced")
    .solve())
```

### 3. Boost Inductor for EV Charger
```python
# 10kW boost stage
design = (Design.boost()
    .vin(200, 450)
    .vout(800)
    .pout(10000)
    .fsw(100e3)
    .ambient_temperature(70)
    .solve())
```

### 4. Using the Low-Level API
```python
import PyOpenMagnetics

# Direct MAS JSON usage for advanced users
inputs = {
    "designRequirements": {
        "magnetizingInductance": {"nominal": 100e-6}
    },
    "operatingPoints": [...]
}

processed = PyOpenMagnetics.process_inputs(inputs)
results = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "standard cores")
```

## Project Structure

```
PyMKF/
├── api/                      # Python API layer
│   ├── design.py             # Fluent Design API
│   ├── mas.py                # MAS waveform generators
│   ├── optimization.py       # NSGA-II optimizer
│   ├── results.py            # Result formatting
│   ├── expert/               # Domain knowledge
│   │   ├── knowledge.py      # Materials, applications, tradeoffs
│   │   ├── examples.py       # Example generator
│   │   └── conversation.py   # Interactive design guide
│   ├── mcp/                  # MCP server for AI assistants
│   ├── gui/                  # Streamlit GUI
│   ├── bridges/              # External tool bridges
│   │   └── femmt.py          # FEMMT FEM export
│   └── architect/            # Code analysis tools
├── examples/                 # Real-world design examples
│   ├── consumer/             # USB chargers, laptops
│   ├── automotive/           # EV, 48V systems
│   ├── industrial/           # DIN rail, medical, VFD
│   ├── telecom/              # PoE, rectifiers
│   └── advanced/             # Optimization, custom simulation
├── src/                      # C++ pybind11 bindings
├── tests/                    # Pytest test suite
└── archive/                  # Legacy code reference
```

## Examples

Run individual examples:
```bash
python examples/consumer/usb_pd_65w.py
python examples/automotive/boost_half_bridge_multi_op.py
python examples/industrial/boost_inductor_design.py
python examples/advanced/nsga2_inductor_optimization.py
```

Run all examples:
```bash
./scripts/run_examples.sh
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_design_builder.py -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html
```

Pre-commit validation:
```bash
./scripts/pre_commit_check.sh
```

## Documentation

| Resource | Description |
|----------|-------------|
| [llms.txt](llms.txt) | Comprehensive API reference (AI-friendly) |
| [CLAUDE.md](CLAUDE.md) | Development guide for Claude Code |
| [PRD.md](PRD.md) | Product Requirements Document |
| [docs/](docs/) | Detailed documentation |
| [notebooks/](notebooks/) | Interactive tutorials |

## API Reference

### Design Builder

| Method | Description |
|--------|-------------|
| `Design.flyback()` | Flyback transformer builder |
| `Design.buck()` | Buck converter inductor builder |
| `Design.boost()` | Boost converter inductor builder |
| `Design.forward()` | Forward transformer builder |
| `Design.llc()` | LLC resonant transformer builder |
| `Design.inductor()` | Standalone inductor builder |

### Builder Methods

| Method | Description |
|--------|-------------|
| `.vin(min, max)` | Set DC input voltage range |
| `.vin_ac(min, max)` | Set AC input voltage range |
| `.vout(voltage)` | Set output voltage |
| `.output(voltage, current)` | Add output (transformers) |
| `.fsw(frequency)` | Set switching frequency |
| `.prefer(priority)` | Set optimization priority |
| `.solve(max_results)` | Run design optimization |

### Expert Knowledge

| Function | Description |
|----------|-------------|
| `suggest_powder_core_material()` | Get material recommendations |
| `calculate_core_loss()` | Steinmetz loss calculation |
| `get_application_info()` | Application-specific guidance |
| `suggest_topology()` | Topology recommendation |

### Optimization

| Class/Function | Description |
|----------------|-------------|
| `NSGAOptimizer` | Multi-objective NSGA-II optimizer |
| `create_inductor_optimizer()` | Pre-configured inductor optimizer |
| `ParetoFront` | Collection of optimal solutions |

## Core Materials Database

### Ferrite
- TDK/EPCOS: N27, N49, N87, N95, N97
- Ferroxcube: 3C90, 3C94, 3C95, 3C97, 3F3, 3F4

### Powder Cores (NEW - 25+ materials)
- **MPP**: 26µ, 60µ, 125µ, 147µ, 160µ, 173µ, 200µ
- **High Flux**: 26µ, 60µ, 125µ, 147µ, 160µ
- **Sendust/Kool Mu**: 26µ, 60µ, 75µ, 90µ, 125µ
- **Mega Flux/XFlux**: 26µ, 50µ, 60µ, 75µ, 90µ

### Nanocrystalline & Amorphous
- Vitroperm, Finemet equivalents
- Metglas amorphous alloys

## Version Tiers

| Feature | FREE | PRO |
|---------|------|-----|
| Basic topologies (buck, boost, flyback) | ✅ | ✅ |
| Design adviser | ✅ | ✅ |
| Core/material database | ✅ | ✅ |
| Multi-objective optimization | ❌ | ✅ |
| MCP server for AI | ❌ | ✅ |
| Streamlit GUI | ❌ | ✅ |
| FEMMT bridge | ❌ | ✅ |
| Expert knowledge base | ❌ | ✅ |
| Advanced topologies (LLC, DAB) | ❌ | ✅ |
| Priority support | ❌ | ✅ |

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/OpenMagnetics/PyMKF.git
cd PyMKF
pip install -e ".[dev]"
pre-commit install

# Run tests before submitting PR
./scripts/pre_commit_check.sh
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [MKF](https://github.com/OpenMagnetics/MKF) - C++ magnetics engine
- [MAS](https://github.com/OpenMagnetics/MAS) - Magnetic Agnostic Structure schema
- [OpenMagnetics Web](https://openmagnetics.com) - Online design tool
- [FEMMT](https://github.com/upb-lea/FEM_Magnetics_Toolbox) - FEM simulation

## Citation

If you use PyOpenMagnetics in research, please cite:
```bibtex
@software{pyopenmagnetics,
  title = {PyOpenMagnetics: Python Toolkit for Magnetic Component Design},
  url = {https://github.com/OpenMagnetics/PyMKF},
  year = {2024}
}
```

## Support

- [GitHub Issues](https://github.com/OpenMagnetics/PyMKF/issues)
- [Discussions](https://github.com/OpenMagnetics/PyMKF/discussions)
- Email: support@openmagnetics.com
