"""Tests for architect tools."""

import pytest
import os

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAnalyzer:
    """Test code analyzer."""

    def test_import_analyzer(self):
        from api.architect import analyze_module, get_module_metrics
        assert callable(analyze_module)
        assert callable(get_module_metrics)

    def test_analyze_module(self):
        from api.architect.analyzer import analyze_module
        # Analyze a real file
        metrics = analyze_module(os.path.join(PROJECT_ROOT, "api/design.py"))

        assert metrics.name == "design"
        assert metrics.line_count > 0
        assert metrics.class_count > 0  # Should have builder classes
        assert metrics.function_count >= 0

    def test_analyze_module_classes(self):
        from api.architect.analyzer import analyze_module
        metrics = analyze_module(os.path.join(PROJECT_ROOT, "api/design.py"))

        # Should find TopologyBuilder and its subclasses
        class_names = [c.name for c in metrics.classes]
        assert "TopologyBuilder" in class_names or "Design" in class_names

    def test_get_module_metrics(self):
        from api.architect.analyzer import get_module_metrics
        metrics = get_module_metrics(os.path.join(PROJECT_ROOT, "api/design.py"))

        assert "lines" in metrics
        assert "classes" in metrics
        assert "functions" in metrics
        assert metrics["lines"] > 0

    def test_suggest_refactorings(self):
        from api.architect.analyzer import suggest_refactorings
        suggestions = suggest_refactorings(os.path.join(PROJECT_ROOT, "api/design.py"))

        assert isinstance(suggestions, list)
        # May or may not have suggestions depending on code quality

    def test_analyze_nonexistent_file(self):
        from api.architect.analyzer import analyze_module
        with pytest.raises(FileNotFoundError):
            analyze_module("/nonexistent/path.py")


class TestPatterns:
    """Test pattern library."""

    def test_import_patterns(self):
        from api.architect import PATTERNS, get_pattern, list_patterns
        assert PATTERNS is not None
        assert callable(get_pattern)
        assert callable(list_patterns)

    def test_list_patterns(self):
        from api.architect.patterns import list_patterns
        patterns = list_patterns()

        assert "fluent_builder" in patterns
        assert "factory_method" in patterns
        assert "dataclass_result" in patterns

    def test_get_pattern(self):
        from api.architect.patterns import get_pattern
        pattern = get_pattern("fluent_builder")

        assert pattern is not None
        assert pattern.name == "Fluent Builder"
        assert pattern.category == "creational"
        assert "Design.flyback()" in pattern.example_code

    def test_get_nonexistent_pattern(self):
        from api.architect.patterns import get_pattern
        pattern = get_pattern("nonexistent_pattern")
        assert pattern is None

    def test_patterns_by_category(self):
        from api.architect.patterns import patterns_by_category

        creational = patterns_by_category("creational")
        assert len(creational) >= 2  # fluent_builder, factory_method

        structural = patterns_by_category("structural")
        assert len(structural) >= 1

    def test_generate_pattern_docs(self):
        from api.architect.patterns import generate_pattern_docs
        docs = generate_pattern_docs()

        assert "# Design Patterns" in docs
        assert "Fluent Builder" in docs
        assert "```python" in docs


class TestDocsGenerator:
    """Test documentation generator."""

    def test_import_docs_generator(self):
        from api.architect import generate_api_docs, generate_architecture_diagram
        assert callable(generate_api_docs)
        assert callable(generate_architecture_diagram)

    def test_generate_api_docs(self):
        from api.architect.docs_generator import generate_api_docs
        docs = generate_api_docs(os.path.join(PROJECT_ROOT, "api"))

        assert "# api API Reference" in docs
        assert "| Module |" in docs
        assert "design" in docs.lower()

    def test_generate_mermaid_diagram(self):
        from api.architect.docs_generator import generate_architecture_diagram
        diagram = generate_architecture_diagram(
            os.path.join(PROJECT_ROOT, "api"),
            format="mermaid"
        )

        assert "```mermaid" in diagram
        assert "graph TD" in diagram

    def test_generate_ascii_diagram(self):
        from api.architect.docs_generator import generate_architecture_diagram
        diagram = generate_architecture_diagram(
            os.path.join(PROJECT_ROOT, "api"),
            format="ascii"
        )

        assert "Architecture:" in diagram
        assert ".py" in diagram

    def test_generate_module_summary(self):
        from api.architect.docs_generator import generate_module_summary
        summary = generate_module_summary(os.path.join(PROJECT_ROOT, "api/design.py"))

        assert "# Module: design" in summary
        assert "**Path:**" in summary
        assert "**Lines:**" in summary

    def test_generate_dependency_graph(self):
        from api.architect.docs_generator import generate_dependency_graph
        graph = generate_dependency_graph(os.path.join(PROJECT_ROOT, "api"))

        assert "nodes" in graph
        assert "edges" in graph
        assert isinstance(graph["nodes"], list)
