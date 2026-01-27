# Installation Guide

## Requirements

### Core Dependencies
- Python >= 3.10
- numpy >= 1.19.0
- pandas >= 1.3.0

### Build Dependencies
- CMake >= 3.15
- C++ compiler with C++23 support
- pybind11
- Node.js 18+ (for schema generation)

## Installation Methods

### From PyPI (Recommended)

PyOpenMagnetics can be installed using pip:

```bash
pip install pyopenmagnetics
```

### From Source

```bash
git clone https://github.com/OpenMagnetics/PyMKF.git
cd PyMKF
pip install .
```

### Build Wheel

```bash
python -m build
```

### Cross-Platform Wheel Building

```bash
python -m cibuildwheel --output-dir wheelhouse
```

## Troubleshooting

### Common Issues

1. **CMake Not Found**
   - Ensure CMake is installed and in your PATH
   - Check CMake version requirements (>= 3.15)

2. **Compiler Errors**
   - Verify C++23 compiler support
   - On Linux, use gcc-toolset-13 or newer

3. **Python Version Mismatch**
   - PyOpenMagnetics supports Python 3.10-3.12
   - Check virtual environment settings

## References

- [PyPI Package](https://pypi.org/project/PyMKF/)
- [GitHub Repository](https://github.com/OpenMagnetics/PyMKF)
