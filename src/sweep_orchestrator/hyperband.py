"""Hyperband: hedging over how aggressively to prune.

Successive halving needs a choice of how many configurations to start with versus
how much resource to give each. Hyperband removes that guess by running several
brackets, from very aggressive early stopping (many configurations, little initial
resource) to no early stopping (few configurations, full resource), and taking the
best configuration found across all of them. The number of brackets and their
sizes follow directly from ``eta`` and the resource range.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from sweep_orchestrator.successive_halving import BracketResult, successive_halving
from sweep_orchestrator.types import Candidate, Configuration, Objective

# Draw ``count`` fresh configurations (for example by sampling the search space).
ConfigurationSampler = Callable[[int], Sequence[Configuration]]


@dataclass(frozen=True)
class HyperbandResult:
    """The outcome of a Hyperband run across all brackets."""

    brackets: tuple[BracketResult, ...]
    best: Candidate
    total_resource: int


def hyperband(
    sampler: ConfigurationSampler,
    objective: Objective,
    *,
    max_resource: int,
    eta: int = 3,
) -> HyperbandResult:
    """Run Hyperband and return the best configuration found across brackets."""
    if eta < 2:
        raise ValueError("eta must be at least 2")
    if max_resource < 1:
        raise ValueError("max_resource must be at least 1")

    s_max = math.floor(math.log(max_resource, eta))
    brackets: list[BracketResult] = []
    total_resource = 0

    for s in range(s_max, -1, -1):
        n = math.ceil((s_max + 1) / (s + 1) * eta**s)
        min_resource = max(1, int(max_resource / eta**s))
        configurations = list(sampler(n))
        bracket = successive_halving(
            configurations,
            objective,
            min_resource=min_resource,
            max_resource=max_resource,
            eta=eta,
        )
        brackets.append(bracket)
        total_resource += bracket.total_resource

    best = min((bracket.best for bracket in brackets), key=lambda candidate: candidate.loss)
    return HyperbandResult(brackets=tuple(brackets), best=best, total_resource=total_resource)
