"""
MCP Server for PyOpenMagnetics.

Two tools + templates for common designs:
- design_magnetic: Design transformer/inductor (or use templates)
- query_database: Query cores, materials, wires

Templates (work offline): usb_pd_20w, usb_pd_65w, buck_5v_3a, buck_3v3_2a,
                          boost_5v_1a, led_driver_12v, poe_12v_1a, filter_100uh
"""

from .tools import design_magnetic, design_from_template, query_database, get_templates, DESIGN_TEMPLATES

__all__ = ["design_magnetic", "design_from_template", "query_database", "get_templates", "DESIGN_TEMPLATES"]
