"""Sweep Orchestrator - multi-fidelity scheduling and multi-objective sweeps from scratch."""

from __future__ import annotations

from sweep_orchestrator.evaluation import StrategyResult, format_table, run_evaluation
from sweep_orchestrator.hyperband import HyperbandResult, hyperband
from sweep_orchestrator.importance import (
    Importance,
    Observation,
    format_importance,
    parameter_importance,
)
from sweep_orchestrator.pareto import (
    MultiObjectivePoint,
    crowding_distance,
    dominates,
    non_dominated_sort,
    pareto_front,
)
from sweep_orchestrator.pruning import MedianPruner, NoPruner, Pruner
from sweep_orchestrator.runner import SweepRunner, SweepStore, TrialRecord
from sweep_orchestrator.successive_halving import BracketResult, Rung, successive_halving
from sweep_orchestrator.types import Candidate, Configuration, Objective, TrialResult

__version__ = "0.1.0"

__all__ = [
    "BracketResult",
    "Candidate",
    "Configuration",
    "HyperbandResult",
    "Importance",
    "MedianPruner",
    "MultiObjectivePoint",
    "NoPruner",
    "Objective",
    "Observation",
    "Pruner",
    "Rung",
    "StrategyResult",
    "SweepRunner",
    "SweepStore",
    "TrialRecord",
    "TrialResult",
    "__version__",
    "crowding_distance",
    "dominates",
    "format_importance",
    "format_table",
    "hyperband",
    "non_dominated_sort",
    "parameter_importance",
    "pareto_front",
    "run_evaluation",
    "successive_halving",
]
