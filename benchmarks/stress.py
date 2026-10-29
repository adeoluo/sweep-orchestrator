"""A production-style stress benchmark for the sweep service.

Drives the full sweep handler under sustained, concurrent load (each request runs
a complete sweep comparison) and reports throughput with p50, p95, and p99
latency. Deterministic and offline; run with:

    uv run python benchmarks/stress.py
"""

from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from sweep_orchestrator.service import SweepService, handle


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main() -> None:
    service = SweepService()
    requests = [{"count": 27} for _ in range(400)]

    def one(body: dict[str, object]) -> float:
        start = time.perf_counter()
        handle("POST", "/sweep", body, service)
        return (time.perf_counter() - start) * 1000

    print(f"Requests: {len(requests)} (each runs a full three-strategy sweep)")
    for workers in (1, 4, 8):
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            latencies = list(pool.map(one, requests))
        wall = time.perf_counter() - start
        print(
            f"workers={workers:<2}  "
            f"throughput={len(requests) / wall:>7.0f} req/s  "
            f"p50={statistics.median(latencies):>6.2f} ms  "
            f"p95={_percentile(latencies, 0.95):>6.2f} ms  "
            f"p99={_percentile(latencies, 0.99):>6.2f} ms"
        )


if __name__ == "__main__":
    main()
