"""
Simplified MCP Server for PyOpenMagnetics.

Two tools + templates for common designs.

Run: python -m api.mcp.server
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

from .tools import design_magnetic, query_database, design_from_template, get_templates

server = Server("pyopenmagnetics")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="design_magnetic",
            description="Design transformer/inductor. Topologies: flyback, buck, boost, forward, llc, inductor. Or use template: " + ", ".join(get_templates().keys()),
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string", "description": "Template name (usb_pd_20w, buck_5v_3a, etc.)"},
                    "topology": {"type": "string", "enum": ["flyback", "buck", "boost", "forward", "llc", "inductor"]},
                    "vin_min": {"type": "number"},
                    "vin_max": {"type": "number"},
                    "vin_is_ac": {"type": "boolean", "default": False},
                    "outputs": {"type": "array", "items": {"type": "object"}},
                    "frequency_hz": {"type": "number", "default": 100000},
                    "inductance": {"type": "number", "description": "For inductor (Henries)"},
                    "current_dc": {"type": "number"},
                    "current_ac_pp": {"type": "number"}
                }
            }
        ),
        Tool(
            name="query_database",
            description="Query cores/materials/wires. Types: shapes, materials, wires, families, shape_info, material_info",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_type": {"type": "string", "enum": ["shapes", "materials", "wires", "families", "shape_info", "material_info"]},
                    "name": {"type": "string", "description": "For shape_info/material_info"},
                    "family": {"type": "string", "description": "Filter shapes (ETD, E, PQ)"},
                    "manufacturer": {"type": "string", "description": "Filter materials (Ferroxcube, TDK)"}
                },
                "required": ["query_type"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "design_magnetic":
            if "template" in arguments:
                result = design_from_template(arguments["template"], arguments.get("max_results", 3))
            else:
                result = design_magnetic(**{k: v for k, v in arguments.items() if k != "template"})
        elif name == "query_database":
            result = query_database(**arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
