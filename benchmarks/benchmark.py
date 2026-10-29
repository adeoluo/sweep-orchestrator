"""A deterministic micro-benchmark for the sweep strategies.

Measures the compute (step-evaluations) and best loss reached by full evaluation,
median pruning, and successive halving on the bundled learning-curve problem, so
the README can quote concrete numbers. Deterministic and offline; run with:

    uv run python benchmarks/benchmark.py
"""

from __future__ import annotations

import time

from sweep_orchestrator.evaluation import ground_truth_best, run_evaluation


def main() -> None:
    count = 81
    start = time.perf_counter()
    results = run_evaluation(count=count)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"Configurations: {count} | wall time: {elapsed_ms:.1f} ms")
    print(f"Ground-truth best final loss: {ground_truth_best(count=count):.4f}\n")
    print(f"{'strategy':<22}{'best loss':>12}{'resource':>12}{'savings':>10}")
    print("-" * 56)
    full = next(r for r in results if r.strategy == "full (no pruning)")
    for result in results:
        savings = full.resource / result.resource
        print(
            f"{result.strategy:<22}{result.best_loss:>12.4f}{result.resource:>12}{savings:>9.2f}x"
        )


if __name__ == "__main__":
    main()
