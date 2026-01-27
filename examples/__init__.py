"""
PyOpenMagnetics Design Examples

Examples organized by application domain:
- consumer: USB chargers, laptop adapters
- automotive: DC-DC converters, gate drivers
- industrial: DIN rail PSUs, medical, VFD
- telecom: Rectifiers, PoE

Each example demonstrates the fluent Design API:
    from api.design import Design
    results = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3).solve()
"""

from . import consumer
from . import automotive
from . import industrial
from . import telecom

__all__ = ["consumer", "automotive", "industrial", "telecom"]
