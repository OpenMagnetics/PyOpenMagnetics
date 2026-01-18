# PyOpenMagnetics Jupyter Notebooks

Interactive tutorials for learning PyOpenMagnetics.

## Prerequisites

```bash
pip install pyopenmagnetics matplotlib numpy
```

## Tutorials

### Getting Started
- **[01_getting_started.ipynb](01_getting_started.ipynb)** - Introduction to PyOpenMagnetics concepts, database exploration, and basic operations

### Design Examples
- **[02_buck_inductor.ipynb](02_buck_inductor.ipynb)** - Complete workflow for designing a buck converter inductor with visualization

### Analysis Deep-Dives  
- **[03_core_losses.ipynb](03_core_losses.ipynb)** - Core loss fundamentals: frequency, temperature, materials, and waveform effects

## Learning Path

1. Start with **01_getting_started** to understand the basics
2. Work through **02_buck_inductor** for a practical design example
3. Dive into **03_core_losses** for detailed loss analysis

## Running the Notebooks

### VS Code
1. Install the Jupyter extension
2. Open any `.ipynb` file
3. Select a Python kernel with PyOpenMagnetics installed
4. Run cells with `Shift+Enter`

### Jupyter Lab
```bash
pip install jupyterlab
jupyter lab
```

### Google Colab
Upload notebooks to [Google Colab](https://colab.research.google.com/) and install PyOpenMagnetics:
```python
!pip install pyopenmagnetics
```

## MAS Schema Overview

PyOpenMagnetics uses the **MAS (Magnetic Agnostic Structure)** JSON schema:

```
┌─────────────────────────────────────────┐
│                  MAS                     │
├─────────────────────────────────────────┤
│  Inputs                                  │
│    ├── Design Requirements               │
│    │     ├── Inductance                  │
│    │     ├── Turns Ratios                │
│    │     └── Constraints                 │
│    └── Operating Points                  │
│          ├── Frequency                   │
│          ├── Current Waveforms           │
│          └── Temperature                 │
├─────────────────────────────────────────┤
│  Magnetic                                │
│    ├── Core                              │
│    │     ├── Shape                       │
│    │     ├── Material                    │
│    │     └── Gapping                     │
│    └── Coil                              │
│          ├── Windings                    │
│          ├── Wire Types                  │
│          └── Turns/Layers                │
├─────────────────────────────────────────┤
│  Outputs                                 │
│    ├── Core Losses                       │
│    ├── Winding Losses                    │
│    ├── Temperature Rise                  │
│    └── Inductance Values                 │
└─────────────────────────────────────────┘
```

## Resources

- [PyOpenMagnetics GitHub](https://github.com/OpenMagnetics/PyOpenMagnetics) - Source code and documentation
- [MAS Schema](https://github.com/OpenMagnetics/MAS) - Magnetic Agnostic Structure definitions
- [MKF Engine](https://github.com/OpenMagnetics/MKF) - C++ computation engine
