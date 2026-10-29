"""A dependency-free HTTP service exposing the sweep orchestrator.

The service runs a sweep over the bundled learning-curve problem with a chosen
strategy, reports the best configuration and the compute spent, or returns a
Pareto front or a hyperparameter-importance ranking. A pure handler is separated
from the socket binding for testing.

Endpoints
---------
``GET  /health``       liveness and available strategies.
``POST /sweep``        body ``{"count"?: int}``; compares full, pruned, and
                       multi-fidelity sweeps and reports best loss and resource.
``POST /importance``   body ``{"count"?: int}``; ranks parameters by variance.
``POST /pareto``       body ``{"points": [[o1, o2], ...]}``; returns the front.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from sweep_orchestrator.data import final_loss, sample_configurations
from sweep_orchestrator.evaluation import ground_truth_best, run_evaluation
from sweep_orchestrator.importance import Observation, parameter_importance
from sweep_orchestrator.observability import ServiceMetrics
from sweep_orchestrator.pareto import MultiObjectivePoint, pareto_front

JsonObject = dict[str, Any]
_MAX_COUNT = 243
_MAX_POINTS = 500


@dataclass(frozen=True)
class SweepService:
    """Runs sweeps, importance analysis, and Pareto fronts over bundled problems."""

    strategies: tuple[str, ...] = ("full (no pruning)", "median pruning", "successive halving")
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)

    def sweep(self, count: int) -> JsonObject:
        results = run_evaluation(count=count)
        return {
            "count": count,
            "ground_truth_best": round(ground_truth_best(count=count), 6),
            "strategies": [
                {
                    "strategy": result.strategy,
                    "best_loss": round(result.best_loss, 6),
                    "resource": result.resource,
                }
                for result in results
            ],
        }

    def importance(self, count: int) -> JsonObject:
        configs = sample_configurations(count)
        observations = [Observation(config, final_loss(config)) for config in configs]
        ranked = parameter_importance(observations)
        return {
            "count": count,
            "importances": [
                {
                    "parameter": item.parameter,
                    "explained_variance": round(item.explained_variance, 6),
                }
                for item in ranked
            ],
        }

    def pareto(self, points: Sequence[Sequence[float]]) -> JsonObject:
        multi = [
            MultiObjectivePoint(index, tuple(float(value) for value in point))
            for index, point in enumerate(points)
        ]
        front = pareto_front(multi)
        front_ids = {point.identifier for point in front}
        return {
            "front": [
                {"identifier": point.identifier, "objectives": list(point.objectives)}
                for point in front
            ],
            "dominated": sorted(
                point.identifier for point in multi if point.identifier not in front_ids
            ),
        }


def _count(body: Mapping[str, Any]) -> int:
    count = body.get("count", 27)
    if not isinstance(count, int) or not 2 <= count <= _MAX_COUNT:
        raise ValueError(f"'count' must be an integer in [2, {_MAX_COUNT}]")
    return count


def _points(body: Mapping[str, Any]) -> list[list[float]]:
    points = body.get("points")
    if not isinstance(points, list) or not points or len(points) > _MAX_POINTS:
        raise ValueError(f"'points' must be a non-empty list of at most {_MAX_POINTS} vectors")
    first_length = None
    parsed: list[list[float]] = []
    for point in points:
        if not isinstance(point, list) or not point:
            raise ValueError("each point must be a non-empty list of numbers")
        if first_length is None:
            first_length = len(point)
        elif len(point) != first_length:
            raise ValueError("all points must have the same number of objectives")
        if not all(isinstance(value, int | float) for value in point):
            raise ValueError("objective values must be numbers")
        parsed.append([float(value) for value in point])
    return parsed


def _route(
    method: str, path: str, body: Mapping[str, Any], service: SweepService
) -> tuple[int, JsonObject]:
    if method == "GET" and path == "/health":
        return 200, {"status": "ok", "strategies": list(service.strategies)}
    if method == "POST" and path == "/sweep":
        try:
            count = _count(body)
        except ValueError as error:
            return 400, {"error": str(error)}
        return 200, service.sweep(count)
    if method == "POST" and path == "/importance":
        try:
            count = _count(body)
        except ValueError as error:
            return 400, {"error": str(error)}
        return 200, service.importance(count)
    if method == "POST" and path == "/pareto":
        try:
            points = _points(body)
        except ValueError as error:
            return 400, {"error": str(error)}
        return 200, service.pareto(points)
    return 404, {"error": f"no route for {method} {path}"}


def handle(
    method: str, path: str, body: Mapping[str, Any], service: SweepService
) -> tuple[int, JsonObject]:
    """Route a request, recording per-route metrics, and return status and payload."""

    if method == "GET" and path == "/ready":
        return 200, {"status": "ready"}
    start = time.perf_counter()
    status, payload = _route(method, path, body, service)
    service.metrics.observe(
        f"{method} {path}", (time.perf_counter() - start) * 1000.0, error=status >= 400
    )
    return status, payload


class _Handler(BaseHTTPRequestHandler):  # pragma: no cover - exercised over sockets
    service: SweepService

    def _respond(self, status: int, payload: JsonObject) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/metrics":
            body = self.service.metrics.render_prometheus().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        status, payload = handle("GET", self.path, {}, self.service)
        self._respond(status, payload)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._respond(400, {"error": "request body is not valid JSON"})
            return
        status, payload = handle("POST", self.path, body, self.service)
        self._respond(status, payload)

    def log_message(self, *_: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:  # pragma: no cover
    """Start the HTTP service (blocking)."""

    handler = type("_BoundHandler", (_Handler,), {"service": SweepService()})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"sweep-orchestrator service listening on http://{host}:{port}")
    server.serve_forever()
