# PyOpenMagnetics Development Skills & Implementation Status

## Implementation Progress

| Skill | Status | Location |
|-------|--------|----------|
| 1. Design Builder (Fluent API) | ✅ Complete | `api/design.py` |
| 2. MCP Server for AI | ✅ Complete | `api/mcp/` |
| 3. Streamlit GUI | ✅ Complete | `api/gui/` |
| 4. Example Library | ✅ Complete | `examples/` |
| 5. FEMMT Bridge | ✅ Complete | `api/bridges/femmt.py` |
| 6. SW Architect Tools | ✅ Complete | `api/architect/` |
| 7. Magnetic Expert Knowledge | ✅ Complete | `api/expert/knowledge.py` |
| 8. Legacy Migration (Sprint 8) | ✅ Complete | `examples/advanced/` |

---

## Core Problem: MAS Format Abstraction

PyOpenMagnetics is built on MAS (Magnetic Agnostic Structure) - a comprehensive JSON schema that is **machine-friendly but human-hostile**:

```json
// What MAS wants (verbose, nested, explicit)
{
  "designRequirements": {
    "magnetizingInductance": {"nominal": 100e-6, "minimum": 90e-6},
    "turnsRatios": [{"nominal": 4.0}]
  },
  "operatingPoints": [{
    "conditions": {"ambientTemperature": 25},
    "excitationsPerWinding": [{
      "frequency": 100000,
      "current": {"waveform": {"data": [...], "time": [...]}}
    }]
  }]
}
```

```python
# What HW engineers want to write
Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3).solve()
```

**The abstraction layer must**:
- Accept familiar parameters (Vin, Vout, Iout, fsw, topology)
- Generate valid MAS internally
- Return results in practical terms (BOM, winding instructions, warnings)
- Hide JSON complexity unless user wants to inspect/modify

---

## Architecture: Abstraction Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ CLI/REPL │  │ GUI App  │  │ MCP/AI   │  │ Jupyter Widgets  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
├───────┴─────────────┴─────────────┴─────────────────┴───────────┤
│                  TOPOLOGY ABSTRACTIONS                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Flyback  │  Buck  │  Boost  │  LLC  │  DAB  │  Forward  │  ││
│  │  ───────────────────────────────────────────────────────── ││
│  │  Inductor │ Transformer │ CM Choke │ Current Sense │ Gate  ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                  DESIGN BUILDER (api/design.py)                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  • Fluent API:  Design.buck().vin(48).vout(12).iout(20)    ││
│  │  • Multi-output: .output(12, 5).output(5, 0.5)             ││
│  │  • Constraints:  .max_height(15).prefer("efficiency")      ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                  MAS GENERATOR (api/waveforms.py)                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Converts user-friendly specs → valid MAS JSON              ││
│  │  • Waveform synthesis from duty cycle + ripple              ││
│  │  • Operating point generation for multiple conditions       ││
│  │  • boost_inductor_waveforms(), flyback_primary_current()   ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                  PyOpenMagnetics API                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  calculate_advised_magnetics()  │  simulate()  │  wind()   ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                  MKF C++ Engine + MAS Schema                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skill 1: Design Builder (Fluent API) ✅

**Status**: Complete
**Location**: `api/design.py`

### Supported Topologies

| Topology | Builder | Status |
|----------|---------|--------|
| Flyback | `Design.flyback()` | ✅ Complete |
| Buck | `Design.buck()` | ✅ Complete |
| Boost | `Design.boost()` | ✅ Complete |
| Forward | `Design.forward()` | ✅ Complete |
| LLC | `Design.llc()` | ✅ Complete |
| Inductor | `Design.inductor()` | ✅ Complete |
| DAB/CLLC | `Design.dab()` | 🚧 Planned |
| PFC | `Design.pfc()` | 🚧 Planned |

### API Examples

```python
from api.design import Design

# Flyback transformer for USB charger
result = (Design.flyback()
    .vin_ac(85, 265)           # Universal AC input
    .output(20, 3.25)          # 20V @ 3.25A
    .fsw(100e3)                # 100kHz switching
    .prefer("efficiency")
    .solve())

# Buck converter inductor
result = Design.buck().vin(12, 24).vout(5).iout(3).fsw(500e3).solve()

# Boost inductor for EV charger
result = (Design.boost()
    .vin(200, 450)
    .vout(800)
    .pout(10000)
    .fsw(100e3)
    .ambient_temperature(70)
    .solve())
```

### Results Format

```python
from api.results import DesignResult

@dataclass
class DesignResult:
    core: str                    # "ETD 34"
    material: str                # "3C95"
    primary_turns: int
    primary_wire: str            # "AWG 24 (0.51mm)"
    secondary_turns: int | None
    secondary_wire: str | None
    air_gap_mm: float
    core_loss_w: float
    copper_loss_w: float
    total_loss_w: float
    temp_rise_c: float
    bpk_tesla: float
    saturation_margin: float     # Percentage
    bom: list[dict]              # Bill of materials
    warnings: list[str]
```

---

## Skill 2: MCP Server for AI ✅

**Status**: Complete
**Location**: `api/mcp/`

### Tools

| Tool | Description |
|------|-------------|
| `design_power_supply_magnetic` | Design transformer/inductor |
| `analyze_existing_design` | Analyze given component |
| `compare_materials` | Compare core materials |
| `suggest_wire` | Recommend wire for current/freq |

### Resources

| Resource | Description |
|----------|-------------|
| `database/cores/{family}` | List cores in family |
| `database/materials/{type}` | List materials by type |

### Example AI Conversation

```
User: Design a transformer for a 65W USB-C charger.
      Universal AC input, 20V/3.25A output, 100kHz.

AI: [Calls design_power_supply_magnetic]

    For your 65W USB-C charger, I recommend:

    **EFD 25 + 3C95**
    - Primary: 56T AWG 28
    - Secondary: 7T AWG 22 x3 parallel
    - Gap: 0.35mm
    - Losses: 1.2W (core 0.7W + copper 0.5W)
    - Temperature rise: ~35°C
```

---

## Skill 3: Streamlit GUI ✅

**Status**: Complete
**Location**: `api/gui/`

### Pages

1. **Design** - Topology selection, parameter input, results
2. **Database** - Browse cores, materials, wires
3. **Analysis** - Analyze existing designs
4. **Compare** - Side-by-side design comparison

### Launch

```bash
streamlit run api/gui/app.py
```

---

## Skill 4: Example Library ✅

**Status**: Complete
**Location**: `examples/`

### Categories

| Category | Examples |
|----------|----------|
| Consumer | USB PD 20W/65W/140W, Laptop 90W |
| Automotive | 48V DC-DC, Gate drivers, Boost half-bridge |
| Industrial | DIN rail, Medical 60601, VFD chokes, Boost inductor |
| Telecom | PoE, 48V rectifiers |
| Advanced | NSGA2 optimization, Custom simulation |

### Example Structure

```python
"""
USB-C PD 65W Charger - Flyback Transformer Design

Application: Universal laptop/phone charger
Real-world equivalents: Apple 67W, Anker Nano II 65W
"""
from api.design import Design

results = (Design.flyback()
    .vin_ac(85, 265)
    .output(20, 3.25)
    .fsw(100e3)
    .prefer("efficiency")
    .solve())
```

### Running Examples

```bash
# Run all examples
./scripts/run_examples.sh

# Run specific example
python examples/consumer/usb_pd_65w.py
```

---

## Skill 5: FEMMT Bridge ✅

**Status**: Complete
**Location**: `api/bridges/femmt.py`

Export PyOpenMagnetics designs to FEMMT for FEM validation.

```python
from api.bridges.femmt import export_to_femmt

femmt_script = export_to_femmt(design_result)
# Generates executable Python script for FEMMT
```

---

## Skill 6: SW Architect Tools ✅

**Status**: Complete
**Location**: `api/architect/`

- Module analyzer
- Pattern documentation
- API docs generator

---

## Skill 7: Magnetic Expert Knowledge ✅

**Status**: Complete
**Location**: `api/expert/knowledge.py`

### Contents

- **APPLICATIONS**: 20+ application profiles with operating conditions
- **TOPOLOGIES**: Topology selection guide
- **MATERIALS_GUIDE**: Ferrite material selection
- **POWDER_CORE_MATERIALS**: 25+ powder core materials with Steinmetz parameters
- **TRADEOFFS**: Engineering tradeoffs explained

### Powder Core Database

```python
from api.expert.knowledge import POWDER_CORE_MATERIALS, suggest_powder_core_material

# Get material data
mat = POWDER_CORE_MATERIALS["CSC_Mega_Flux_60u"]
print(mat["steinmetz"])  # {'k': 108.0, 'alpha': 1.10, 'beta': 2.15}

# Get recommendations
suggestions = suggest_powder_core_material(
    dc_bias_amps=50,
    frequency_hz=100e3,
    priority="high_bias"  # or "low_loss", "cost", "balanced"
)
```

### Material Families

| Family | Materials | Best For |
|--------|-----------|----------|
| MPP | 26µ, 60µ, 125µ, 147µ, 160µ, 173µ, 200µ | Lowest core loss, filter inductors |
| High Flux | 26µ, 60µ, 125µ, 147µ, 160µ | High DC bias applications |
| Sendust/Kool Mu | 26µ, 60µ, 75µ, 90µ, 125µ | Good balance cost/performance |
| Mega Flux/XFlux | 26µ, 50µ, 60µ, 75µ, 90µ | Highest DC bias, lowest cost |

---

## Sprint 8: Legacy Migration ✅

**Status**: Complete

### Migrated Files

| Original | New Location | Status |
|----------|--------------|--------|
| `magnetic_material_parameters.py` | `api/expert/knowledge.py` | ✅ Migrated |
| `calc_boost_inductor_loss.py` | `examples/industrial/boost_inductor_design.py` | ✅ Migrated |
| `custom_magnetic.json` | `examples/data/bdc6128_inductor.json` | ✅ Moved |
| `results/*.json` | `examples/data/precomputed/` | ✅ Moved |
| `20231124_inductor_nsga2.ipynb` | `examples/advanced/nsga2_inductor_optimization.py` | ✅ Migrated |
| `test_om.ipynb` | `examples/automotive/boost_half_bridge_multi_op.py` | ✅ Migrated |
| `Untitled-1.ipynb` | `examples/advanced/custom_magnetic_simulation.py` | ✅ Migrated |
| `Inductor/*.m` | `archive/matlab_legacy/` | ✅ Archived |

### New Components

1. **Boost Waveform Calculator** (`api/waveforms.py`)
   ```python
   from api.waveforms import boost_inductor_waveforms

   waveforms = boost_inductor_waveforms(
       vin=400, vout=800, power=10000,
       inductance=120e-6, frequency=100e3
   )
   # Returns: current, voltage, i_dc, i_ripple_pp, i_rms, l_critical
   ```

2. **NSGA-II Optimizer** (`api/optimization.py`)
   ```python
   from api.optimization import NSGAOptimizer

   optimizer = NSGAOptimizer(
       objectives=["mass", "total_loss"],
       constraints={"inductance": (100e-6, 140e-6)}
   )
   optimizer.add_variable("turns", range=(20, 60))
   pareto_front = optimizer.run(generations=50)
   ```

---

## Version Tiers: FREE vs PRO

### FREE Features
- Basic topologies (buck, boost, flyback)
- Design adviser
- Core/material database (basic)
- Python API
- Basic examples
- LTspice export

### PRO Features
- Multi-objective optimization (NSGA-II)
- MCP server for AI
- Streamlit GUI
- FEMMT bridge
- Expert knowledge base (full 25+ powder cores)
- Advanced topologies (LLC, DAB, Forward)
- Nanocrystalline materials
- Priority support

### Implementation

```python
# api/__init__.py
import os

PYOM_LICENSE = os.getenv("PYOPENMAGNETICS_LICENSE", "FREE")

def require_pro(feature_name):
    if PYOM_LICENSE != "PRO":
        raise LicenseError(
            f"'{feature_name}' requires PyOpenMagnetics PRO. "
            f"Visit https://openmagnetics.com/pro for licensing."
        )
```

---

## Related Projects & Inspiration

### FEMMT (FEM Magnetics Toolbox) - UPB-LEA
**https://github.com/upb-lea/FEM_Magnetics_Toolbox**

| Aspect | FEMMT | PyOpenMagnetics |
|--------|-------|-----------------|
| Core engine | ONELAB/gmsh FEM | MKF analytical |
| Speed | Minutes (FEM) | Milliseconds |
| Accuracy | High (field-based) | Good (validated) |
| Integration | Export bridge | Native |

### PyScaleXFMR - ETH/OTVAM
**https://github.com/otvam/pyscalexfmr**

Focus on medium-frequency transformer optimization for DAB and SRC converters.

### AI-mag - ETH PES
**https://github.com/ethz-pes/AI-mag**

ML-accelerated inductor design with surrogate models.

---

## Development Scripts

```bash
# Run all examples
./scripts/run_examples.sh

# Pre-commit checks (syntax, imports, tests)
./scripts/pre_commit_check.sh

# Quick checks only (skip slow tests)
./scripts/pre_commit_check.sh --quick

# Full checks including all examples
./scripts/pre_commit_check.sh --full
```

---

## File Structure

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
│   ├── advanced/             # Optimization, custom simulation
│   └── data/                 # Pre-defined magnetics, results
├── src/                      # C++ pybind11 bindings
├── tests/                    # Pytest test suite
├── scripts/                  # Development scripts
│   ├── run_examples.sh       # Run all examples
│   ├── pre_commit_check.sh   # Pre-commit validation
│   └── block_push.sh         # Push blocker (FREE/PRO split)
└── archive/                  # Legacy code reference
    └── matlab_legacy/        # Archived MATLAB files
```

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Time from spec to design | < 5 seconds | ✅ ~2s |
| Lines of user code | < 10 for basic design | ✅ 4-6 lines |
| Example coverage | 50+ applications | ✅ 25+ |
| GUI usability | Productive in < 5 min | ✅ |
| MCP response quality | Actionable BOM | ✅ |
