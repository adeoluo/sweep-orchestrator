"""Measure what pruning and multi-fidelity scheduling save.

Compare three strategies on the bundled sweep problem: run every configuration to
full budget (no pruning), run with a median pruner, and run successive halving.
Report the best final loss each finds and the total resource (step-evaluations)
each spends, so the compute saving of early stopping is explicit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from sweep_orchestrator.data import STEPS, final_loss, learning_curve, sample_configurations
from sweep_orchestrator.pruning import MedianPruner
from sweep_orchestrator.runner import SweepRunner
from sweep_orchestrator.successive_halving import successive_halving


@dataclass(frozen=True)
class StrategyResult:
    """The outcome of one sweep strategy: best loss and resource spent."""

    strategy: str
    best_loss: float
    resource: int


def _resource_of(store_history_lengths: Sequence[int]) -> int:
    return sum(store_history_lengths)


def run_evaluation(*, count: int = 27, seed: int = 0) -> list[StrategyResult]:
    """Compare full evaluation, median pruning, and successive halving."""
    configurations = sample_configurations(count, seed=seed)
    results: list[StrategyResult] = []

    full = SweepRunner(steps=STEPS).run(configurations, learning_curve)
    results.append(
        StrategyResult(
            "full (no pruning)",
            full.best().value,
            _resource_of([len(record.history) for record in full.records.values()]),
        )
    )

    pruned = SweepRunner(steps=STEPS, pruner=MedianPruner(n_warmup=1, min_peers=3)).run(
        configurations, learning_curve
    )
    results.append(
        StrategyResult(
            "median pruning",
            pruned.best().value,
            _resource_of([len(record.history) for record in pruned.records.values()]),
        )
    )

    def objective(configuration: Mapping[str, float], resource: int) -> float:
        return learning_curve(configuration, min(resource, STEPS) - 1)

    bracket = successive_halving(
        configurations, objective, min_resource=1, max_resource=STEPS, eta=3
    )
    results.append(StrategyResult("successive halving", bracket.best.loss, bracket.total_resource))
    return results


def format_table(results: Sequence[StrategyResult]) -> str:
    """Render the strategy comparison as a text table."""
    header = f"{'strategy':<22}{'best loss':>12}{'resource':>12}"
    lines = [header, "-" * len(header)]
    for result in results:
        lines.append(f"{result.strategy:<22}{result.best_loss:>12.4f}{result.resource:>12}")
    baseline = next(r.resource for r in results if r.strategy == "full (no pruning)")
    lines.append("")
    lines.append(f"Full-budget resource = {baseline} step-evaluations; lower is cheaper.")
    return "\n".join(lines)


def ground_truth_best(*, count: int = 27, seed: int = 0) -> float:
    """The true best final loss over the sampled configurations."""
    return min(final_loss(config) for config in sample_configurations(count, seed=seed))
