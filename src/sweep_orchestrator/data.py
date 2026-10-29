"""A bundled, deterministic sweep problem used for demonstrations and evaluation.

The objective mimics training curves: each configuration has a true final loss
determined by its parameters, and a learning curve that approaches that loss over
steps with configuration-dependent speed. Good configurations separate from bad
ones early, which is exactly what makes early stopping pay off.
"""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence

from sweep_orchestrator.types import Configuration

STEPS = 9


def sample_configurations(count: int, *, seed: int = 0) -> list[Configuration]:
    """Sample ``count`` configurations of a learning-rate and depth problem."""
    rng = random.Random(seed)
    configurations: list[Configuration] = []
    for _ in range(count):
        log_learning_rate = rng.uniform(-4.0, -1.0)
        depth = rng.uniform(1.0, 8.0)
        configurations.append({"log_learning_rate": log_learning_rate, "depth": depth})
    return configurations


def _final_loss(configuration: Mapping[str, float]) -> float:
    # Best around log learning rate -2.5 and depth 4; a smooth bowl.
    lr_penalty = (float(configuration["log_learning_rate"]) + 2.5) ** 2
    depth_penalty = 0.05 * (float(configuration["depth"]) - 4.0) ** 2
    return 0.1 + lr_penalty + depth_penalty


def learning_curve(configuration: Mapping[str, float], step: int) -> float:
    """The intermediate loss at ``step`` (0-indexed), approaching the final loss."""
    final = _final_loss(configuration)
    # Faster-decaying curve for lower-loss configurations, so rank is visible early.
    progress = 1.0 - math.exp(-(step + 1) / 3.0)
    start = final + 2.0
    return start + (final - start) * progress


def final_loss(configuration: Mapping[str, float]) -> float:
    """The loss a configuration reaches at the final step (the ground truth)."""
    return learning_curve(configuration, STEPS - 1)


def best_possible(configurations: Sequence[Configuration]) -> float:
    """The lowest final loss among the given configurations."""
    return min(final_loss(configuration) for configuration in configurations)
