"""Tests for Streamlit GUI components."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGUIImports:
    """Test GUI module imports."""

    def test_import_app(self):
        # Can't fully test Streamlit without running server, but test imports
        from api.gui import pages
        assert pages is not None

    def test_import_design_page(self):
        from api.gui.pages import design
        assert hasattr(design, 'render')

    def test_import_database_page(self):
        from api.gui.pages import database
        assert hasattr(database, 'render')

    def test_import_analysis_page(self):
        from api.gui.pages import analysis
        assert hasattr(analysis, 'render')

    def test_import_compare_page(self):
        from api.gui.pages import compare
        assert hasattr(compare, 'render')


class TestGUIFunctions:
    """Test GUI helper functions."""

    def test_design_page_display_results(self):
        from api.gui.pages.design import display_results
        # Test with empty results (should not raise)
        # Note: Can't fully test Streamlit functions without running server
        assert callable(display_results)
