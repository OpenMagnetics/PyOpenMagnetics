# PyOpenMagnetics Examples

This directory contains practical examples demonstrating PyOpenMagnetics workflows.

## Available Examples

| File | Description |
|------|-------------|
| [flyback_design.py](flyback_design.py) | Complete flyback transformer design workflow |
| [buck_inductor.py](buck_inductor.py) | Buck converter output inductor design |

## Running Examples

```bash
# Install PyOpenMagnetics first
pip install PyOpenMagnetics

# Run an example
python examples/flyback_design.py
```

## Example Topics Covered

### flyback_design.py
- Defining multi-output flyback requirements
- Using the design adviser
- Calculating core and winding losses
- Exploring the material/shape database

### buck_inductor.py
- Non-isolated inductor design
- Working with DC bias and saturation
- Wire selection for high currents
- Powder core considerations

## Creating Your Own Designs

All examples follow this general workflow:

```python
import PyOpenMagnetics

# 1. Define requirements
inputs = {
    "designRequirements": {
        "magnetizingInductance": {"nominal": 100e-6},
        # ... other requirements
    },
    "operatingPoints": [{
        "conditions": {"ambientTemperature": 25},
        "excitationsPerWinding": [{
            "frequency": 100000,
            "current": {"waveform": {...}},
            "voltage": {"waveform": {...}}
        }]
    }]
}

# 2. Process inputs (adds harmonics)
processed = PyOpenMagnetics.process_inputs(inputs)

# 3. Get recommendations
magnetics = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")

# 4. Analyze results
for mag in magnetics:
    losses = PyOpenMagnetics.calculate_core_losses(
        mag["magnetic"]["core"],
        mag["magnetic"]["coil"],
        processed,
        {"coreLosses": "IGSE", "reluctance": "ZHANG"}
    )
    print(f"Core losses: {losses['coreLosses']:.3f} W")
```

## Additional Resources

- **[llms.txt](../llms.txt)** - Complete API reference
- **[PyOpenMagnetics.pyi](../PyOpenMagnetics.pyi)** - Type stubs for IDE support
- **[MAS Schema](https://github.com/OpenMagnetics/MAS)** - Data structure definitions
