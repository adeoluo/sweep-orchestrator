"""Core types for sweeps: configurations, trials, and objective callables.

A configuration is a mapping from parameter name to value. A trial evaluates a
configuration at a given *resource level* (for example a number of training
epochs) and reports a scalar loss (lower is better). Multi-fidelity schedulers
run many configurations cheaply and promote only the promising ones to higher
resource levels.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

Configuration = dict[str, float]

# Evaluate a configuration at a resource level, returning a loss (lower is better).
Objective = Callable[[Mapping[str, float], int], float]


@dataclass(frozen=True)
class TrialResult:
    """The outcome of evaluating one configuration at one resource level."""

    configuration: Configuration
    resource: int
    loss: float


@dataclass(frozen=True)
class Candidate:
    """A configuration carried through the rungs of a multi-fidelity schedule."""

    identifier: int
    configuration: Configuration
    loss: float = float("inf")
    resource: int = 0
