"""
Multi-objective optimization module for magnetic component design.

Provides wrappers around pymoo's NSGA-II algorithm for Pareto optimization
of inductor and transformer designs.

Example:
    from api.optimization import NSGAOptimizer

    optimizer = NSGAOptimizer(
        objectives=["mass", "total_loss"],
        constraints={"inductance": (100e-6, 140e-6), "max_temp_rise": 50}
    )
    optimizer.add_variable("turns", range=(20, 60))
    pareto_front = optimizer.run(generations=50)
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
from abc import ABC, abstractmethod


@dataclass
class DesignVariable:
    """Definition of a design variable for optimization."""
    name: str
    var_type: str  # "continuous", "integer", "discrete"
    bounds: Optional[tuple] = None  # (min, max) for continuous/integer
    choices: Optional[list] = None  # For discrete variables

    def __post_init__(self):
        if self.var_type in ("continuous", "integer") and self.bounds is None:
            raise ValueError(f"Variable {self.name}: bounds required for {self.var_type}")
        if self.var_type == "discrete" and self.choices is None:
            raise ValueError(f"Variable {self.name}: choices required for discrete")


@dataclass
class OptimizationResult:
    """Result from a single Pareto-optimal design."""
    variables: dict
    objectives: dict
    constraints: dict
    feasible: bool = True

    @property
    def mass_kg(self) -> Optional[float]:
        return self.objectives.get("mass")

    @property
    def total_loss_w(self) -> Optional[float]:
        return self.objectives.get("total_loss")


@dataclass
class ParetoFront:
    """Collection of Pareto-optimal solutions."""
    solutions: list[OptimizationResult] = field(default_factory=list)
    generations: int = 0
    population_size: int = 0
    converged: bool = False

    def __len__(self) -> int:
        return len(self.solutions)

    def __iter__(self):
        return iter(self.solutions)

    def __getitem__(self, idx) -> OptimizationResult:
        return self.solutions[idx]

    def sort_by(self, objective: str, ascending: bool = True) -> list[OptimizationResult]:
        """Sort solutions by a specific objective."""
        return sorted(
            self.solutions,
            key=lambda x: x.objectives.get(objective, float('inf')),
            reverse=not ascending
        )

    def filter_feasible(self) -> list[OptimizationResult]:
        """Return only feasible solutions."""
        return [s for s in self.solutions if s.feasible]


class BaseOptimizer(ABC):
    """Abstract base class for optimizers."""

    def __init__(
        self,
        objectives: list[str],
        constraints: Optional[dict] = None,
    ):
        self.objectives = objectives
        self.constraints = constraints or {}
        self.variables: list[DesignVariable] = []
        self._evaluator: Optional[Callable] = None

    def add_variable(
        self,
        name: str,
        *,
        range: Optional[tuple] = None,
        choices: Optional[list] = None,
        var_type: Optional[str] = None,
    ) -> "BaseOptimizer":
        """Add a design variable to the optimization."""
        if choices is not None:
            var = DesignVariable(name, "discrete", choices=choices)
        elif range is not None:
            inferred_type = var_type or ("integer" if all(isinstance(x, int) for x in range) else "continuous")
            var = DesignVariable(name, inferred_type, bounds=range)
        else:
            raise ValueError(f"Variable {name}: provide either range or choices")

        self.variables.append(var)
        return self

    def set_evaluator(self, evaluator: Callable[[dict], dict]) -> "BaseOptimizer":
        """Set custom evaluation function.

        Args:
            evaluator: Function that takes variable dict and returns
                      dict with objective values.
        """
        self._evaluator = evaluator
        return self

    @abstractmethod
    def run(
        self,
        generations: int = 50,
        population: int = 100,
        seed: Optional[int] = None,
    ) -> ParetoFront:
        """Run the optimization."""
        ...


class NSGAOptimizer(BaseOptimizer):
    """NSGA-II multi-objective optimizer for magnetic design.

    Uses pymoo for optimization if available, falls back to random sampling.
    """

    def __init__(
        self,
        objectives: list[str],
        constraints: Optional[dict] = None,
    ):
        super().__init__(objectives, constraints)
        self._pymoo_available = self._check_pymoo()

    def _check_pymoo(self) -> bool:
        """Check if pymoo is available."""
        try:
            import pymoo
            return True
        except ImportError:
            return False

    def run(
        self,
        generations: int = 50,
        population: int = 100,
        seed: Optional[int] = None,
    ) -> ParetoFront:
        """Run NSGA-II optimization.

        Args:
            generations: Number of generations to evolve
            population: Population size per generation
            seed: Random seed for reproducibility

        Returns:
            ParetoFront with optimal solutions
        """
        if not self.variables:
            raise ValueError("No design variables defined. Use add_variable().")

        if self._pymoo_available:
            return self._run_pymoo(generations, population, seed)
        else:
            print("Note: pymoo not available. Using random sampling fallback.")
            return self._run_random_sampling(generations * population, seed)

    def _run_pymoo(
        self,
        generations: int,
        population: int,
        seed: Optional[int],
    ) -> ParetoFront:
        """Run optimization using pymoo's NSGA-II."""
        import numpy as np
        from pymoo.algorithms.moo.nsga2 import NSGA2
        from pymoo.core.problem import Problem
        from pymoo.optimize import minimize
        from pymoo.operators.crossover.sbx import SBX
        from pymoo.operators.mutation.pm import PM
        from pymoo.operators.sampling.rnd import FloatRandomSampling

        optimizer = self

        class MagneticProblem(Problem):
            def __init__(self):
                n_var = len(optimizer.variables)
                n_obj = len(optimizer.objectives)

                # Set up bounds
                xl = []
                xu = []
                for var in optimizer.variables:
                    if var.var_type == "discrete":
                        xl.append(0)
                        xu.append(len(var.choices) - 1)
                    else:
                        xl.append(var.bounds[0])
                        xu.append(var.bounds[1])

                super().__init__(
                    n_var=n_var,
                    n_obj=n_obj,
                    n_ieq_constr=len(optimizer.constraints),
                    xl=np.array(xl),
                    xu=np.array(xu),
                )

            def _evaluate(self, x, out, *args, **kwargs):
                F = []
                G = []

                for xi in x:
                    # Convert to variable dict
                    var_dict = {}
                    for i, var in enumerate(optimizer.variables):
                        if var.var_type == "discrete":
                            idx = int(round(xi[i]))
                            idx = max(0, min(idx, len(var.choices) - 1))
                            var_dict[var.name] = var.choices[idx]
                        elif var.var_type == "integer":
                            var_dict[var.name] = int(round(xi[i]))
                        else:
                            var_dict[var.name] = xi[i]

                    # Evaluate
                    if optimizer._evaluator:
                        result = optimizer._evaluator(var_dict)
                    else:
                        result = optimizer._default_evaluator(var_dict)

                    # Extract objectives
                    f = [result.get(obj, float('inf')) for obj in optimizer.objectives]
                    F.append(f)

                    # Extract constraints (g <= 0 is feasible)
                    g = []
                    for name, (lo, hi) in optimizer.constraints.items():
                        val = result.get(name, 0)
                        g.append(lo - val)  # val >= lo
                        g.append(val - hi)  # val <= hi
                    G.append(g)

                out["F"] = np.array(F)
                if G:
                    out["G"] = np.array(G)

        problem = MagneticProblem()

        algorithm = NSGA2(
            pop_size=population,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(eta=20),
            eliminate_duplicates=True,
        )

        res = minimize(
            problem,
            algorithm,
            ("n_gen", generations),
            seed=seed,
            verbose=False,
        )

        # Convert results to ParetoFront
        solutions = []
        for i, (x, f) in enumerate(zip(res.X, res.F)):
            var_dict = {}
            for j, var in enumerate(self.variables):
                if var.var_type == "discrete":
                    idx = int(round(x[j]))
                    var_dict[var.name] = var.choices[idx]
                elif var.var_type == "integer":
                    var_dict[var.name] = int(round(x[j]))
                else:
                    var_dict[var.name] = x[j]

            obj_dict = {obj: f[k] for k, obj in enumerate(self.objectives)}

            # Check constraint violation
            feasible = True
            if res.G is not None:
                feasible = all(g <= 0 for g in res.G[i])

            solutions.append(OptimizationResult(
                variables=var_dict,
                objectives=obj_dict,
                constraints={},
                feasible=feasible,
            ))

        return ParetoFront(
            solutions=solutions,
            generations=generations,
            population_size=population,
            converged=True,
        )

    def _run_random_sampling(
        self,
        n_samples: int,
        seed: Optional[int],
    ) -> ParetoFront:
        """Fallback: random sampling with Pareto filtering."""
        import random
        if seed is not None:
            random.seed(seed)

        samples = []
        for _ in range(n_samples):
            var_dict = {}
            for var in self.variables:
                if var.var_type == "discrete":
                    var_dict[var.name] = random.choice(var.choices)
                elif var.var_type == "integer":
                    var_dict[var.name] = random.randint(var.bounds[0], var.bounds[1])
                else:
                    var_dict[var.name] = random.uniform(var.bounds[0], var.bounds[1])

            if self._evaluator:
                result = self._evaluator(var_dict)
            else:
                result = self._default_evaluator(var_dict)

            obj_dict = {obj: result.get(obj, float('inf')) for obj in self.objectives}

            # Check constraints
            feasible = True
            for name, (lo, hi) in self.constraints.items():
                val = result.get(name, 0)
                if val < lo or val > hi:
                    feasible = False
                    break

            samples.append(OptimizationResult(
                variables=var_dict,
                objectives=obj_dict,
                constraints={},
                feasible=feasible,
            ))

        # Filter to Pareto front
        pareto = self._pareto_filter(samples)

        return ParetoFront(
            solutions=pareto,
            generations=1,
            population_size=n_samples,
            converged=False,
        )

    def _pareto_filter(self, samples: list[OptimizationResult]) -> list[OptimizationResult]:
        """Filter samples to Pareto-optimal set."""
        feasible = [s for s in samples if s.feasible]
        if not feasible:
            return samples[:10]  # Return some samples even if infeasible

        pareto = []
        for candidate in feasible:
            dominated = False
            for other in feasible:
                if other is candidate:
                    continue
                # Check if other dominates candidate
                better_in_all = all(
                    other.objectives[obj] <= candidate.objectives[obj]
                    for obj in self.objectives
                )
                strictly_better = any(
                    other.objectives[obj] < candidate.objectives[obj]
                    for obj in self.objectives
                )
                if better_in_all and strictly_better:
                    dominated = True
                    break
            if not dominated:
                pareto.append(candidate)

        return pareto

    def _default_evaluator(self, variables: dict) -> dict:
        """Default evaluator using simplified inductor model."""
        # Extract variables
        turns = variables.get("turns", 30)
        core_size = variables.get("core_size", 1.0)  # Relative size factor
        wire_gauge = variables.get("wire_gauge", 18)

        # Simplified physics model
        # Mass ~ core_size^3 + turns * wire_mass
        wire_area = 0.5 * (0.127 ** (wire_gauge / 10))  # Simplified AWG
        core_mass = 0.1 * core_size ** 3
        wire_mass = turns * 0.05 * wire_area * core_size
        total_mass = core_mass + wire_mass

        # Losses ~ core_loss/turns^2 + copper_loss*turns
        core_loss = 10 * core_size ** 2 / (turns ** 1.5)
        copper_loss = 0.1 * turns * (1 / wire_area) * core_size
        total_loss = core_loss + copper_loss

        # Inductance
        inductance = turns ** 2 * core_size * 1e-6  # Simplified

        return {
            "mass": total_mass,
            "total_loss": total_loss,
            "core_loss": core_loss,
            "copper_loss": copper_loss,
            "inductance": inductance,
        }


def create_inductor_optimizer(
    target_inductance: float,
    tolerance: float = 0.2,
    max_loss: Optional[float] = None,
    max_mass: Optional[float] = None,
) -> NSGAOptimizer:
    """Factory function to create a pre-configured inductor optimizer.

    Args:
        target_inductance: Target inductance in Henries
        tolerance: Inductance tolerance (default ±20%)
        max_loss: Maximum acceptable loss in Watts (optional)
        max_mass: Maximum acceptable mass in kg (optional)

    Returns:
        Configured NSGAOptimizer ready for variable addition
    """
    constraints = {
        "inductance": (
            target_inductance * (1 - tolerance),
            target_inductance * (1 + tolerance),
        )
    }
    if max_loss:
        constraints["total_loss"] = (0, max_loss)
    if max_mass:
        constraints["mass"] = (0, max_mass)

    return NSGAOptimizer(
        objectives=["mass", "total_loss"],
        constraints=constraints,
    )
