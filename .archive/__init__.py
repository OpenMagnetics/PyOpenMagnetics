"""
Magnetic Expert - Domain knowledge for hardware engineers.

Provides application-focused design guidance, not code-focused APIs.
"""

from .knowledge import APPLICATIONS, TOPOLOGIES, MATERIALS_GUIDE, TRADEOFFS
from .examples import ExampleGenerator, generate_application_examples
from .conversation import MagneticExpert

__all__ = [
    "APPLICATIONS",
    "TOPOLOGIES",
    "MATERIALS_GUIDE",
    "TRADEOFFS",
    "ExampleGenerator",
    "generate_application_examples",
    "MagneticExpert",
]
