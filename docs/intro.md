# Introduction to PyOpenMagnetics

PyOpenMagnetics is a comprehensive Python library for magnetic component design. It provides tools for designing transformers, inductors, and chokes used in power electronics applications.

## Architecture

```
User Interfaces
├── api/design.py        Fluent Design API (Design.flyback(), Design.buck(), etc.)
├── api/mcp/             MCP Server for AI assistants
└── api/gui/             Streamlit GUI
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

## Supported Topologies

| Topology | Method | Use Case |
|----------|--------|----------|
| Flyback | `Design.flyback()` | Isolated SMPS <150W |
| Buck | `Design.buck()` | Non-isolated step-down |
| Boost | `Design.boost()` | Non-isolated step-up, PFC |
| Forward | `Design.forward()` | Isolated, higher power |
| LLC | `Design.llc()` | High efficiency, resonant |
| Inductor | `Design.inductor()` | Standalone inductors |

## Core Materials

| Manufacturer | Materials |
|--------------|-----------|
| TDK/EPCOS | N27, N49, N87, N95, N97, PC40, PC95 |
| Ferroxcube | 3C90, 3C94, 3C95, 3C96, 3F3, 3F4, 3F35 |
| Fair-Rite | 67, 77, 78 |
| Magnetics Inc | MPP, High Flux, Kool Mu, XFlux |
| Micrometals | Iron powder: -2, -8, -18, -26, -52 |

## Core Shape Families

E, EI, EFD, EQ, ER, ETD, EC, PQ, PM, RM, T (toroidal), P, PT, U, UI, LP (planar)
