"""
Code Analyzer for PyOpenMagnetics.

Tools for analyzing Python modules and suggesting improvements.
"""

import ast
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class FunctionMetrics:
    """Metrics for a single function."""
    name: str
    line_number: int
    line_count: int
    parameter_count: int
    has_docstring: bool
    has_type_hints: bool
    complexity: int = 0  # Cyclomatic complexity estimate


@dataclass
class ClassMetrics:
    """Metrics for a single class."""
    name: str
    line_number: int
    line_count: int
    method_count: int
    has_docstring: bool
    base_classes: list[str] = field(default_factory=list)
    methods: list[FunctionMetrics] = field(default_factory=list)


@dataclass
class ModuleMetrics:
    """Metrics for a Python module."""
    path: str
    name: str
    line_count: int
    import_count: int
    function_count: int
    class_count: int
    has_docstring: bool
    functions: list[FunctionMetrics] = field(default_factory=list)
    classes: list[ClassMetrics] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


class CodeAnalyzer(ast.NodeVisitor):
    """AST-based code analyzer."""

    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.functions: list[FunctionMetrics] = []
        self.classes: list[ClassMetrics] = []
        self.imports: list[str] = []
        self._current_class: Optional[ClassMetrics] = None

    def analyze(self) -> dict:
        """Analyze the source code."""
        tree = ast.parse(self.source)
        self.visit(tree)
        return {
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
        }

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Count lines
        end_line = node.end_lineno or node.lineno
        line_count = end_line - node.lineno + 1

        # Check docstring
        has_docstring = (
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant)
        )

        # Check type hints
        has_type_hints = node.returns is not None or any(
            arg.annotation is not None for arg in node.args.args
        )

        # Estimate cyclomatic complexity (simplified)
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        func_metrics = FunctionMetrics(
            name=node.name,
            line_number=node.lineno,
            line_count=line_count,
            parameter_count=len(node.args.args),
            has_docstring=has_docstring,
            has_type_hints=has_type_hints,
            complexity=complexity
        )

        if self._current_class:
            self._current_class.methods.append(func_metrics)
        else:
            self.functions.append(func_metrics)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        # Treat async functions same as regular
        self.visit_FunctionDef(node)  # type: ignore

    def visit_ClassDef(self, node: ast.ClassDef):
        # Count lines
        end_line = node.end_lineno or node.lineno
        line_count = end_line - node.lineno + 1

        # Check docstring
        has_docstring = (
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant)
        )

        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)

        class_metrics = ClassMetrics(
            name=node.name,
            line_number=node.lineno,
            line_count=line_count,
            method_count=0,
            has_docstring=has_docstring,
            base_classes=bases,
        )

        self._current_class = class_metrics
        self.generic_visit(node)
        class_metrics.method_count = len(class_metrics.methods)
        self._current_class = None

        self.classes.append(class_metrics)


def analyze_module(module_path: str) -> ModuleMetrics:
    """
    Analyze a Python module file.

    Args:
        module_path: Path to the Python file

    Returns:
        ModuleMetrics with detailed analysis

    Example:
        >>> metrics = analyze_module("api/design.py")
        >>> print(f"Classes: {metrics.class_count}, Functions: {metrics.function_count}")
    """
    path = Path(module_path)
    if not path.exists():
        raise FileNotFoundError(f"Module not found: {module_path}")

    source = path.read_text()
    lines = source.split('\n')

    # Check module docstring
    has_docstring = False
    try:
        tree = ast.parse(source)
        if tree.body and isinstance(tree.body[0], ast.Expr):
            if isinstance(tree.body[0].value, ast.Constant):
                has_docstring = True
    except SyntaxError:
        pass

    analyzer = CodeAnalyzer(source)
    try:
        analyzer.analyze()
    except SyntaxError as e:
        return ModuleMetrics(
            path=str(path),
            name=path.stem,
            line_count=len(lines),
            import_count=0,
            function_count=0,
            class_count=0,
            has_docstring=False,
        )

    return ModuleMetrics(
        path=str(path),
        name=path.stem,
        line_count=len(lines),
        import_count=len(analyzer.imports),
        function_count=len(analyzer.functions),
        class_count=len(analyzer.classes),
        has_docstring=has_docstring,
        functions=analyzer.functions,
        classes=analyzer.classes,
        imports=analyzer.imports,
    )


def analyze_package(package_path: str) -> list[ModuleMetrics]:
    """
    Analyze all Python modules in a package.

    Args:
        package_path: Path to the package directory

    Returns:
        List of ModuleMetrics for each .py file
    """
    path = Path(package_path)
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {package_path}")

    results = []
    for py_file in path.rglob("*.py"):
        try:
            results.append(analyze_module(str(py_file)))
        except Exception:
            pass

    return results


def get_module_metrics(module_path: str) -> dict:
    """
    Get simplified metrics dict for a module.

    Returns:
        Dict with summary metrics
    """
    metrics = analyze_module(module_path)
    return {
        "path": metrics.path,
        "name": metrics.name,
        "lines": metrics.line_count,
        "imports": metrics.import_count,
        "functions": metrics.function_count,
        "classes": metrics.class_count,
        "has_docstring": metrics.has_docstring,
        "total_methods": sum(c.method_count for c in metrics.classes),
        "avg_function_complexity": (
            sum(f.complexity for f in metrics.functions) / len(metrics.functions)
            if metrics.functions else 0
        ),
    }


def suggest_refactorings(module_path: str) -> list[dict]:
    """
    Suggest potential refactorings for a module.

    Args:
        module_path: Path to analyze

    Returns:
        List of suggestion dicts with type, location, and description
    """
    metrics = analyze_module(module_path)
    suggestions = []

    # Check for missing docstrings
    if not metrics.has_docstring:
        suggestions.append({
            "type": "missing_docstring",
            "location": f"{metrics.name}:1",
            "description": "Module is missing a docstring",
            "severity": "info"
        })

    for func in metrics.functions:
        if not func.has_docstring:
            suggestions.append({
                "type": "missing_docstring",
                "location": f"{metrics.name}:{func.line_number}",
                "description": f"Function '{func.name}' is missing a docstring",
                "severity": "info"
            })

        if func.complexity > 10:
            suggestions.append({
                "type": "high_complexity",
                "location": f"{metrics.name}:{func.line_number}",
                "description": f"Function '{func.name}' has high complexity ({func.complexity})",
                "severity": "warning"
            })

        if func.line_count > 50:
            suggestions.append({
                "type": "long_function",
                "location": f"{metrics.name}:{func.line_number}",
                "description": f"Function '{func.name}' is long ({func.line_count} lines)",
                "severity": "info"
            })

        if func.parameter_count > 5:
            suggestions.append({
                "type": "many_parameters",
                "location": f"{metrics.name}:{func.line_number}",
                "description": f"Function '{func.name}' has many parameters ({func.parameter_count})",
                "severity": "info"
            })

    for cls in metrics.classes:
        if not cls.has_docstring:
            suggestions.append({
                "type": "missing_docstring",
                "location": f"{metrics.name}:{cls.line_number}",
                "description": f"Class '{cls.name}' is missing a docstring",
                "severity": "info"
            })

        if cls.method_count > 20:
            suggestions.append({
                "type": "large_class",
                "location": f"{metrics.name}:{cls.line_number}",
                "description": f"Class '{cls.name}' has many methods ({cls.method_count})",
                "severity": "info"
            })

    return suggestions
