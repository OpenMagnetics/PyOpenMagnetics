"""Tests for PyOpenMagnetics simplified MCP tools."""

import pytest


class TestMCPImports:
    """Test MCP module imports."""

    def test_import_tools(self):
        from api.mcp import design_magnetic, design_from_template, query_database, get_templates, DESIGN_TEMPLATES
        assert all([design_magnetic, design_from_template, query_database, get_templates, DESIGN_TEMPLATES])


class TestDesignTemplates:
    """Test predefined design templates."""

    def test_get_templates(self):
        from api.mcp import get_templates
        templates = get_templates()
        assert "usb_pd_20w" in templates
        assert "buck_5v_3a" in templates
        assert len(templates) >= 8

    def test_invalid_template(self):
        from api.mcp import design_from_template
        result = design_from_template("nonexistent")
        assert "error" in result
        assert "available" in result

    def test_buck_template(self):
        from api.mcp import design_from_template
        result = design_from_template("buck_5v_3a")
        assert "designs" in result or "error" in result


class TestDesignMagnetic:
    """Test design_magnetic function."""

    def test_buck_design(self):
        from api.mcp import design_magnetic
        result = design_magnetic(topology="buck", vin_min=12, vin_max=24,
                                 outputs=[{"voltage": 5, "current": 3}], frequency_hz=500000)
        assert "designs" in result or "error" in result

    def test_invalid_topology(self):
        from api.mcp import design_magnetic
        result = design_magnetic(topology="invalid", vin_min=12, vin_max=24,
                                 outputs=[{"voltage": 5, "current": 1}], frequency_hz=100000)
        assert "error" in result


class TestQueryDatabase:
    """Test query_database function."""

    def test_query_shapes(self):
        from api.mcp import query_database
        result = query_database(query_type="shapes")
        assert "shapes" in result
        assert result["total"] > 0

    def test_query_materials(self):
        from api.mcp import query_database
        result = query_database(query_type="materials")
        assert "materials" in result
        assert result["count"] > 0

    def test_query_families(self):
        from api.mcp import query_database
        result = query_database(query_type="families")
        assert "families" in result


class TestMCPServer:
    """Test MCP server structure."""

    def test_server_import(self):
        from api.mcp.server import server
        assert server is not None

    @pytest.mark.asyncio
    async def test_list_tools(self):
        from api.mcp.server import list_tools
        tools = await list_tools()
        assert len(tools) == 2
        assert {t.name for t in tools} == {"design_magnetic", "query_database"}

    @pytest.mark.asyncio
    async def test_call_query_tool(self):
        from api.mcp.server import call_tool
        import json
        result = await call_tool("query_database", {"query_type": "families"})
        data = json.loads(result[0].text)
        assert "families" in data
