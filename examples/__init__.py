"""
PyOpenMagnetics Design Examples

Examples organized by application domain:
- consumer: USB chargers, laptop adapters
- automotive: DC-DC converters, gate drivers, EV applications
- industrial: DIN rail PSUs, medical, VFD, boost inductors
- telecom: Rectifiers, PoE
- advanced: Multi-objective optimization, custom simulation

Each example demonstrates the fluent Design API:
    from api.design import Design
    results = Design.flyback().vin_ac(85, 265).output(12, 5).fsw(100e3).solve()

Data files:
    from examples.data import load_bdc6128_inductor
    magnetic = load_bdc6128_inductor()
"""

from . import consumer
from . import automotive
from . import industrial
from . import telecom
from . import advanced
from . import data

__all__ = ["consumer", "automotive", "industrial", "telecom", "advanced", "data"]
