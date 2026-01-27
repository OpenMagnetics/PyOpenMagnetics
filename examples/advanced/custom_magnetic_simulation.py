"""
Custom Magnetic Component Simulation

Application: Analyzing an existing inductor design (BDC6128 boost inductor)
Demonstrates: Loading existing magnetic definitions, sweeping parameters,
              comparing losses across operating conditions

This example shows how to:
1. Load a pre-defined magnetic component from JSON
2. Run simulations across different number of turns
3. Analyze core vs winding losses tradeoffs
4. Find optimal turns for minimum total loss

The BDC6128 is a high-power boost inductor used in EV charger applications.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import json
import copy
from pathlib import Path

# Try to import PyOpenMagnetics (may not be available in all environments)
try:
    import PyOpenMagnetics
    HAS_PYOPENMAGMETICS = True
except ImportError:
    HAS_PYOPENMAGMETICS = False
    print("Note: PyOpenMagnetics not available. Running in demo mode.")

# Import local modules
from examples.data import load_bdc6128_inductor, DATA_DIR


def analyze_turns_sweep():
    """Sweep number of turns and analyze loss tradeoffs."""
    print("=" * 70)
    print("CUSTOM MAGNETIC SIMULATION - TURNS SWEEP ANALYSIS")
    print("Component: BDC6128 Boost Inductor")
    print("=" * 70)

    # Load the pre-defined magnetic component
    print("\nLoading magnetic definition...")
    try:
        mas = load_bdc6128_inductor()
        magnetic = mas.get("magnetic", {})
        inputs = mas.get("inputs", {})
        print(f"  Loaded: {DATA_DIR / 'bdc6128_inductor.json'}")
    except FileNotFoundError:
        print("  Error: BDC6128 definition not found. Using example parameters.")
        return demo_mode()

    # Display component info
    core = magnetic.get("core", {})
    coil = magnetic.get("coil", {})

    core_shape = core.get("functionalDescription", {}).get("shape", {}).get("name", "Unknown")
    core_material = core.get("functionalDescription", {}).get("material", "Unknown")
    if isinstance(core_material, dict):
        core_material = core_material.get("name", "Unknown")

    print(f"\nComponent Details:")
    print(f"  Core shape:    {core_shape}")
    print(f"  Core material: {core_material}")

    if not HAS_PYOPENMAGMETICS:
        return demo_mode()

    # Get operating frequency
    freq = inputs.get("operatingPoints", [{}])[0].get(
        "excitationsPerWinding", [{}]
    )[0].get("frequency", 100e3)

    print(f"  Frequency:     {freq/1e3:.0f} kHz")

    # Sweep number of turns (starting from 10, not 1 - more realistic)
    turns_range = list(range(10, 60, 10))
    results = []

    print(f"\n" + "-" * 70)
    print(f"SWEEPING TURNS: {turns_range}")
    print("-" * 70)

    # Loss calculation models
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG"
    }

    for turns in turns_range:
        print(f"\nSimulating {turns} turns...")

        try:
            # Create a deep copy to modify
            mag_copy = copy.deepcopy(magnetic)
            inputs_copy = copy.deepcopy(inputs)

            # Update turns count in the coil
            if "functionalDescription" in mag_copy["coil"]:
                for winding in mag_copy["coil"]["functionalDescription"]:
                    winding["numberTurns"] = turns

            # Re-wind the coil with new turns
            mag_copy["coil"] = PyOpenMagnetics.wind(
                mag_copy["coil"], 1, [], [], []
            )

            # Calculate inductance
            magnetizing_inductance = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
                mag_copy["core"],
                mag_copy["coil"],
                inputs_copy["operatingPoints"][0],
                models
            )

            # Calculate core losses
            losses = PyOpenMagnetics.calculate_core_losses(
                mag_copy["core"],
                mag_copy["coil"],
                inputs_copy,
                models
            )
            core_loss = losses.get("coreLosses", 0)

            # Calculate winding losses
            winding_losses = PyOpenMagnetics.calculate_winding_losses(
                mag_copy,
                inputs_copy["operatingPoints"][0],
                85  # Operating temperature
            )
            winding_loss = winding_losses.get("windingLosses", 0)

            total_loss = core_loss + winding_loss

            results.append({
                "turns": turns,
                "inductance_uH": magnetizing_inductance * 1e6,
                "core_loss_W": core_loss,
                "winding_loss_W": winding_loss,
                "total_loss_W": total_loss,
            })

            print(f"  L = {magnetizing_inductance*1e6:.2f} uH")
            print(f"  Core loss:    {core_loss:.2f} W")
            print(f"  Winding loss: {winding_loss:.2f} W")
            print(f"  Total loss:   {total_loss:.2f} W")

        except Exception as e:
            print(f"  Error simulating {turns} turns: {e}")
            continue

    if not results:
        print("\nNo successful simulations. Falling back to demo mode.")
        return demo_mode()

    # Find optimal turns
    optimal = min(results, key=lambda x: x["total_loss_W"])

    print(f"\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)

    print(f"\n{'Turns':>6} {'L (uH)':>10} {'Core (W)':>12} {'Cu (W)':>12} {'Total (W)':>12}")
    print("-" * 54)
    for r in results:
        marker = " *" if r == optimal else ""
        print(f"{r['turns']:>6} {r['inductance_uH']:>10.2f} {r['core_loss_W']:>12.2f} "
              f"{r['winding_loss_W']:>12.2f} {r['total_loss_W']:>12.2f}{marker}")

    print(f"\n* Optimal: {optimal['turns']} turns")
    print(f"  Inductance: {optimal['inductance_uH']:.2f} uH")
    print(f"  Total loss: {optimal['total_loss_W']:.2f} W")

    print("\nObservations:")
    print("  - Core loss decreases with more turns (lower flux density)")
    print("  - Winding loss increases with more turns (longer wire)")
    print("  - Optimal point balances these competing effects")

    return results


def demo_mode():
    """Run in demo mode without PyOpenMagnetics."""
    print(f"\n" + "-" * 70)
    print("DEMO MODE - Simulated Results")
    print("-" * 70)

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
    print("  1. Very few turns has extreme core loss due to high flux density")
    print("  2. Too many turns increases winding loss without proportional core benefit")
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


def main():
    """Run the custom magnetic simulation examples."""
    results = analyze_turns_sweep()
    frequency_sweep_analysis()

    print(f"\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nThis example demonstrated:")
    print("  - Loading custom magnetic definitions")
    print("  - Parameter sweeps (turns, frequency)")
    print("  - Loss analysis and optimization")
    print("\nFor production use:")
    print("  - Install PyOpenMagnetics for full simulation")
    print("  - Use actual measured core/material data")
    print("  - Consider thermal constraints")


if __name__ == "__main__":
    main()
