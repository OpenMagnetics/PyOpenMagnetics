# Product Requirements Document (PRD)
# PyOpenMagnetics

**Version**: 2.0
**Date**: January 2025
**Status**: Active Development

---

## Executive Summary

PyOpenMagnetics transforms magnetic component design from a specialized art requiring decades of experience into an accessible, automated process. By wrapping the powerful MKF C++ engine with an intuitive Python API, we enable hardware engineers to design transformers and inductors in seconds rather than hours.

### Vision Statement
> Make magnetic design as easy as selecting a capacitor from a catalog.

### Target Users
1. **Hardware Engineers** - Power supply designers who need quick, reliable magnetics
2. **Students** - Learning power electronics without magnetics expertise
3. **AI Assistants** - Claude/GPT providing design recommendations via MCP
4. **Researchers** - Exploring design spaces with optimization algorithms

---

## Problem Statement

### Current Pain Points

| Problem | Impact | Frequency |
|---------|--------|-----------|
| MAS JSON complexity | 50+ lines for simple design | Every design |
| Manual waveform calculation | Error-prone, time-consuming | Every design |
| Trial-and-error core selection | Days of iteration | 80% of projects |
| No automated optimization | Sub-optimal designs ship | 60% of designs |
| Disconnected tools | Copy-paste between tools | Daily |

### The Gap

```
What engineers know:          What MAS needs:
─────────────────────         ────────────────────────────
Vin: 85-265VAC         →      {"operatingPoints": [{
Vout: 12V @ 5A                   "excitationsPerWinding": [{
fsw: 100kHz                        "current": {"waveform": {
                                      "data": [0, 1.2, 0.8, ...],
                                      "time": [0, 2.5e-6, ...]
                                    }},
                                   "voltage": {...}
                                 }]
                               }]}
```

**PyOpenMagnetics bridges this gap.**

---

## Product Goals

### Primary Goals (P0)
1. **Reduce design time** from hours to seconds
2. **Lower barrier to entry** for magnetic design
3. **Improve design quality** through automated optimization
4. **Enable AI integration** via MCP server

### Secondary Goals (P1)
1. Create industry-standard example library
2. Bridge to FEM tools (FEMMT) for validation
3. Support advanced topologies (LLC, DAB)
4. Enable multi-objective optimization

### Nice-to-have (P2)
1. Natural language design input
2. ML-accelerated design space exploration
3. Integration with PCB tools
4. Component sourcing integration

---

## Feature Specifications

### Skill 1: Fluent Design API

**Priority**: P0
**Status**: ✅ Implemented (Sprint 1-3)

#### Description
Python API that accepts familiar engineering parameters and generates MAS internally.

#### User Story
> As a hardware engineer, I want to specify a power supply in terms I understand (Vin, Vout, Power, frequency) so that I can get magnetic designs without learning MAS JSON.

#### API Specification
```python
from api.design import Design

# Fluent builder pattern
result = (Design.flyback()
    .vin_ac(85, 265)           # AC input range
    .output(12, 5)             # 12V @ 5A
    .output(5, 0.5)            # Auxiliary output
    .fsw(100e3)                # 100kHz
    .efficiency(0.88)          # Target efficiency
    .max_height(15)            # Max height in mm
    .prefer("efficiency")      # Optimization priority
    .solve(max_results=5))     # Get top 5 designs

# Result contains:
# - Core shape and material
# - Winding specification
# - Loss breakdown
# - Temperature rise
# - Bill of materials
```

#### Supported Topologies
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

#### Acceptance Criteria
- [ ] All topologies produce valid MAS JSON
- [ ] Design time < 5 seconds for simple designs
- [ ] Results include actionable BOM
- [ ] Error messages are helpful, not cryptic

---

### Skill 2: MCP Server for AI

**Priority**: P0
**Status**: ✅ Implemented (Sprint 2)

#### Description
Model Context Protocol server enabling AI assistants to design magnetics.

#### User Story
> As an AI assistant user, I want to ask Claude to design a transformer so that I can get a complete design recommendation in conversation.

#### Tools
| Tool | Description |
|------|-------------|
| `design_power_supply_magnetic` | Design transformer/inductor |
| `analyze_existing_design` | Analyze given component |
| `compare_materials` | Compare core materials |
| `suggest_wire` | Recommend wire for current/freq |

#### Resources
| Resource | Description |
|----------|-------------|
| `database/cores/{family}` | List cores in family |
| `database/materials/{type}` | List materials by type |

#### Example Conversation
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

    Design notes:
    - Consider interleaved winding for lower leakage
    - Margin tape required for safety isolation
```

---

### Skill 3: Streamlit GUI

**Priority**: P1
**Status**: ✅ Implemented (Sprint 4)

#### Description
Web-based GUI for engineers who prefer visual interfaces.

#### Pages
1. **Design** - Topology selection, parameter input, results
2. **Database** - Browse cores, materials, wires
3. **Analysis** - Analyze existing designs
4. **Compare** - Side-by-side design comparison

#### Launch
```bash
streamlit run api/gui/app.py
```

---

### Skill 4: Example Library

**Priority**: P1
**Status**: ✅ Implemented (Sprint 3, 8)

#### Categories
| Category | Examples | Status |
|----------|----------|--------|
| Consumer | USB PD 20W/65W/140W, Laptop adapters | ✅ |
| Automotive | 48V DC-DC, Gate drivers, EV boost | ✅ |
| Industrial | DIN rail, Medical, VFD chokes | ✅ |
| Telecom | PoE, Rectifiers | ✅ |
| Advanced | NSGA2 optimization, Custom simulation | ✅ |

#### Example Format
Each example includes:
- Real-world context and equivalents
- Complete working code
- Expected output documentation
- Design notes and warnings

---

### Skill 5: FEMMT Bridge

**Priority**: P1
**Status**: ✅ Implemented (Sprint 5)

#### Description
Export PyOpenMagnetics designs to FEMMT for FEM validation.

```python
from api.bridges.femmt import export_to_femmt

femmt_script = export_to_femmt(design_result)
# Generates executable Python script for FEMMT
```

---

### Skill 6: SW Architect Tools

**Priority**: P2
**Status**: ✅ Implemented (Sprint 6)

#### Description
Code analysis tools for maintaining the codebase.

- Module analyzer
- Pattern documentation
- API docs generator

---

### Skill 7: Magnetic Expert Knowledge

**Priority**: P1
**Status**: ✅ Implemented (Sprint 7)

#### Description
Domain knowledge base for applications, materials, and tradeoffs.

```python
from api.expert.knowledge import (
    APPLICATIONS,        # 20+ application profiles
    TOPOLOGIES,          # Topology selection guide
    MATERIALS_GUIDE,     # Material selection
    TRADEOFFS,           # Engineering tradeoffs explained
    suggest_topology,
    suggest_core_material
)
```

---

### Skill 8: Legacy Migration

**Priority**: P1
**Status**: ✅ Implemented (Sprint 8)

#### Description
Upgrade legacy MATLAB/notebook code to fluent API.

- Migrated 25+ powder core materials to knowledge base
- Created boost waveform calculator
- Ported NSGA2 optimization example
- Archived MATLAB legacy code

---

## Multi-Objective Optimization Module

**Priority**: P1
**Status**: ✅ Implemented (Sprint 8)

#### Description
NSGA-II optimization for Pareto-optimal designs.

```python
from api.optimization import NSGAOptimizer

optimizer = NSGAOptimizer(
    objectives=["mass", "total_loss"],
    constraints={"inductance": (100e-6, 140e-6)}
)
optimizer.add_variable("turns", range=(20, 60))
optimizer.add_variable("core_size", range=(0.5, 2.0))

pareto_front = optimizer.run(generations=50)
```

---

## Version Tiers (FREE vs PRO)

### Rationale
Advanced features require significant R&D investment. Tiering enables:
1. Wide adoption via free core features
2. Sustainable development via PRO revenue
3. Clear upgrade path for serious users

### Feature Matrix

| Feature | FREE | PRO |
|---------|:----:|:---:|
| **Design API** | | |
| Buck converter | ✅ | ✅ |
| Boost converter | ✅ | ✅ |
| Flyback (basic) | ✅ | ✅ |
| Forward converter | ❌ | ✅ |
| LLC resonant | ❌ | ✅ |
| DAB/CLLC | ❌ | ✅ |
| **Database** | | |
| Core shapes | ✅ | ✅ |
| Ferrite materials | ✅ | ✅ |
| Powder cores (basic) | ✅ | ✅ |
| Powder cores (full 25+) | ❌ | ✅ |
| Nanocrystalline | ❌ | ✅ |
| **Optimization** | | |
| Design adviser | ✅ | ✅ |
| Multi-objective (NSGA-II) | ❌ | ✅ |
| Pareto visualization | ❌ | ✅ |
| **Interfaces** | | |
| Python API | ✅ | ✅ |
| MCP Server | ❌ | ✅ |
| Streamlit GUI | ❌ | ✅ |
| **Integrations** | | |
| FEMMT export | ❌ | ✅ |
| LTspice export | ✅ | ✅ |
| **Knowledge** | | |
| Basic examples | ✅ | ✅ |
| Expert knowledge base | ❌ | ✅ |
| Application guides | ❌ | ✅ |
| **Support** | | |
| GitHub Issues | ✅ | ✅ |
| Priority support | ❌ | ✅ |
| Custom development | ❌ | ✅ |

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

# In optimization.py
def NSGAOptimizer(...):
    require_pro("Multi-objective optimization")
    ...
```

---

## Technical Requirements

### Performance
| Metric | Target | Current |
|--------|--------|---------|
| Simple design time | < 5s | ~2s |
| Complex design time | < 30s | ~15s |
| Memory usage | < 500MB | ~200MB |
| Startup time | < 2s | ~1s |

### Compatibility
- Python 3.10, 3.11, 3.12
- Ubuntu 22.04+, Windows 10+, macOS 12+
- x86_64, arm64

### Dependencies
- Core: numpy, pybind11
- Optional: pymoo (optimization), streamlit (GUI), mcp (AI)

---

## Quality Assurance

### Testing Strategy
1. **Unit tests** - All API functions
2. **Integration tests** - End-to-end workflows
3. **Example validation** - All examples run successfully
4. **Regression tests** - Design results within tolerance

### Test Coverage Target
- Core API: 90%
- Design builders: 85%
- Expert knowledge: 80%

### Pre-commit Checks
```bash
./scripts/pre_commit_check.sh
# Runs: syntax check, pytest, example validation
```

---

## Roadmap

### Q1 2025 (Current)
- [x] Fluent Design API
- [x] MCP Server
- [x] Streamlit GUI
- [x] Example library
- [x] FEMMT bridge
- [x] Expert knowledge base
- [x] NSGA-II optimization
- [x] Legacy migration

### Q2 2025
- [ ] DAB/CLLC topology
- [ ] PFC boost builder
- [ ] Thermal modeling
- [ ] Component sourcing API

### Q3 2025
- [ ] ML surrogate models
- [ ] Natural language input
- [ ] PCB integration
- [ ] Mobile-friendly GUI

### Q4 2025
- [ ] Cloud deployment
- [ ] Enterprise features
- [ ] API metering
- [ ] Custom material fitting

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Design time reduction | 10x | User study |
| Adoption (downloads) | 10K/month | PyPI stats |
| Active users | 1K/month | Telemetry |
| PRO conversion | 5% | Sales |
| GitHub stars | 1K | GitHub |
| Issue resolution | < 7 days | GitHub |

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MKF API changes | High | Low | Pin MKF version, adapter layer |
| Competition | Medium | Medium | Focus on UX, examples |
| Performance issues | Medium | Low | Profiling, caching |
| License confusion | Low | Medium | Clear documentation |

---

## Appendix

### Glossary
- **MAS**: Magnetic Agnostic Structure - JSON schema for magnetic components
- **MKF**: Magnetics Knowledge Foundation - C++ simulation engine
- **MCP**: Model Context Protocol - AI tool integration standard
- **FEMMT**: FEM Magnetics Toolbox - FEM simulation tool

### References
- [MAS Schema](https://github.com/OpenMagnetics/MAS)
- [MKF Engine](https://github.com/OpenMagnetics/MKF)
- [FEMMT](https://github.com/upb-lea/FEM_Magnetics_Toolbox)
- [MCP Specification](https://modelcontextprotocol.io)
