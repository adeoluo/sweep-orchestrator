"""Hyperparameter importance via variance decomposition.

After a sweep, the natural question is *which hyperparameters mattered*. This
module answers it with a functional-ANOVA-style decomposition: for each
parameter, bin the completed trials by that parameter's value and measure how
much of the total variance in the objective is explained by the between-bin
differences. A parameter whose value strongly predicts the objective explains a
large fraction of the variance and is therefore important.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from sweep_orchestrator.types import Configuration


@dataclass(frozen=True)
class Observation:
    """One completed trial: its configuration and the objective it achieved."""

    configuration: Configuration
    objective: float


@dataclass(frozen=True)
class Importance:
    """The fraction of objective variance explained by one parameter."""

    parameter: str
    explained_variance: float


def _variance(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def _explained_fraction(values: Sequence[float], groups: Sequence[int], bins: int) -> float:
    total_variance = _variance(values)
    if total_variance == 0.0:
        return 0.0
    grand_mean = sum(values) / len(values)
    between = 0.0
    for bin_index in range(bins):
        members = [value for value, group in zip(values, groups, strict=True) if group == bin_index]
        if not members:
            continue
        group_mean = sum(members) / len(members)
        between += len(members) * (group_mean - grand_mean) ** 2
    between /= len(values)
    return min(1.0, between / total_variance)


def parameter_importance(observations: Sequence[Observation], *, bins: int = 4) -> list[Importance]:
    """Rank parameters by the fraction of objective variance they explain."""
    if len(observations) < 2:
        raise ValueError("need at least two observations")
    if bins < 2:
        raise ValueError("bins must be at least 2")

    objectives = [observation.objective for observation in observations]
    names = sorted(observations[0].configuration)
    importances: list[Importance] = []
    for name in names:
        values = [float(observation.configuration[name]) for observation in observations]
        groups = _bin_values(values, bins)
        fraction = _explained_fraction(objectives, groups, bins)
        importances.append(Importance(parameter=name, explained_variance=fraction))
    importances.sort(key=lambda item: item.explained_variance, reverse=True)
    return importances


def _bin_values(values: Sequence[float], bins: int) -> list[int]:
    low, high = min(values), max(values)
    span = high - low
    if span == 0:
        return [0 for _ in values]
    return [min(bins - 1, int((value - low) / span * bins)) for value in values]


def format_importance(importances: Sequence[Importance]) -> str:
    """Render a ranked importance table."""
    lines = [f"{'parameter':<20}{'explained variance':>20}", "-" * 40]
    for item in importances:
        lines.append(f"{item.parameter:<20}{item.explained_variance:>20.4f}")
    return "\n".join(lines)
