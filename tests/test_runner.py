"""Tests for the pruners, the parallel runner, and the evaluation."""

from __future__ import annotations

import pytest

from sweep_orchestrator import (
    MedianPruner,
    NoPruner,
    SweepRunner,
    format_table,
    run_evaluation,
)
from sweep_orchestrator.cli import main
from sweep_orchestrator.data import learning_curve, sample_configurations


def test_median_pruner_stops_clear_losers() -> None:
    pruner = MedianPruner(n_warmup=0, min_peers=3)
    # A value worse than every peer at a step is pruned.
    assert pruner.should_prune(step=1, value=10.0, peers=[1.0, 2.0, 3.0])
    assert not pruner.should_prune(step=1, value=0.5, peers=[1.0, 2.0, 3.0])


def test_median_pruner_respects_warmup_and_min_peers() -> None:
    pruner = MedianPruner(n_warmup=2, min_peers=3)
    assert not pruner.should_prune(step=0, value=100.0, peers=[1.0, 2.0, 3.0])
    assert not pruner.should_prune(step=5, value=100.0, peers=[1.0])


def test_median_pruner_validates() -> None:
    with pytest.raises(ValueError):
        MedianPruner(n_warmup=-1)
    with pytest.raises(ValueError):
        MedianPruner(min_peers=0)


def test_runner_without_pruning_completes_all() -> None:
    configs = sample_configurations(10)
    store = SweepRunner(steps=9, pruner=NoPruner()).run(configs, learning_curve)
    assert len(store.records) == 10
    assert all(not record.pruned for record in store.records.values())


def test_runner_prunes_some_trials() -> None:
    configs = sample_configurations(27)
    store = SweepRunner(steps=9, pruner=MedianPruner(n_warmup=1, min_peers=3)).run(
        configs, learning_curve
    )
    pruned = [record for record in store.records.values() if record.pruned]
    assert pruned  # some clear losers are stopped early
    # The best trial is never pruned.
    assert not store.best().pruned


def test_runner_validates() -> None:
    with pytest.raises(ValueError):
        SweepRunner(steps=0)
    with pytest.raises(ValueError):
        SweepRunner(steps=5, max_workers=0)


def test_parallel_runner_matches_sequential_best() -> None:
    configs = sample_configurations(20)
    sequential = SweepRunner(steps=9, max_workers=1).run(configs, learning_curve).best().value
    parallel = SweepRunner(steps=9, max_workers=4).run(configs, learning_curve).best().value
    assert sequential == parallel


def test_evaluation_pruning_is_cheaper_but_as_good() -> None:
    results = {r.strategy: r for r in run_evaluation(count=27)}
    full = results["full (no pruning)"]
    pruned = results["median pruning"]
    halving = results["successive halving"]
    assert pruned.resource < full.resource
    assert halving.resource < full.resource
    # Early stopping still finds a configuration as good as the full sweep.
    assert pruned.best_loss <= full.best_loss + 1e-9
    assert halving.best_loss <= full.best_loss + 1e-9


def test_cli_commands(capsys) -> None:
    main(["evaluate", "--count", "27"])
    assert "successive halving" in capsys.readouterr().out
    main(["importance", "--count", "40"])
    assert "explained variance" in capsys.readouterr().out
    main(["pareto"])
    assert "Pareto" in capsys.readouterr().out


def test_format_table_contents() -> None:
    table = format_table(run_evaluation(count=27))
    assert "median pruning" in table
    assert "resource" in table
