"""
PyOpenMagnetics Python API - Fluent design interface.

Example:
    from api.design import Design
    results = Design.buck().vin(12,24).vout(5).iout(3).fsw(500e3).solve()
"""

from .design import Design
from .results import DesignResult, WindingInfo, BOMItem

__all__ = ["Design", "DesignResult", "WindingInfo", "BOMItem"]
