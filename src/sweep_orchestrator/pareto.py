"""Multi-objective optimization: Pareto fronts over conflicting objectives.

Real sweeps optimize several objectives at once (accuracy, latency, cost) that
trade off against each other, so there is no single best configuration, only a
set of non-dominated ones: the **Pareto front**. This module implements the two
primitives at the heart of NSGA-II: fast non-dominated sorting into fronts, and
crowding distance to spread solutions along each front.

All objectives are minimized; negate any you want to maximize.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class MultiObjectivePoint:
    """A configuration and the objective vector it achieved (all minimized)."""

    identifier: int
    objectives: tuple[float, ...]


def dominates(left: Sequence[float], right: Sequence[float]) -> bool:
    """Return whether ``left`` Pareto-dominates ``right`` (no worse, strictly better once)."""
    if len(left) != len(right):
        raise ValueError("objective vectors must have the same length")
    no_worse = all(a <= b for a, b in zip(left, right, strict=True))
    strictly_better = any(a < b for a, b in zip(left, right, strict=True))
    return no_worse and strictly_better


def non_dominated_sort(points: Sequence[MultiObjectivePoint]) -> list[list[MultiObjectivePoint]]:
    """Sort points into Pareto fronts (front 0 is non-dominated by anything)."""
    domination_count = {point.identifier: 0 for point in points}
    dominated: dict[int, list[MultiObjectivePoint]] = {point.identifier: [] for point in points}

    for p in points:
        for q in points:
            if p.identifier == q.identifier:
                continue
            if dominates(p.objectives, q.objectives):
                dominated[p.identifier].append(q)
            elif dominates(q.objectives, p.objectives):
                domination_count[p.identifier] += 1

    fronts: list[list[MultiObjectivePoint]] = []
    current = [point for point in points if domination_count[point.identifier] == 0]
    while current:
        fronts.append(current)
        nxt: list[MultiObjectivePoint] = []
        for point in current:
            for dominated_point in dominated[point.identifier]:
                domination_count[dominated_point.identifier] -= 1
                if domination_count[dominated_point.identifier] == 0:
                    nxt.append(dominated_point)
        current = nxt
    return fronts


def pareto_front(points: Sequence[MultiObjectivePoint]) -> list[MultiObjectivePoint]:
    """Return only the first (non-dominated) Pareto front."""
    if not points:
        return []
    return non_dominated_sort(points)[0]


def crowding_distance(front: Sequence[MultiObjectivePoint]) -> dict[int, float]:
    """Assign each point a crowding distance (boundary points get infinity).

    Crowding distance estimates how isolated a solution is on its front, so a
    selector can prefer well-spread solutions over clustered ones.
    """
    size = len(front)
    distance = {point.identifier: 0.0 for point in front}
    if size <= 2:
        return {point.identifier: float("inf") for point in front}

    objective_count = len(front[0].objectives)
    for axis in range(objective_count):
        ordered = sorted(front, key=lambda point: point.objectives[axis])
        low = ordered[0].objectives[axis]
        high = ordered[-1].objectives[axis]
        distance[ordered[0].identifier] = float("inf")
        distance[ordered[-1].identifier] = float("inf")
        span = high - low
        if span == 0:
            continue
        for index in range(1, size - 1):
            previous_value = ordered[index - 1].objectives[axis]
            next_value = ordered[index + 1].objectives[axis]
            distance[ordered[index].identifier] += (next_value - previous_value) / span
    return distance
