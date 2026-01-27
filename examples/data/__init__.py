"""
Pre-defined magnetic components and simulation results.

This module provides access to example magnetic component definitions
and pre-computed simulation results for testing and demonstration.
"""

import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent


def load_bdc6128_inductor() -> dict:
    """
    Load BDC6128 boost inductor definition.

    This is a real-world inductor design used in high-power DC-DC converters,
    providing a reference for validation and testing.

    Returns:
        dict: MAS-format magnetic component definition
    """
    with open(DATA_DIR / "bdc6128_inductor.json") as f:
        return json.load(f)


def load_precomputed_mas(index: int = 1) -> Optional[dict]:
    """
    Load pre-computed MAS simulation result.

    These are cached results from inductor simulations across different
    operating points, useful for testing without running full simulations.

    Args:
        index: Result index (1, 11, 21, 31, or 41)

    Returns:
        dict: MAS simulation result, or None if not found
    """
    result_file = DATA_DIR / "precomputed" / f"mas_{index}.json"
    if result_file.exists():
        with open(result_file) as f:
            return json.load(f)
    return None


def list_precomputed_results() -> list[str]:
    """
    List available pre-computed result files.

    Returns:
        list[str]: List of available result file names
    """
    precomputed_dir = DATA_DIR / "precomputed"
    if precomputed_dir.exists():
        return [f.name for f in precomputed_dir.glob("*.json")]
    return []


def get_data_path(filename: str) -> Path:
    """
    Get the full path to a data file.

    Args:
        filename: Name of the data file

    Returns:
        Path: Full path to the data file
    """
    return DATA_DIR / filename
