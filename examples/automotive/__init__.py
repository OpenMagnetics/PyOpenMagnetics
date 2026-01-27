"""Automotive power electronics examples."""

from .gate_drive_isolated import design_gate_drive_isolated

__all__ = [
    "design_gate_drive_isolated",
]

# Note: 48v_to_12v_1kw has a numeric prefix so can't be imported directly
# Use: from examples.automotive.buck_48v_to_12v_1kw import design_48v_to_12v_1kw
