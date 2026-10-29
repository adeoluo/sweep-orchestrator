"""Successive halving: the core multi-fidelity primitive.

Given a set of candidate configurations and a minimum resource level, evaluate
all of them cheaply, keep the best ``1 / eta`` fraction, multiply the resource by
``eta``, and repeat. Most configurations are discarded early at low cost, so the
total compute to find a good configuration is far below evaluating them all at
full resource. This is the engine inside Hyperband and ASHA.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from sweep_orchestrator.types import Candidate, Configuration, Objective


@dataclass(frozen=True)
class Rung:
    """One level of a successive-halving ladder: a resource and its survivors."""

    resource: int
    survivors: tuple[Candidate, ...]


@dataclass(frozen=True)
class BracketResult:
    """The outcome of one successive-halving bracket."""

    rungs: tuple[Rung, ...]
    best: Candidate
    total_resource: int


def successive_halving(
    configurations: Sequence[Configuration],
    objective: Objective,
    *,
    min_resource: int,
    max_resource: int,
    eta: int = 3,
) -> BracketResult:
    """Run successive halving over ``configurations`` and return the best candidate."""
    if eta < 2:
        raise ValueError("eta must be at least 2")
    if min_resource < 1 or max_resource < min_resource:
        raise ValueError("require 1 <= min_resource <= max_resource")
    if not configurations:
        raise ValueError("need at least one configuration")

    candidates = [
        Candidate(identifier=index, configuration=dict(config))
        for index, config in enumerate(configurations)
    ]
    rungs: list[Rung] = []
    total_resource = 0
    resource = min_resource

    while True:
        evaluated = [
            Candidate(
                identifier=candidate.identifier,
                configuration=candidate.configuration,
                loss=objective(candidate.configuration, resource),
                resource=resource,
            )
            for candidate in candidates
        ]
        total_resource += resource * len(evaluated)
        evaluated.sort(key=lambda candidate: candidate.loss)
        rungs.append(Rung(resource=resource, survivors=tuple(evaluated)))

        if resource >= max_resource or len(evaluated) == 1:
            break
        keep = max(1, math.floor(len(evaluated) / eta))
        candidates = evaluated[:keep]
        resource = min(max_resource, resource * eta)

    best = min((rung.survivors[0] for rung in rungs), key=lambda candidate: candidate.loss)
    return BracketResult(rungs=tuple(rungs), best=best, total_resource=total_resource)
