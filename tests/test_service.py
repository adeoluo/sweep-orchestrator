"""Tests for the dependency-free HTTP sweep service (pure handler layer)."""

from __future__ import annotations

from sweep_orchestrator.service import SweepService, handle

_SERVICE = SweepService()


def test_health() -> None:
    status, payload = handle("GET", "/health", {}, _SERVICE)
    assert status == 200
    assert payload["status"] == "ok"
    assert "successive halving" in payload["strategies"]


def test_sweep_pruning_is_cheaper() -> None:
    status, payload = handle("POST", "/sweep", {"count": 27}, _SERVICE)
    assert status == 200
    by = {row["strategy"]: row for row in payload["strategies"]}
    assert by["median pruning"]["resource"] < by["full (no pruning)"]["resource"]
    assert by["successive halving"]["resource"] < by["full (no pruning)"]["resource"]


def test_importance_ranks_learning_rate_first() -> None:
    status, payload = handle("POST", "/importance", {"count": 64}, _SERVICE)
    assert status == 200
    assert payload["importances"][0]["parameter"] == "log_learning_rate"


def test_pareto_marks_dominated() -> None:
    status, payload = handle(
        "POST", "/pareto", {"points": [[0.1, 0.9], [0.5, 0.5], [0.9, 0.1], [0.6, 0.6]]}, _SERVICE
    )
    assert status == 200
    assert payload["dominated"] == [3]
    assert len(payload["front"]) == 3


def test_sweep_rejects_bad_count() -> None:
    status, payload = handle("POST", "/sweep", {"count": 1}, _SERVICE)
    assert status == 400
    assert "count" in payload["error"]


def test_pareto_rejects_malformed_points() -> None:
    status, _ = handle("POST", "/pareto", {"points": []}, _SERVICE)
    assert status == 400
    status, _ = handle("POST", "/pareto", {"points": [[0.1, 0.2], [0.3]]}, _SERVICE)
    assert status == 400
    status, _ = handle("POST", "/pareto", {"points": [["a", "b"]]}, _SERVICE)
    assert status == 400


def test_unknown_route() -> None:
    status, payload = handle("GET", "/nope", {}, _SERVICE)
    assert status == 404
    assert "error" in payload
