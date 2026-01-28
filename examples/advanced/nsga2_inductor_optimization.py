"""
Multi-Objective Inductor Optimization using NSGA-II

Application: Finding optimal inductor designs for EV chargers
Optimizes: Mass vs Total Losses (Pareto front)

This example demonstrates using evolutionary multi-objective optimization
to find the best tradeoffs between competing design goals.

Why multi-objective optimization?
- Single-objective optimization forces you to pick ONE best design
- Real engineering involves tradeoffs: lighter = more expensive, etc.
- Pareto optimization gives you the FULL tradeoff curve
- You can then pick based on actual project constraints

Algorithm: NSGA-II (Non-dominated Sorting Genetic Algorithm II)
- Industry standard for multi-objective optimization
- Maintains population diversity on the Pareto front
- Handles constraints naturally
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import math
from api.optimization import NSGAOptimizer, ParetoFront
from examples.common import DEFAULT_MAX_RESULTS, get_output_dir


def optimize_boost_inductor():
    """Optimize a boost inductor for mass vs efficiency tradeoff."""
    print("=" * 70)
    print("NSGA-II MULTI-OBJECTIVE INDUCTOR OPTIMIZATION")
    print("Objectives: Minimize Mass AND Minimize Losses")
    print(f"Target: {DEFAULT_MAX_RESULTS} Pareto-optimal solutions")
    print("=" * 70)

    # Define the optimization problem
    print("\nSetting up optimization problem...")

    optimizer = NSGAOptimizer(
        objectives=["mass", "total_loss"],
        constraints={
            "inductance": (100e-6, 140e-6),  # 100-140 uH
        }
    )

    # Add design variables
    optimizer.add_variable(
        "turns",
        range=(20, 60),
        var_type="integer"
    )
    optimizer.add_variable(
        "core_size",
        range=(0.5, 2.0),  # Relative size factor
        var_type="continuous"
    )
    optimizer.add_variable(
        "wire_gauge",
        choices=[14, 16, 18, 20, 22],  # AWG wire sizes
    )

    print(f"  Variables: {len(optimizer.variables)}")
    for var in optimizer.variables:
        if var.choices:
            print(f"    - {var.name}: choices {var.choices}")
        else:
            print(f"    - {var.name}: {var.bounds[0]} to {var.bounds[1]}")

    print(f"  Objectives: {optimizer.objectives}")
    print(f"  Constraints: {optimizer.constraints}")

    # Run optimization with 50 population for Pareto front
    print(f"\n" + "-" * 70)
    print("RUNNING NSGA-II OPTIMIZATION")
    print("-" * 70)

    pareto_front = optimizer.run(
        generations=30,
        population=DEFAULT_MAX_RESULTS,  # Use 50 for diverse Pareto front
        seed=42,  # For reproducibility
    )

    print(f"\nOptimization complete!")
    print(f"  Generations: {pareto_front.generations}")
    print(f"  Population: {pareto_front.population_size}")
    print(f"  Pareto solutions: {len(pareto_front)}")

    # Display results
    display_pareto_front(pareto_front)

    # Save results
    save_pareto_report(pareto_front, "nsga2_inductor")

    return pareto_front


def optimize_with_custom_evaluator():
    """Demonstrate custom evaluation function with PyOpenMagnetics."""
    print(f"\n" + "=" * 70)
    print("OPTIMIZATION WITH CUSTOM EVALUATOR")
    print("=" * 70)

    # Try to use PyOpenMagnetics for accurate evaluation
    try:
        import PyOpenMagnetics
        HAS_PYOPENMAGMETICS = True
    except ImportError:
        HAS_PYOPENMAGMETICS = False

    def custom_evaluator(variables: dict) -> dict:
        """
        Custom evaluation function.

        In production, this would call PyOpenMagnetics.simulate()
        for accurate loss and thermal calculations.
        """
        turns = variables.get("turns", 30)
        core_idx = variables.get("core_idx", 0)
        material_idx = variables.get("material_idx", 0)

        # Core options (simplified)
        cores = ["ETD29", "ETD34", "ETD39", "ETD44", "ETD49"]
        materials = ["3C95", "N97", "High_Flux_125u", "Sendust_60u"]

        core = cores[min(core_idx, len(cores)-1)]
        material = materials[min(material_idx, len(materials)-1)]

        # Simplified model (replace with actual simulation)
        core_volumes = {"ETD29": 5.5e-6, "ETD34": 7.6e-6, "ETD39": 11.5e-6,
                       "ETD44": 17.8e-6, "ETD49": 24.0e-6}
        core_vol = core_volumes.get(core, 10e-6)

        # Mass estimation
        core_density = 4800  # kg/m3 for ferrite
        wire_density = 8900  # kg/m3 for copper
        core_mass = core_vol * core_density
        wire_mass = turns * 0.001 * (core_vol ** 0.33)  # Simplified
        total_mass = core_mass + wire_mass

        # Loss estimation (very simplified)
        # In reality, use PyOpenMagnetics.calculate_core_losses()
        freq = 100e3
        B_peak = 0.2 / math.sqrt(turns)
        core_loss = 50 * core_vol * 1e6 * (freq/100e3)**1.3 * B_peak**2.5
        copper_loss = 0.1 * turns * (core_vol ** 0.33)
        total_loss = core_loss + copper_loss

        # Inductance
        mu_r = 2000 if "3C" in material or "N9" in material else 60
        al = 4 * math.pi * 1e-7 * mu_r * (core_vol ** 0.67) / 0.001
        inductance = turns ** 2 * al

        return {
            "mass": total_mass,
            "total_loss": total_loss,
            "core_loss": core_loss,
            "copper_loss": copper_loss,
            "inductance": inductance,
            "core": core,
            "material": material,
        }

    # Create optimizer with custom evaluator
    optimizer = NSGAOptimizer(
        objectives=["mass", "total_loss"],
        constraints={"inductance": (100e-6, 200e-6)}
    )

    optimizer.add_variable("turns", range=(15, 50), var_type="integer")
    optimizer.add_variable("core_idx", range=(0, 4), var_type="integer")
    optimizer.add_variable("material_idx", range=(0, 3), var_type="integer")

    optimizer.set_evaluator(custom_evaluator)

    print("\nRunning with custom evaluator...")
    pareto_front = optimizer.run(generations=20, population=30, seed=123)

    print(f"Found {len(pareto_front)} Pareto-optimal designs")

    # Show some solutions
    print(f"\nSample Solutions:")
    print("-" * 70)

    sorted_by_mass = pareto_front.sort_by("mass")
    for i, sol in enumerate(sorted_by_mass[:5]):
        print(f"\nDesign {i+1}:")
        print(f"  Turns: {sol.variables['turns']}")
        print(f"  Core:  ETD{29 + sol.variables['core_idx']*5}")
        materials = ["3C95", "N97", "High_Flux_125u", "Sendust_60u"]
        print(f"  Material: {materials[sol.variables['material_idx']]}")
        print(f"  Mass: {sol.objectives['mass']*1000:.1f} g")
        print(f"  Loss: {sol.objectives['total_loss']:.2f} W")


def display_pareto_front(pareto: ParetoFront):
    """Display Pareto front results in a readable format."""
    print(f"\n" + "-" * 70)
    print("PARETO FRONT RESULTS")
    print("-" * 70)

    # Sort by mass
    sorted_solutions = pareto.sort_by("mass")

    print(f"\n{'#':>3} {'Mass (g)':>10} {'Loss (W)':>10} {'Turns':>7} "
          f"{'Core Size':>11} {'Wire AWG':>10}")
    print("-" * 55)

    for i, sol in enumerate(sorted_solutions[:15], 1):
        mass_g = sol.objectives.get("mass", 0) * 1000
        loss_w = sol.objectives.get("total_loss", 0)
        turns = sol.variables.get("turns", "?")
        core_size = sol.variables.get("core_size", "?")
        wire = sol.variables.get("wire_gauge", "?")

        if isinstance(core_size, float):
            core_size = f"{core_size:.2f}x"

        print(f"{i:>3} {mass_g:>10.1f} {loss_w:>10.2f} {turns:>7} "
              f"{core_size:>11} {wire:>10}")

    # Analysis
    min_mass = min(s.objectives["mass"] for s in sorted_solutions)
    max_mass = max(s.objectives["mass"] for s in sorted_solutions)
    min_loss = min(s.objectives["total_loss"] for s in sorted_solutions)
    max_loss = max(s.objectives["total_loss"] for s in sorted_solutions)

    print(f"\n" + "-" * 70)
    print("TRADEOFF ANALYSIS")
    print("-" * 70)
    print(f"\nMass range:  {min_mass*1000:.1f}g - {max_mass*1000:.1f}g")
    print(f"Loss range:  {min_loss:.2f}W - {max_loss:.2f}W")

    # Find knee point (good balance)
    # Normalize objectives and find point closest to origin
    best_balanced = None
    best_score = float('inf')
    for sol in sorted_solutions:
        norm_mass = (sol.objectives["mass"] - min_mass) / (max_mass - min_mass + 1e-9)
        norm_loss = (sol.objectives["total_loss"] - min_loss) / (max_loss - min_loss + 1e-9)
        score = math.sqrt(norm_mass**2 + norm_loss**2)
        if score < best_score:
            best_score = score
            best_balanced = sol

    if best_balanced:
        print(f"\nRecommended (balanced) design:")
        print(f"  Turns:     {best_balanced.variables.get('turns')}")
        print(f"  Core size: {best_balanced.variables.get('core_size', 1):.2f}x")
        print(f"  Wire:      AWG {best_balanced.variables.get('wire_gauge')}")
        print(f"  Mass:      {best_balanced.objectives['mass']*1000:.1f}g")
        print(f"  Loss:      {best_balanced.objectives['total_loss']:.2f}W")


def save_pareto_report(pareto: ParetoFront, example_name: str):
    """Save Pareto front report to output directory."""
    import json
    from pathlib import Path

    output_dir = get_output_dir(example_name)
    output_path = Path(output_dir)

    # Save JSON summary
    solutions_data = []
    for sol in pareto.solutions:
        solutions_data.append({
            "variables": sol.variables,
            "objectives": sol.objectives,
        })

    summary = {
        "generations": pareto.generations,
        "population_size": pareto.population_size,
        "pareto_solutions": len(pareto),
        "solutions": solutions_data,
    }

    json_path = output_path / "pareto_results.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {output_dir}/")
    print(f"  - pareto_results.json ({len(solutions_data)} solutions)")

    # Try to generate matplotlib plot
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 8))

        masses = [s.objectives["mass"] * 1000 for s in pareto.solutions]
        losses = [s.objectives["total_loss"] for s in pareto.solutions]

        ax.scatter(masses, losses, c='blue', alpha=0.7, s=50)
        ax.set_xlabel("Mass (g)", fontsize=12)
        ax.set_ylabel("Total Loss (W)", fontsize=12)
        ax.set_title("NSGA-II Pareto Front: Mass vs Loss", fontsize=14)
        ax.grid(True, alpha=0.3)

        # Mark best balanced point
        min_mass, max_mass = min(masses), max(masses)
        min_loss, max_loss = min(losses), max(losses)

        best_idx = 0
        best_score = float('inf')
        for i, (m, l) in enumerate(zip(masses, losses)):
            norm_m = (m - min_mass) / (max_mass - min_mass + 1e-9)
            norm_l = (l - min_loss) / (max_loss - min_loss + 1e-9)
            score = math.sqrt(norm_m**2 + norm_l**2)
            if score < best_score:
                best_score = score
                best_idx = i

        ax.scatter([masses[best_idx]], [losses[best_idx]],
                  c='red', s=150, marker='*', label='Balanced', zorder=5)
        ax.legend()

        plt.tight_layout()
        plot_path = output_path / "pareto_front.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()

        print(f"  - pareto_front.png (visualization)")

    except ImportError:
        print("  [matplotlib not available for plot generation]")


def plot_pareto_ascii(pareto: ParetoFront):
    """Create ASCII art visualization of Pareto front."""
    print(f"\n" + "-" * 70)
    print("PARETO FRONT VISUALIZATION")
    print("-" * 70)

    solutions = pareto.solutions
    if not solutions:
        print("No solutions to plot")
        return

    masses = [s.objectives["mass"] * 1000 for s in solutions]
    losses = [s.objectives["total_loss"] for s in solutions]

    min_m, max_m = min(masses), max(masses)
    min_l, max_l = min(losses), max(losses)

    # Create grid
    width, height = 50, 20
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot points
    for m, l in zip(masses, losses):
        x = int((m - min_m) / (max_m - min_m + 1e-9) * (width - 1))
        y = int((1 - (l - min_l) / (max_l - min_l + 1e-9)) * (height - 1))
        x = max(0, min(width-1, x))
        y = max(0, min(height-1, y))
        grid[y][x] = '*'

    # Print grid
    print(f"\n     Loss (W)")
    print(f"     ^")
    print(f"{max_l:5.1f}|" + "".join(grid[0]))
    for i in range(1, height-1):
        print("     |" + "".join(grid[i]))
    print(f"{min_l:5.1f}|" + "".join(grid[-1]))
    print("     +" + "-" * width + "> Mass (g)")
    print(f"      {min_m:.0f}" + " " * (width - 10) + f"{max_m:.0f}")


def main():
    """Run the NSGA-II optimization examples."""
    # Basic optimization
    pareto = optimize_boost_inductor()

    # ASCII visualization
    plot_pareto_ascii(pareto)

    # Advanced: custom evaluator
    optimize_with_custom_evaluator()

    print(f"\n" + "=" * 70)
    print("OPTIMIZATION COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Multi-objective optimization reveals the full design space")
    print("  2. The Pareto front shows unavoidable tradeoffs")
    print("  3. No single 'best' design - choose based on priorities")
    print("  4. Use PyOpenMagnetics for accurate evaluations in production")


if __name__ == "__main__":
    main()
