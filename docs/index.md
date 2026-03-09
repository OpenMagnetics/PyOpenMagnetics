# PyOpenMagnetics Documentation

Welcome to the PyOpenMagnetics documentation!

PyOpenMagnetics is a Python library for designing and analyzing magnetic components - transformers, inductors, and chokes for power electronics. It wraps the OpenMagnetics MKF C++ engine and provides multiple interfaces.

## Features

- **Fluent Design API** - `Design.flyback().vin_ac(85, 265).output(12, 5).solve()`
- **Low-level C++ Bindings** - Direct access to MKF engine via `PyOpenMagnetics` module
- **MCP Server** - AI assistant integration for natural language design
- **Streamlit GUI** - Visual interface for hardware engineers

## Quick Start

```python
from api.design import Design

result = Design.flyback() \
    .vin_ac(85, 265) \
    .output(12, 5) \
    .fsw(100e3) \
    .solve(verbose=True)

print(f"Best design: {result[0].core} with {result[0].material}")
print(f"Total loss: {result[0].total_loss_w:.2f} W")
```

## Available Functions

PyOpenMagnetics provides comprehensive functionality including:

- Core data calculation and database access
- Material property queries (Steinmetz coefficients, permeability)
- Winding design and loss calculations
- Design advisers for optimal component selection
- Visualization tools (core plots, field plots)

See the [Examples](examples.md) section for detailed usage patterns.
