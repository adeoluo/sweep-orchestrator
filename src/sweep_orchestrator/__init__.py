"""Sweep Orchestrator - multi-fidelity scheduling and multi-objective sweeps from scratch."""

from __future__ import annotations

from sweep_orchestrator.hyperband import HyperbandResult, hyperband
from sweep_orchestrator.successive_halving import BracketResult, Rung, successive_halving
from sweep_orchestrator.types import Candidate, Configuration, Objective, TrialResult

__version__ = "0.1.0"

__all__ = [
    "BracketResult",
    "Candidate",
    "Configuration",
    "HyperbandResult",
    "Objective",
    "Rung",
    "TrialResult",
    "__version__",
    "hyperband",
    "successive_halving",
]
