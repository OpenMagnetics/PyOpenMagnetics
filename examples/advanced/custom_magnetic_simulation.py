"""
Custom Magnetic Component Simulation

Application: Analyzing inductor design parameter sweeps
Demonstrates: Parameter sweeping, loss analysis, optimization

This example shows how to:
1. Understand turns count vs loss tradeoffs
2. Analyze core vs winding losses
3. Find optimal turns for minimum total loss
4. Understand frequency effects on skin depth

Use case: High-power boost inductor for EV charger applications.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from examples.common import get_output_dir


def analyze_turns_sweep():
    """Sweep number of turns and analyze loss tradeoffs."""
    print("=" * 70)
    print("CUSTOM MAGNETIC SIMULATION - TURNS SWEEP ANALYSIS")
    print("Component: High-Power Boost Inductor")
    print("=" * 70)

    # Simulated results based on typical inductor behavior
    # These follow the physical relationships:
    # - Core loss ~ 1/N^beta (decreases with turns as B decreases)
    # - Winding loss ~ N * R (increases with turns due to longer wire)

    results = [
        {"turns": 10, "inductance_uH": 50.0, "core_loss_W": 45.0, "winding_loss_W": 8.0, "total_loss_W": 53.0},
        {"turns": 20, "inductance_uH": 200.0, "core_loss_W": 12.0, "winding_loss_W": 15.0, "total_loss_W": 27.0},
        {"turns": 30, "inductance_uH": 450.0, "core_loss_W": 5.5, "winding_loss_W": 22.0, "total_loss_W": 27.5},
        {"turns": 40, "inductance_uH": 800.0, "core_loss_W": 3.0, "winding_loss_W": 30.0, "total_loss_W": 33.0},
        {"turns": 50, "inductance_uH": 1250.0, "core_loss_W": 2.0, "winding_loss_W": 38.0, "total_loss_W": 40.0},
    ]

    optimal = min(results, key=lambda x: x["total_loss_W"])

    print(f"\n{'Turns':>6} {'L (uH)':>10} {'Core (W)':>12} {'Cu (W)':>12} {'Total (W)':>12}")
    print("-" * 54)
    for r in results:
        marker = " *" if r == optimal else ""
        print(f"{r['turns']:>6} {r['inductance_uH']:>10.1f} {r['core_loss_W']:>12.1f} "
              f"{r['winding_loss_W']:>12.1f} {r['total_loss_W']:>12.1f}{marker}")

    print(f"\n* Optimal: {optimal['turns']} turns (lowest total loss)")

    print("\nKey Insights:")
    print("  1. Very few turns -> high flux density -> extreme core loss")
    print("  2. Too many turns -> long wire -> high winding loss")
    print("  3. There's a sweet spot that minimizes total losses")
    print("  4. The optimal point depends on frequency and core material")

    return results


def frequency_sweep_analysis():
    """Demonstrate frequency sweep analysis."""
    print(f"\n" + "=" * 70)
    print("FREQUENCY SWEEP ANALYSIS")
    print("=" * 70)

    frequencies = [50e3, 100e3, 200e3, 400e3]

    print("\nAnalyzing losses vs frequency (fixed turns = 30):")
    print(f"{'Frequency':>12} {'Core Loss':>12} {'Cu Loss':>12} {'Skin Depth':>12}")
    print("-" * 50)

    for freq in frequencies:
        # Approximate calculations for demo
        # Core loss increases with frequency (Steinmetz)
        core_loss = 1000 * (freq / 100e3) ** 1.3

        # Copper loss increases due to skin effect
        skin_depth_mm = 66 / (freq / 1000) ** 0.5
        ac_factor = 1 + 0.1 * (100e3 / freq) ** 0.5
        cu_loss = 50 * ac_factor

        print(f"{freq/1e3:>10.0f}kHz {core_loss:>12.1f}W {cu_loss:>12.1f}W "
              f"{skin_depth_mm:>10.2f}mm")

    print("\nNotes:")
    print("  - Core loss increases with frequency (Steinmetz equation)")
    print("  - Skin depth decreases, increasing AC resistance")
    print("  - Consider Litz wire for frequencies above 100kHz")


def save_analysis_report():
    """Save analysis results to output directory."""
    import json
    from pathlib import Path

    output_dir = get_output_dir("custom_simulation")
    output_path = Path(output_dir)

    # Save turns sweep data
    turns_data = [
        {"turns": 10, "inductance_uH": 50.0, "core_loss_W": 45.0, "winding_loss_W": 8.0, "total_loss_W": 53.0},
        {"turns": 20, "inductance_uH": 200.0, "core_loss_W": 12.0, "winding_loss_W": 15.0, "total_loss_W": 27.0},
        {"turns": 30, "inductance_uH": 450.0, "core_loss_W": 5.5, "winding_loss_W": 22.0, "total_loss_W": 27.5},
        {"turns": 40, "inductance_uH": 800.0, "core_loss_W": 3.0, "winding_loss_W": 30.0, "total_loss_W": 33.0},
        {"turns": 50, "inductance_uH": 1250.0, "core_loss_W": 2.0, "winding_loss_W": 38.0, "total_loss_W": 40.0},
    ]

    summary = {
        "example": "custom_magnetic_simulation",
        "description": "Turns sweep analysis for high-power boost inductor",
        "optimal_turns": 20,
        "optimal_total_loss_W": 27.0,
        "turns_sweep": turns_data,
    }

    json_path = output_path / "analysis_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {output_dir}/")
    print(f"  - analysis_summary.json")

    # Try to generate matplotlib plot
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))

        turns = [d["turns"] for d in turns_data]
        core_loss = [d["core_loss_W"] for d in turns_data]
        winding_loss = [d["winding_loss_W"] for d in turns_data]
        total_loss = [d["total_loss_W"] for d in turns_data]

        ax.plot(turns, core_loss, 'b-o', label='Core Loss', linewidth=2)
        ax.plot(turns, winding_loss, 'r-s', label='Winding Loss', linewidth=2)
        ax.plot(turns, total_loss, 'g-^', label='Total Loss', linewidth=2)

        # Mark optimal point
        opt_idx = total_loss.index(min(total_loss))
        ax.axvline(x=turns[opt_idx], color='gray', linestyle='--', alpha=0.5)
        ax.scatter([turns[opt_idx]], [total_loss[opt_idx]], c='green', s=150, marker='*', zorder=5)

        ax.set_xlabel("Number of Turns", fontsize=12)
        ax.set_ylabel("Loss (W)", fontsize=12)
        ax.set_title("Turns vs Loss Tradeoff Analysis", fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = output_path / "turns_sweep.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()

        print(f"  - turns_sweep.png (visualization)")

    except ImportError:
        print("  [matplotlib not available for plot generation]")


def main():
    """Run the custom magnetic simulation examples."""
    analyze_turns_sweep()
    frequency_sweep_analysis()
    save_analysis_report()

    print(f"\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nThis example demonstrated:")
    print("  - Parameter sweeps (turns, frequency)")
    print("  - Core vs winding loss tradeoffs")
    print("  - Finding optimal design point")
    print("\nFor production use with PyOpenMagnetics:")
    print("  from api.design import Design")
    print("  results = Design.inductor().inductance(450e-6).idc(10).fsw(100e3).solve()")


if __name__ == "__main__":
    main()
