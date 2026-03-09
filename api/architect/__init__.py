"""
Software Architect Tools for PyOpenMagnetics.

Tools for code analysis, pattern documentation, and architecture generation.
"""

from .analyzer import analyze_module, analyze_package, get_module_metrics
from .patterns import PATTERNS, get_pattern, list_patterns
from .docs_generator import generate_api_docs, generate_architecture_diagram

__all__ = [
    "analyze_module",
    "analyze_package",
    "get_module_metrics",
    "PATTERNS",
    "get_pattern",
    "list_patterns",
    "generate_api_docs",
    "generate_architecture_diagram",
]
