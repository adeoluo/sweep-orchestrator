"""Tests for the multi-fidelity schedulers."""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence

import pytest

from sweep_orchestrator import Configuration, hyperband, successive_halving


def _objective(config: Mapping[str, float], resource: int) -> float:
    # A configuration's true loss is (x - 2)^2; higher resource reduces evaluation noise.
    true_loss = (float(config["x"]) - 2.0) ** 2
    noise = (1.0 / resource) * math.sin(float(config["x"]) * 10.0)
    return true_loss + noise


def _configs(count: int, *, seed: int = 0) -> list[Configuration]:
    rng = random.Random(seed)
    return [{"x": rng.uniform(-5.0, 5.0)} for _ in range(count)]


def test_successive_halving_finds_a_good_configuration() -> None:
    result = successive_halving(_configs(27), _objective, min_resource=1, max_resource=9, eta=3)
    assert abs(result.best.configuration["x"] - 2.0) < 1.0
    # Rungs should shrink as resource grows.
    sizes = [len(rung.survivors) for rung in result.rungs]
    assert sizes == sorted(sizes, reverse=True)


def test_successive_halving_cheaper_than_full_evaluation() -> None:
    configs = _configs(27)
    result = successive_halving(configs, _objective, min_resource=1, max_resource=9, eta=3)
    full_cost = len(configs) * 9
    assert result.total_resource < full_cost


def test_successive_halving_validates() -> None:
    with pytest.raises(ValueError):
        successive_halving(_configs(4), _objective, min_resource=1, max_resource=9, eta=1)
    with pytest.raises(ValueError):
        successive_halving([], _objective, min_resource=1, max_resource=9)
    with pytest.raises(ValueError):
        successive_halving(_configs(4), _objective, min_resource=0, max_resource=9)


def test_hyperband_runs_multiple_brackets() -> None:
    def sampler(count: int) -> Sequence[Configuration]:
        return _configs(count, seed=count)

    result = hyperband(sampler, _objective, max_resource=9, eta=3)
    assert len(result.brackets) >= 2
    assert abs(result.best.configuration["x"] - 2.0) < 1.0


def test_hyperband_bracket_count_matches_exact_powers() -> None:
    # Regression: math.log(eta**k, eta) can be slightly below k (for example
    # log(243, 3) == 4.999999999999999), which dropped the most aggressive
    # bracket. For R = eta**k the run must have exactly k + 1 brackets.
    def sampler(count: int) -> Sequence[Configuration]:
        return _configs(count, seed=count)

    for eta in (2, 3, 5, 10):
        for k in range(0, 5):
            max_resource = eta**k
            result = hyperband(sampler, _objective, max_resource=max_resource, eta=eta)
            assert len(result.brackets) == k + 1, (eta, k, max_resource)


def test_hyperband_validates() -> None:
    with pytest.raises(ValueError):
        hyperband(lambda n: _configs(n), _objective, max_resource=9, eta=1)
    with pytest.raises(ValueError):
        hyperband(lambda n: _configs(n), _objective, max_resource=0)
