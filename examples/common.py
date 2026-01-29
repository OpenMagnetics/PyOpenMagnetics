"""
Common utilities for PyOpenMagnetics examples.

Provides standardized output generation for all examples.
"""

from pathlib import Path
from typing import List, Any, Optional, Dict

# Standard configuration for all examples
DEFAULT_MAX_RESULTS = 50
OUTPUT_BASE_DIR = Path(__file__).parent / "_output"


def get_output_dir(example_name: str) -> str:
    """Get standardized output directory for an example.

    Args:
        example_name: Short name like "usb_pd_65w" or "buck_inductor"

    Returns:
        Path string to output directory
    """
    output_dir = OUTPUT_BASE_DIR / example_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


def generate_example_report(
    results: List[Any],
    example_name: str,
    title: str,
    specs: Optional[Dict[str, Any]] = None,
    verbose: bool = True
) -> Optional[str]:
    """
    Generate standardized reports for an example.

    Generates:
    - design_report.png: Main dashboard with Pareto front
    - pareto_detailed.png: Detailed Pareto analysis
    - parallel_coordinates.png: Multi-objective comparison
    - heatmap.png: Design characteristics
    - report_summary.json: Statistics

    Args:
        results: List of DesignResult objects
        example_name: Short name for output directory
        title: Report title
        specs: Optional specifications dict
        verbose: Print progress

    Returns:
        Path to output directory, or None if report generation failed
    """
    if not results:
        if verbose:
            print("[No results to generate report]")
        return None

    output_dir = get_output_dir(example_name)

    try:
        from api.report import generate_design_report

        if verbose:
            print(f"\nGenerating reports for {len(results)} designs...")

        generate_design_report(
            results,
            output_dir,
            title=title,
            specs=specs,
            verbose=verbose
        )

        if verbose:
            print(f"\nReports saved to: {output_dir}/")
            print("  - design_report.png (main dashboard with Pareto front)")
            print("  - pareto_detailed.png (loss vs volume analysis)")
            print("  - parallel_coordinates.png (multi-objective comparison)")
            print("  - heatmap.png (design characteristics)")
            print("  - report_summary.json (statistics)")

        return output_dir

    except ImportError as e:
        if verbose:
            print(f"\n[Visual reports skipped - matplotlib not installed: {e}]")
        return None
    except Exception as e:
        if verbose:
            print(f"\n[Report generation failed: {e}]")
        return None


def print_results_summary(results: List[Any], max_display: int = 10):
    """Print a summary of design results.

    Args:
        results: List of DesignResult objects
        max_display: Maximum number of results to display in detail
    """
    if not results:
        print("No designs found.")
        return

    print(f"\nFound {len(results)} designs (showing top {min(len(results), max_display)}):\n")

    for i, r in enumerate(results[:max_display], 1):
        print(f"Design #{i}: {r.core} / {r.material}")
        print(f"  Primary:    {r.primary_turns}T, {r.primary_wire}")
        if hasattr(r, 'secondary_turns') and r.secondary_turns:
            print(f"  Secondary:  {r.secondary_turns}T")
        print(f"  Air gap:    {r.air_gap_mm:.2f} mm")
        print(f"  Core loss:  {r.core_loss_w:.3f} W")
        print(f"  Cu loss:    {r.copper_loss_w:.3f} W")
        print(f"  Total loss: {r.total_loss_w:.3f} W")
        if r.temp_rise_c:
            print(f"  Temp rise:  {r.temp_rise_c:.1f} K")
        print()

    if len(results) > max_display:
        print(f"  ... and {len(results) - max_display} more designs")

    # Statistics
    total_losses = [r.total_loss_w for r in results]
    print(f"\nStatistics ({len(results)} designs):")
    print(f"  Min loss:  {min(total_losses):.3f} W")
    print(f"  Max loss:  {max(total_losses):.3f} W")
    print(f"  Avg loss:  {sum(total_losses)/len(total_losses):.3f} W")
