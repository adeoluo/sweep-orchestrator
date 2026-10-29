"""Tests for Pareto fronts, crowding distance, and importance analysis."""

from __future__ import annotations

import random

import pytest

from sweep_orchestrator import (
    MultiObjectivePoint,
    Observation,
    crowding_distance,
    dominates,
    non_dominated_sort,
    parameter_importance,
    pareto_front,
)


def test_dominates() -> None:
    assert dominates((1.0, 1.0), (2.0, 2.0))
    assert dominates((1.0, 2.0), (1.0, 3.0))
    assert not dominates((1.0, 3.0), (2.0, 2.0))  # a tradeoff: neither dominates
    with pytest.raises(ValueError):
        dominates((1.0,), (1.0, 2.0))


def test_pareto_front_identifies_tradeoffs() -> None:
    points = [
        MultiObjectivePoint(0, (0.1, 0.9)),  # accurate, slow
        MultiObjectivePoint(1, (0.5, 0.5)),  # balanced
        MultiObjectivePoint(2, (0.9, 0.1)),  # fast, inaccurate
        MultiObjectivePoint(3, (0.6, 0.6)),  # dominated by point 1
    ]
    front = {point.identifier for point in pareto_front(points)}
    assert front == {0, 1, 2}
    assert 3 not in front


def test_non_dominated_sort_layers() -> None:
    points = [
        MultiObjectivePoint(0, (0.0, 0.0)),
        MultiObjectivePoint(1, (1.0, 1.0)),
        MultiObjectivePoint(2, (2.0, 2.0)),
    ]
    fronts = non_dominated_sort(points)
    assert [p.identifier for p in fronts[0]] == [0]
    assert len(fronts) == 3


def test_crowding_distance_boundaries_are_infinite() -> None:
    front = [
        MultiObjectivePoint(0, (0.0, 1.0)),
        MultiObjectivePoint(1, (0.5, 0.5)),
        MultiObjectivePoint(2, (1.0, 0.0)),
    ]
    distances = crowding_distance(front)
    assert distances[0] == float("inf")
    assert distances[2] == float("inf")
    assert distances[1] < float("inf")


def test_importance_ranks_the_relevant_parameter_first() -> None:
    # Objective depends strongly on x and not at all on y.
    rng = random.Random(0)
    observations = []
    for _ in range(80):
        x = rng.uniform(0.0, 1.0)
        y = rng.uniform(0.0, 1.0)
        observations.append(Observation({"x": x, "y": y}, objective=(x - 0.5) ** 2))
    importances = parameter_importance(observations)
    assert importances[0].parameter == "x"
    assert importances[0].explained_variance > importances[1].explained_variance


def test_importance_validates() -> None:
    with pytest.raises(ValueError):
        parameter_importance([Observation({"x": 1.0}, 1.0)])
