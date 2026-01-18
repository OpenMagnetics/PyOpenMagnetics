"""
PyOpenMagnetics Schema Validation Module

Provides JSON Schema validation for MAS (Magnetic Agnostic Structure) inputs
to catch configuration errors early with helpful error messages.

Usage:
    from PyOpenMagnetics.validation import validate_inputs, validate_magnetic, validate_core

    # Validate inputs before calling PyOpenMagnetics functions
    errors = validate_inputs(inputs_dict)
    if errors:
        for error in errors:
            print(f"Validation error: {error}")
    else:
        # Safe to proceed
        result = PyOpenMagnetics.simulate(inputs, magnetic, models)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Try to import jsonschema, provide helpful message if not available
try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class SchemaValidationError(Exception):
    """Exception raised when schema validation fails."""
    
    def __init__(self, errors: List[str], path: str = ""):
        self.errors = errors
        self.path = path
        message = f"Validation failed with {len(errors)} error(s)"
        if path:
            message += f" at {path}"
        super().__init__(message)


def _get_schema_dir() -> Path:
    """Get the path to MAS schema files."""
    # Look for schemas in common locations
    possible_paths = [
        Path(__file__).parent.parent / "MAS" / "schemas",
        Path(__file__).parent / "schemas",
        Path.home() / "OpenMagnetics" / "MAS" / "schemas",
        Path("/home/alf/OpenMagnetics/MAS/schemas"),
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "inputs.json").exists():
            return path
    
    return None


def _load_schema(schema_name: str) -> Optional[Dict[str, Any]]:
    """Load a JSON schema file."""
    schema_dir = _get_schema_dir()
    if not schema_dir:
        return None
    
    schema_file = schema_dir / f"{schema_name}.json"
    if not schema_file.exists():
        return None
    
    with open(schema_file, 'r') as f:
        return json.load(f)


def _format_validation_error(error: 'ValidationError') -> str:
    """Format a validation error into a human-readable message."""
    path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
    
    if error.validator == 'required':
        missing = list(error.validator_value)
        return f"Missing required field(s) at '{path}': {missing}"
    
    elif error.validator == 'type':
        expected = error.validator_value
        actual = type(error.instance).__name__
        return f"Wrong type at '{path}': expected {expected}, got {actual}"
    
    elif error.validator == 'enum':
        allowed = error.validator_value
        return f"Invalid value at '{path}': must be one of {allowed}"
    
    elif error.validator == 'minimum':
        return f"Value too small at '{path}': minimum is {error.validator_value}"
    
    elif error.validator == 'maximum':
        return f"Value too large at '{path}': maximum is {error.validator_value}"
    
    elif error.validator == 'additionalProperties':
        return f"Unexpected property at '{path}': {error.message}"
    
    else:
        return f"Validation error at '{path}': {error.message}"


def validate_inputs(inputs: Dict[str, Any], raise_on_error: bool = False) -> List[str]:
    """
    Validate an inputs dictionary against the MAS inputs schema.
    
    Args:
        inputs: Dictionary containing design requirements and operating points
        raise_on_error: If True, raise SchemaValidationError on validation failure
        
    Returns:
        List of validation error messages (empty if valid)
        
    Raises:
        SchemaValidationError: If raise_on_error=True and validation fails
        
    Example:
        >>> inputs = {
        ...     "designRequirements": {
        ...         "magnetizingInductance": {"nominal": 100e-6}
        ...     },
        ...     "operatingPoints": [...]
        ... }
        >>> errors = validate_inputs(inputs)
        >>> if not errors:
        ...     print("Inputs are valid!")
    """
    if not HAS_JSONSCHEMA:
        return ["jsonschema package not installed. Install with: pip install jsonschema"]
    
    schema = _load_schema("inputs")
    if not schema:
        return ["Could not find MAS schema files. Skipping validation."]
    
    errors = []
    validator = Draft7Validator(schema)
    
    for error in validator.iter_errors(inputs):
        errors.append(_format_validation_error(error))
    
    if errors and raise_on_error:
        raise SchemaValidationError(errors, "inputs")
    
    return errors


def validate_magnetic(magnetic: Dict[str, Any], raise_on_error: bool = False) -> List[str]:
    """
    Validate a magnetic component dictionary against the MAS magnetic schema.
    
    Args:
        magnetic: Dictionary containing core and coil specifications
        raise_on_error: If True, raise SchemaValidationError on validation failure
        
    Returns:
        List of validation error messages (empty if valid)
        
    Example:
        >>> magnetic = {
        ...     "core": {...},
        ...     "coil": {...}
        ... }
        >>> errors = validate_magnetic(magnetic)
    """
    if not HAS_JSONSCHEMA:
        return ["jsonschema package not installed. Install with: pip install jsonschema"]
    
    schema = _load_schema("magnetic")
    if not schema:
        return ["Could not find MAS schema files. Skipping validation."]
    
    errors = []
    validator = Draft7Validator(schema)
    
    for error in validator.iter_errors(magnetic):
        errors.append(_format_validation_error(error))
    
    if errors and raise_on_error:
        raise SchemaValidationError(errors, "magnetic")
    
    return errors


def validate_core(core: Dict[str, Any]) -> List[str]:
    """
    Validate a core dictionary structure.
    
    Args:
        core: Dictionary containing core specifications
        
    Returns:
        List of validation error messages (empty if valid)
        
    Example:
        >>> core = {
        ...     "functionalDescription": {
        ...         "shape": "ETD 39/20/13",
        ...         "material": "3C95",
        ...         "gapping": [],
        ...         "numberStacks": 1
        ...     }
        ... }
        >>> errors = validate_core(core)
    """
    errors = []
    
    # Basic structural validation
    if not isinstance(core, dict):
        return ["Core must be a dictionary"]
    
    # Check for functional description
    if "functionalDescription" not in core:
        errors.append("Core must have 'functionalDescription' field")
    else:
        func_desc = core["functionalDescription"]
        
        if not isinstance(func_desc, dict):
            errors.append("'functionalDescription' must be a dictionary")
        else:
            # Required fields
            if "shape" not in func_desc:
                errors.append("Core functionalDescription must have 'shape' field")
            
            if "material" not in func_desc:
                errors.append("Core functionalDescription must have 'material' field")
            
            # Validate gapping if present
            if "gapping" in func_desc:
                gapping = func_desc["gapping"]
                if not isinstance(gapping, list):
                    errors.append("'gapping' must be a list")
                else:
                    for i, gap in enumerate(gapping):
                        if not isinstance(gap, dict):
                            errors.append(f"Gap {i} must be a dictionary")
                        elif "length" not in gap:
                            errors.append(f"Gap {i} must have 'length' field")
            
            # Validate numberStacks
            if "numberStacks" in func_desc:
                if not isinstance(func_desc["numberStacks"], (int, float)):
                    errors.append("'numberStacks' must be a number")
                elif func_desc["numberStacks"] < 1:
                    errors.append("'numberStacks' must be >= 1")
    
    return errors


def validate_operating_point(operating_point: Dict[str, Any]) -> List[str]:
    """
    Validate a single operating point dictionary.
    
    Args:
        operating_point: Dictionary containing operating conditions
        
    Returns:
        List of validation error messages (empty if valid)
        
    Example:
        >>> op = {
        ...     "conditions": {"ambientTemperature": 25},
        ...     "excitationsPerWinding": [
        ...         {"frequency": 100000, "current": {...}}
        ...     ]
        ... }
        >>> errors = validate_operating_point(op)
    """
    errors = []
    
    if not isinstance(operating_point, dict):
        return ["Operating point must be a dictionary"]
    
    # Check for excitations
    if "excitationsPerWinding" not in operating_point:
        errors.append("Operating point must have 'excitationsPerWinding' field")
    else:
        excitations = operating_point["excitationsPerWinding"]
        if not isinstance(excitations, list):
            errors.append("'excitationsPerWinding' must be a list")
        elif len(excitations) == 0:
            errors.append("'excitationsPerWinding' must have at least one winding excitation")
        else:
            for i, exc in enumerate(excitations):
                if not isinstance(exc, dict):
                    errors.append(f"Excitation {i} must be a dictionary")
                else:
                    if "frequency" not in exc:
                        errors.append(f"Excitation {i} must have 'frequency' field")
                    elif not isinstance(exc["frequency"], (int, float)):
                        errors.append(f"Excitation {i} 'frequency' must be a number")
                    elif exc["frequency"] <= 0:
                        errors.append(f"Excitation {i} 'frequency' must be positive")
    
    # Check conditions if present
    if "conditions" in operating_point:
        conditions = operating_point["conditions"]
        if not isinstance(conditions, dict):
            errors.append("'conditions' must be a dictionary")
        else:
            if "ambientTemperature" in conditions:
                temp = conditions["ambientTemperature"]
                if not isinstance(temp, (int, float)):
                    errors.append("'ambientTemperature' must be a number")
                elif temp < -273.15:
                    errors.append("'ambientTemperature' cannot be below absolute zero")
    
    return errors


def validate_waveform(waveform: Dict[str, Any], waveform_type: str = "current") -> List[str]:
    """
    Validate a waveform specification (current or voltage).
    
    Args:
        waveform: Dictionary containing waveform specification
        waveform_type: Type of waveform ("current" or "voltage")
        
    Returns:
        List of validation error messages (empty if valid)
        
    Example:
        >>> current = {
        ...     "processed": {
        ...         "label": "Triangular",
        ...         "peakToPeak": 2.0,
        ...         "offset": 10.0,
        ...         "dutyCycle": 0.5
        ...     }
        ... }
        >>> errors = validate_waveform(current, "current")
    """
    errors = []
    
    if not isinstance(waveform, dict):
        return [f"{waveform_type.capitalize()} waveform must be a dictionary"]
    
    # Check for processed or waveform data
    if "processed" not in waveform and "waveform" not in waveform:
        errors.append(f"{waveform_type.capitalize()} must have 'processed' or 'waveform' field")
    
    if "processed" in waveform:
        processed = waveform["processed"]
        if not isinstance(processed, dict):
            errors.append("'processed' must be a dictionary")
        else:
            valid_labels = ["Sinusoidal", "Triangular", "Rectangular", "Trapezoidal", "Custom"]
            if "label" in processed and processed["label"] not in valid_labels:
                errors.append(f"Invalid waveform label: must be one of {valid_labels}")
            
            if "peakToPeak" in processed:
                if not isinstance(processed["peakToPeak"], (int, float)):
                    errors.append("'peakToPeak' must be a number")
                elif processed["peakToPeak"] < 0:
                    errors.append("'peakToPeak' must be non-negative")
            
            if "dutyCycle" in processed:
                dc = processed["dutyCycle"]
                if not isinstance(dc, (int, float)):
                    errors.append("'dutyCycle' must be a number")
                elif dc < 0 or dc > 1:
                    errors.append("'dutyCycle' must be between 0 and 1")
    
    return errors


def quick_validate(data: Dict[str, Any], data_type: str = "auto") -> bool:
    """
    Quick validation check - returns True if valid, False otherwise.
    
    Args:
        data: Dictionary to validate
        data_type: One of "inputs", "magnetic", "core", "operating_point", or "auto"
        
    Returns:
        True if validation passes, False otherwise
        
    Example:
        >>> if quick_validate(inputs, "inputs"):
        ...     result = PyOpenMagnetics.simulate(inputs, magnetic, models)
    """
    if data_type == "auto":
        # Try to detect type
        if "designRequirements" in data or "operatingPoints" in data:
            data_type = "inputs"
        elif "core" in data and "coil" in data:
            data_type = "magnetic"
        elif "functionalDescription" in data:
            data_type = "core"
        elif "excitationsPerWinding" in data:
            data_type = "operating_point"
        else:
            return True  # Can't detect type, assume valid
    
    validators = {
        "inputs": validate_inputs,
        "magnetic": validate_magnetic,
        "core": validate_core,
        "operating_point": validate_operating_point,
    }
    
    validator = validators.get(data_type)
    if not validator:
        return True
    
    errors = validator(data)
    return len(errors) == 0


def print_validation_report(data: Dict[str, Any], data_type: str = "inputs") -> None:
    """
    Print a formatted validation report.
    
    Args:
        data: Dictionary to validate
        data_type: Type of data ("inputs", "magnetic", "core", "operating_point")
        
    Example:
        >>> print_validation_report(inputs, "inputs")
        ✓ Validation passed for inputs
    """
    validators = {
        "inputs": validate_inputs,
        "magnetic": validate_magnetic,
        "core": validate_core,
        "operating_point": validate_operating_point,
    }
    
    validator = validators.get(data_type)
    if not validator:
        print(f"Unknown data type: {data_type}")
        return
    
    errors = validator(data)
    
    if not errors:
        print(f"✓ Validation passed for {data_type}")
    else:
        print(f"✗ Validation failed for {data_type} ({len(errors)} error(s)):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")


# Make common functions available at module level
__all__ = [
    'validate_inputs',
    'validate_magnetic', 
    'validate_core',
    'validate_operating_point',
    'validate_waveform',
    'quick_validate',
    'print_validation_report',
    'SchemaValidationError',
    'HAS_JSONSCHEMA',
]
