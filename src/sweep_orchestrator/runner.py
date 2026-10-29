"""The parallel sweep runner: execute trials concurrently with pruning.

The runner evaluates many configurations, each reporting intermediate values over
a sequence of steps. It runs trials in a worker pool, consults a pruner to stop
clearly-losing trials early, and records every trial (including pruned ones) in a
resumable store. A deterministic single-worker mode keeps results reproducible for
tests; the thread pool is used only to overlap evaluations.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from sweep_orchestrator.pruning import NoPruner, Pruner
from sweep_orchestrator.types import Configuration

# A step objective yields a trial's intermediate value at each step (lower is better).
StepObjective = Callable[[Mapping[str, float], int], float]


@dataclass(frozen=True)
class TrialRecord:
    """The record of one executed trial, pruned or complete."""

    identifier: int
    configuration: Configuration
    value: float
    last_step: int
    pruned: bool
    history: tuple[float, ...] = field(default_factory=tuple)


@dataclass
class SweepStore:
    """A resumable record of a sweep's trials, keyed by trial identifier."""

    records: dict[int, TrialRecord] = field(default_factory=dict)

    def add(self, record: TrialRecord) -> None:
        self.records[record.identifier] = record

    @property
    def completed(self) -> list[TrialRecord]:
        return [record for record in self.records.values() if not record.pruned]

    def best(self) -> TrialRecord:
        if not self.records:
            raise ValueError("the sweep has no trials")
        return min(self.records.values(), key=lambda record: record.value)


class SweepRunner:
    """Runs configurations to completion or early-stopping under a pruner."""

    def __init__(
        self,
        *,
        steps: int,
        pruner: Pruner | None = None,
        max_workers: int = 1,
    ) -> None:
        if steps < 1:
            raise ValueError("steps must be at least 1")
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        self._steps = steps
        self._pruner = pruner or NoPruner()
        self._max_workers = max_workers

    def run(self, configurations: Sequence[Configuration], objective: StepObjective) -> SweepStore:
        """Execute every configuration, pruning clear losers, into a store."""
        store = SweepStore()
        # Peer values at each step, accumulated as trials report, for the pruner.
        peers: list[list[float]] = [[] for _ in range(self._steps)]

        def evaluate(item: tuple[int, Configuration]) -> TrialRecord:
            identifier, configuration = item
            history: list[float] = []
            value = float("inf")
            last_step = 0
            for step in range(self._steps):
                value = objective(configuration, step)
                history.append(value)
                last_step = step
                if self._pruner.should_prune(step, value, peers[step]):
                    peers[step].append(value)
                    return TrialRecord(
                        identifier=identifier,
                        configuration=dict(configuration),
                        value=value,
                        last_step=last_step,
                        pruned=True,
                        history=tuple(history),
                    )
                peers[step].append(value)
            return TrialRecord(
                identifier=identifier,
                configuration=dict(configuration),
                value=value,
                last_step=last_step,
                pruned=False,
                history=tuple(history),
            )

        items = list(enumerate(configurations))
        if self._max_workers == 1:
            records = [evaluate(item) for item in items]
        else:
            with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
                records = list(pool.map(evaluate, items))
        for record in records:
            store.add(record)
        return store
