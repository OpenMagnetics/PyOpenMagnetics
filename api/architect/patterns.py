"""
Design Pattern Library for PyOpenMagnetics.

Documents the design patterns used in the codebase with examples.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PatternInfo:
    """Information about a design pattern."""
    name: str
    category: str  # creational, structural, behavioral
    description: str
    use_case: str
    example_location: str
    example_code: str


PATTERNS = {
    "fluent_builder": PatternInfo(
        name="Fluent Builder",
        category="creational",
        description="""
The Fluent Builder pattern provides a readable way to construct complex objects
step by step. Each method returns 'self' to enable method chaining.
        """.strip(),
        use_case="""
Used for topology builders (FlybackBuilder, BuckBuilder, etc.) to allow
engineers to specify design parameters in a natural, readable way.
        """.strip(),
        example_location="api/design.py",
        example_code="""
# Fluent builder pattern in action
design = (
    Design.flyback()
    .vin_ac(85, 265)
    .output(12, 5)
    .fsw(100e3)
    .efficiency(0.87)
    .max_height(15)
    .solve()
)
        """.strip(),
    ),

    "factory_method": PatternInfo(
        name="Factory Method",
        category="creational",
        description="""
The Factory Method pattern provides an interface for creating objects without
specifying their concrete classes. Static methods on a class create instances
of appropriate subclasses.
        """.strip(),
        use_case="""
Used in the Design class to create topology-specific builders without
requiring the user to know the specific builder class names.
        """.strip(),
        example_location="api/design.py",
        example_code="""
class Design:
    @staticmethod
    def flyback() -> 'FlybackBuilder':
        return FlybackBuilder()

    @staticmethod
    def buck() -> 'BuckBuilder':
        return BuckBuilder()

# Usage - user doesn't need to know builder class names
builder = Design.flyback()
        """.strip(),
    ),

    "dataclass_result": PatternInfo(
        name="Dataclass Result",
        category="structural",
        description="""
Using dataclasses to represent structured result data provides automatic
__init__, __repr__, and comparison methods. Combined with factory classmethods,
this creates clean, immutable result objects.
        """.strip(),
        use_case="""
Used for DesignResult, WindingInfo, and BOMItem to represent magnetic
component design outputs in a structured, type-safe way.
        """.strip(),
        example_location="api/results.py",
        example_code="""
@dataclass
class DesignResult:
    core: str
    material: str
    windings: list[WindingInfo]
    air_gap_mm: float
    # ... more fields

    @classmethod
    def from_mas(cls, mas: dict) -> "DesignResult":
        # Parse MAS format into structured result
        return cls(...)
        """.strip(),
    ),

    "template_method": PatternInfo(
        name="Template Method",
        category="behavioral",
        description="""
The Template Method pattern defines the skeleton of an algorithm in a base class,
with concrete steps implemented by subclasses. Abstract methods ensure subclasses
provide required implementations.
        """.strip(),
        use_case="""
Used in TopologyBuilder base class. The solve() and to_mas() methods define
the algorithm structure, while subclasses implement _generate_operating_points()
and _generate_design_requirements().
        """.strip(),
        example_location="api/design.py",
        example_code="""
class TopologyBuilder(ABC):
    def to_mas(self) -> dict:
        # Template method - defines structure
        return {
            "designRequirements": self._generate_design_requirements(),
            "operatingPoints": self._generate_operating_points()
        }

    @abstractmethod
    def _generate_operating_points(self) -> list[dict]:
        # Must be implemented by subclasses
        ...
        """.strip(),
    ),

    "strategy": PatternInfo(
        name="Strategy",
        category="behavioral",
        description="""
The Strategy pattern defines a family of algorithms and makes them interchangeable.
The algorithm can be selected at runtime without changing the clients that use it.
        """.strip(),
        use_case="""
Used for loss calculation models (IGSE, STEINMETZ, etc.) where different
algorithms can be selected for core loss calculation.
        """.strip(),
        example_location="PyOpenMagnetics bindings",
        example_code="""
# Different loss calculation strategies
models = {
    "coreLosses": "IGSE",      # or "STEINMETZ", "MSE", etc.
    "reluctance": "ZHANG",
    "coreTemperature": "MANIKTALA"
}

losses = PyOpenMagnetics.calculate_core_losses(
    core, coil, inputs, models
)
        """.strip(),
    ),

    "facade": PatternInfo(
        name="Facade",
        category="structural",
        description="""
The Facade pattern provides a simplified interface to a complex subsystem.
It wraps a complicated system with a simpler interface.
        """.strip(),
        use_case="""
The MCP tools module acts as a facade over the Design API and PyOpenMagnetics,
providing simple functions for AI assistants to use.
        """.strip(),
        example_location="api/mcp/tools.py",
        example_code="""
def design_magnetic(
    topology: str,
    vin_min: float,
    vin_max: float,
    outputs: list[dict],
    frequency_hz: float,
    **kwargs
) -> dict:
    # Facade hides complexity of Design API
    builder = Design.flyback()
    builder.vin_ac(vin_min, vin_max)
    # ... setup
    return {"designs": results}
        """.strip(),
    ),

    "adapter": PatternInfo(
        name="Adapter",
        category="structural",
        description="""
The Adapter pattern converts the interface of a class into another interface
that clients expect. It lets classes work together that couldn't otherwise.
        """.strip(),
        use_case="""
The FEMMT bridge acts as an adapter, converting PyOpenMagnetics DesignResult
format into FEMMT's expected input format.
        """.strip(),
        example_location="api/bridges/femmt.py",
        example_code="""
class FEMMTExporter:
    # Adapts DesignResult to FEMMT format
    CORE_TYPE_MAP = {"E": "E", "ETD": "E", "PQ": "PQ", ...}
    MATERIAL_MAP = {"3C95": "N95", "N87": "N87", ...}

    def export(self, design: DesignResult) -> str:
        # Convert PyOpenMagnetics format to FEMMT script
        ...
        """.strip(),
    ),
}


def get_pattern(name: str) -> Optional[PatternInfo]:
    """
    Get information about a specific design pattern.

    Args:
        name: Pattern name (e.g., "fluent_builder")

    Returns:
        PatternInfo or None if not found
    """
    return PATTERNS.get(name)


def list_patterns() -> list[str]:
    """List all documented patterns."""
    return list(PATTERNS.keys())


def patterns_by_category(category: str) -> list[PatternInfo]:
    """
    Get all patterns in a category.

    Args:
        category: "creational", "structural", or "behavioral"

    Returns:
        List of matching PatternInfo objects
    """
    return [p for p in PATTERNS.values() if p.category == category]


def generate_pattern_docs() -> str:
    """Generate markdown documentation for all patterns."""
    lines = ["# Design Patterns in PyOpenMagnetics", ""]

    for category in ["creational", "structural", "behavioral"]:
        patterns = patterns_by_category(category)
        if patterns:
            lines.append(f"## {category.title()} Patterns")
            lines.append("")

            for p in patterns:
                lines.append(f"### {p.name}")
                lines.append("")
                lines.append(p.description)
                lines.append("")
                lines.append(f"**Use Case:** {p.use_case}")
                lines.append("")
                lines.append(f"**Example Location:** `{p.example_location}`")
                lines.append("")
                lines.append("```python")
                lines.append(p.example_code)
                lines.append("```")
                lines.append("")

    return "\n".join(lines)
