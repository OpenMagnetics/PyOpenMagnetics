# Contributing Guide

## Setting Up Development Environment

### Prerequisites

1. Install build dependencies:

```bash
# Linux
sudo apt-get install python3-dev cmake build-essential

# macOS
brew install cmake python

# Windows
# Install Visual Studio Build Tools with C++ support
```

2. Clone the repository:

```bash
git clone https://github.com/OpenMagnetics/PyMKF.git
cd PyMKF
```

3. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

4. Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Project Structure

```
PyMKF/
├── api/                 # Python API layer
│   ├── design.py        # Fluent Design API
│   ├── MAS.py           # Auto-generated dataclasses
│   ├── validation.py    # JSON schema validation
│   ├── mcp/             # MCP Server
│   └── gui/             # Streamlit GUI
├── src/                 # C++ pybind11 bindings
│   ├── module.cpp       # Main binding definitions
│   ├── database.cpp     # Core/material/wire database
│   ├── advisers.cpp     # Design recommendation algorithms
│   └── ...
├── tests/               # pytest test suite
├── examples/            # Working examples
├── notebooks/           # Jupyter notebooks
└── docs/                # Documentation
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_core.py -v

# Run all examples
./scripts/run_examples.sh

# Quick validation
./scripts/pre_commit_check.sh
```

## Code Style

### Python Code

- Follow PEP 8
- Use type hints
- Document using NumPy style docstrings

```python
def calculate_losses(
    core_data: dict[str, Any],
    temperature: float
) -> float:
    """Calculate core losses.

    Parameters
    ----------
    core_data : dict[str, Any]
        Core specifications and properties
    temperature : float
        Operating temperature in Celsius

    Returns
    -------
    float
        Calculated losses in Watts
    """
    pass
```

### C++ Code

- Follow the Google C++ Style Guide
- Use consistent naming conventions
- Document using Doxygen style

## Building Documentation

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Contributing Workflow

1. Create a new branch:
```bash
git checkout -b feature/new-feature
```

2. Make changes and commit:
```bash
git add .
git commit -m "feat: add new feature"
```

3. Push changes and create Pull Request

### Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

## Code Review Process

1. Submit PR with:
   - Clear description
   - Test results
   - Documentation updates

2. Address review comments

3. Ensure CI/CD pipeline passes:
   - Tests pass
   - Code style checks pass
