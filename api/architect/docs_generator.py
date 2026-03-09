"""
Documentation Generator for PyOpenMagnetics.

Tools for generating API documentation and architecture diagrams.
"""

from pathlib import Path
from typing import Optional
from .analyzer import analyze_module, analyze_package, ModuleMetrics


def generate_api_docs(package_path: str, output_path: Optional[str] = None) -> str:
    """
    Generate API documentation for a Python package.

    Args:
        package_path: Path to the package directory
        output_path: Optional path to write the documentation

    Returns:
        Markdown documentation string
    """
    modules = analyze_package(package_path)
    lines = []

    # Header
    package_name = Path(package_path).name
    lines.append(f"# {package_name} API Reference")
    lines.append("")
    lines.append("Auto-generated API documentation.")
    lines.append("")

    # Summary table
    lines.append("## Module Summary")
    lines.append("")
    lines.append("| Module | Classes | Functions | Lines |")
    lines.append("|--------|---------|-----------|-------|")
    for m in sorted(modules, key=lambda x: x.path):
        rel_path = Path(m.path).relative_to(package_path) if package_path in m.path else m.path
        lines.append(f"| {rel_path} | {m.class_count} | {m.function_count} | {m.line_count} |")
    lines.append("")

    # Detailed documentation
    for m in sorted(modules, key=lambda x: x.path):
        rel_path = Path(m.path).relative_to(package_path) if package_path in m.path else m.path
        lines.append(f"## {rel_path}")
        lines.append("")

        if m.classes:
            lines.append("### Classes")
            lines.append("")
            for cls in m.classes:
                lines.append(f"#### `{cls.name}`")
                if cls.base_classes:
                    lines.append(f"*Inherits from: {', '.join(cls.base_classes)}*")
                lines.append("")
                lines.append(f"- Line: {cls.line_number}")
                lines.append(f"- Methods: {cls.method_count}")
                lines.append("")

                if cls.methods:
                    lines.append("**Methods:**")
                    lines.append("")
                    for method in cls.methods:
                        hint = " (typed)" if method.has_type_hints else ""
                        lines.append(f"- `{method.name}({method.parameter_count} params)`{hint}")
                    lines.append("")

        if m.functions:
            lines.append("### Functions")
            lines.append("")
            for func in m.functions:
                hint = " (typed)" if func.has_type_hints else ""
                lines.append(f"- `{func.name}({func.parameter_count} params)`{hint} - Line {func.line_number}")
            lines.append("")

    doc_text = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(doc_text)

    return doc_text


def generate_architecture_diagram(package_path: str, format: str = "mermaid") -> str:
    """
    Generate an architecture diagram for a package.

    Args:
        package_path: Path to the package directory
        format: Output format ("mermaid" or "ascii")

    Returns:
        Diagram string
    """
    modules = analyze_package(package_path)

    if format == "mermaid":
        return _generate_mermaid_diagram(modules, package_path)
    else:
        return _generate_ascii_diagram(modules, package_path)


def _generate_mermaid_diagram(modules: list[ModuleMetrics], package_path: str) -> str:
    """Generate Mermaid.js diagram."""
    lines = ["```mermaid", "graph TD"]

    # Group modules by directory
    dirs = {}
    for m in modules:
        rel_path = Path(m.path).relative_to(package_path) if package_path in m.path else Path(m.path)
        parent = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
        if parent not in dirs:
            dirs[parent] = []
        dirs[parent].append(m)

    # Create subgraphs for directories
    for dir_name, dir_modules in dirs.items():
        if dir_name != "root":
            safe_name = dir_name.replace("/", "_").replace(".", "_")
            lines.append(f"    subgraph {safe_name}[{dir_name}]")

        for m in dir_modules:
            node_id = m.name.replace(".", "_")
            label = f"{m.name}<br/>{m.class_count}C {m.function_count}F"
            lines.append(f"        {node_id}[{label}]")

        if dir_name != "root":
            lines.append("    end")

    # Add dependency edges based on imports
    for m in modules:
        src = m.name.replace(".", "_")
        for imp in m.imports:
            # Only show internal dependencies
            for other in modules:
                if other.name in imp and other.name != m.name:
                    dst = other.name.replace(".", "_")
                    lines.append(f"    {src} --> {dst}")
                    break

    lines.append("```")
    return "\n".join(lines)


def _generate_ascii_diagram(modules: list[ModuleMetrics], package_path: str) -> str:
    """Generate ASCII diagram."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  Architecture: {Path(package_path).name}")
    lines.append("=" * 60)
    lines.append("")

    # Group by directory
    dirs = {}
    for m in modules:
        rel_path = Path(m.path).relative_to(package_path) if package_path in m.path else Path(m.path)
        parent = str(rel_path.parent) if rel_path.parent != Path(".") else "."
        if parent not in dirs:
            dirs[parent] = []
        dirs[parent].append(m)

    for dir_name in sorted(dirs.keys()):
        dir_modules = dirs[dir_name]

        if dir_name != ".":
            lines.append(f"  [{dir_name}/]")

        for m in dir_modules:
            prefix = "    " if dir_name != "." else "  "
            stats = f"({m.class_count}C, {m.function_count}F, {m.line_count}L)"
            lines.append(f"{prefix}+-- {m.name}.py {stats}")

        lines.append("")

    return "\n".join(lines)


def generate_dependency_graph(package_path: str) -> dict:
    """
    Generate a dependency graph for the package.

    Returns:
        Dict with nodes and edges for graph visualization
    """
    modules = analyze_package(package_path)

    nodes = []
    edges = []

    for m in modules:
        nodes.append({
            "id": m.name,
            "label": m.name,
            "classes": m.class_count,
            "functions": m.function_count,
            "lines": m.line_count
        })

        for imp in m.imports:
            for other in modules:
                if other.name in imp and other.name != m.name:
                    edges.append({
                        "source": m.name,
                        "target": other.name
                    })
                    break

    return {"nodes": nodes, "edges": edges}


def generate_module_summary(module_path: str) -> str:
    """
    Generate a summary for a single module.

    Args:
        module_path: Path to the Python file

    Returns:
        Markdown summary string
    """
    m = analyze_module(module_path)
    lines = []

    lines.append(f"# Module: {m.name}")
    lines.append("")
    lines.append(f"**Path:** `{m.path}`")
    lines.append(f"**Lines:** {m.line_count}")
    lines.append(f"**Has Docstring:** {'Yes' if m.has_docstring else 'No'}")
    lines.append("")

    if m.classes:
        lines.append("## Classes")
        lines.append("")
        for cls in m.classes:
            bases = f" ({', '.join(cls.base_classes)})" if cls.base_classes else ""
            lines.append(f"### {cls.name}{bases}")
            lines.append(f"- **Line:** {cls.line_number}")
            lines.append(f"- **Methods:** {cls.method_count}")
            if cls.methods:
                lines.append("")
                for method in cls.methods:
                    lines.append(f"  - `{method.name}()`")
            lines.append("")

    if m.functions:
        lines.append("## Functions")
        lines.append("")
        for func in m.functions:
            lines.append(f"### `{func.name}()`")
            lines.append(f"- **Line:** {func.line_number}")
            lines.append(f"- **Parameters:** {func.parameter_count}")
            lines.append(f"- **Complexity:** {func.complexity}")
            lines.append("")

    return "\n".join(lines)
