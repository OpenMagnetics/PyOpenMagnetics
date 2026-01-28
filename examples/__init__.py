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
"""

from . import consumer
from . import automotive
from . import industrial
from . import telecom
from . import advanced
from .common import DEFAULT_MAX_RESULTS, get_output_dir, generate_example_report, print_results_summary

__all__ = [
    "consumer",
    "automotive",
    "industrial",
    "telecom",
    "advanced",
    "DEFAULT_MAX_RESULTS",
    "get_output_dir",
    "generate_example_report",
    "print_results_summary",
]
