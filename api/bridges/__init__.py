"""
Bridges to external tools and simulation software.

- femmt: Export to FEMMT (FEM Magnetics Toolbox) for FEM simulation
"""

from .femmt import export_to_femmt, FEMMTExporter

__all__ = ["export_to_femmt", "FEMMTExporter"]
