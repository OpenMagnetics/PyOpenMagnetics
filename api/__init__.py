"""
PyOpenMagnetics Python API - Fluent design interface.

Example:
    from api.design import Design
    results = Design.buck().vin(12,24).vout(5).iout(3).fsw(500e3).solve()

Optimization:
    from api.optimization import NSGAOptimizer
    optimizer = NSGAOptimizer(objectives=["mass", "total_loss"])
    optimizer.add_variable("turns", range=(20, 60))
    pareto_front = optimizer.run()
"""

from .design import Design
from .results import DesignResult, WindingInfo, BOMItem
from .optimization import NSGAOptimizer, create_inductor_optimizer, ParetoFront

__all__ = [
    "Design",
    "DesignResult",
    "WindingInfo",
    "BOMItem",
    "NSGAOptimizer",
    "create_inductor_optimizer",
    "ParetoFront",
]
