# Examples

## Basic Usage

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
    .ripple_ratio(0.3)         # 30% current ripple

results = design.solve()
```

### Design a Boost Inductor

```python
design = Design.boost() \
    .vin(200, 400) \           # Input voltage range
    .vout(800) \               # Output voltage
    .pout(3000) \              # Output power
    .fsw(65e3) \               # Switching frequency
    .efficiency(0.97)          # Target efficiency

results = design.solve()
```

## Database Queries

### Query Materials

```python
import PyOpenMagnetics

# Get all available materials
materials = PyOpenMagnetics.get_core_material_names()
print(f"Available materials: {len(materials)}")

# Get material details
material = PyOpenMagnetics.find_core_material_by_name("3C95")

# Get Steinmetz coefficients for loss calculation
steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients("3C95", 100000)
print(f"k={steinmetz['k']}, alpha={steinmetz['alpha']}, beta={steinmetz['beta']}")
```

### Query Core Shapes

```python
# Get all available shapes
shapes = PyOpenMagnetics.get_core_shape_names()

# Get shape details
shape = PyOpenMagnetics.find_core_shape_by_name("E 42/21/15")
```

### Query Wires

```python
# Get available wires
wires = PyOpenMagnetics.get_wire_names()

# Get wire details
wire = PyOpenMagnetics.find_wire_by_name("Round 0.5 - Grade 1")
```

## Loss Calculations

### Core Losses

```python
models = {"coreLosses": "IGSE", "reluctance": "ZHANG"}

losses = PyOpenMagnetics.calculate_core_losses(core, coil, inputs, models)
print(f"Core loss: {losses['coreLosses']:.3f} W")
print(f"B_peak: {losses['magneticFluxDensityPeak']*1000:.1f} mT")
```

### Winding Losses

```python
winding_losses = PyOpenMagnetics.calculate_winding_losses(magnetic, operating_point, 85)
print(f"Winding loss: {winding_losses['windingLosses']:.3f} W")
```

## Real-World Examples

The `examples/` directory contains 17 working examples across different applications:

### Consumer Electronics
- USB PD 65W charger (`consumer/usb_pd_65w.py`)

### Automotive
- 48V DC-DC converters (`automotive/boost_half_bridge_multi_op.py`)
- Gate drive transformers (`automotive/gate_drive_isolated.py`)

### Industrial
- Boost inductor design (`industrial/boost_inductor_design.py`)

### Telecom
- 48V 3kW rectifier (`telecom/rectifier_48v_3kw.py`)

### Advanced
- Custom magnetic simulation (`advanced/custom_magnetic_simulation.py`)
- NSGA2 multi-objective optimization (`advanced/nsga2_inductor_optimization.py`)

## Interactive Notebooks

The `notebooks/` directory contains Jupyter notebooks for interactive learning:

1. **01_getting_started.ipynb** - Introduction to PyOpenMagnetics
2. **02_buck_inductor.ipynb** - Buck converter inductor design
3. **03_core_losses.ipynb** - Core loss analysis and material comparison

## Best Practices

1. **Always process inputs first**
   ```python
   processed = PyOpenMagnetics.process_inputs(inputs)
   magnetics = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
   ```

2. **Handle return values correctly**
   ```python
   result = PyOpenMagnetics.calculate_advised_magnetics(processed, 5, "STANDARD_CORES")
   if isinstance(result, str):
       magnetics = json.loads(result)
   elif isinstance(result, dict):
       data = result.get("data", result)
       magnetics = json.loads(data) if isinstance(data, str) else data
   ```

3. **Check for errors**
   ```python
   result = PyOpenMagnetics.calculate_core_data(data, False)
   if isinstance(result, str) and result.startswith("Exception:"):
       print(f"Error: {result}")
   ```
