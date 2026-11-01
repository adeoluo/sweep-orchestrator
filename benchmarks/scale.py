"""A large-workload scale benchmark for successive-halving scheduling.

Runs the multi-fidelity successive-halving scheduler on progressively larger pools
of synthetic configurations and reports, per workload, the wall-clock time,
throughput in configurations per second, the peak traced memory, the simple regret
of the selected configuration against the ground-truth best, and the compute saved
versus a full no-pruning sweep. It complements ``benchmark.py`` (a fixed 81-config
comparison) by showing how the scheduler scales as the pool of candidates grows.

Timing and memory are captured in separate phases on purpose: ``tracemalloc``
instruments every allocation and perturbs the wall-clock, while the peak footprint
is governed by the resident configuration pool rather than the schedule, so a short
traced pass measures it faithfully. Deterministic and offline; run with:

    uv run python benchmarks/scale.py
"""

from __future__ import annotations

import time
import tracemalloc
from collections.abc import Mapping
from dataclasses import dataclass

from sweep_orchestrator.data import STEPS, final_loss, learning_curve, sample_configurations
from sweep_orchestrator.successive_halving import successive_halving

WORKLOADS: tuple[int, ...] = (243, 729, 2187, 6561)
_SEED = 0


def _objective(configuration: Mapping[str, float], resource: int) -> float:
    return learning_curve(configuration, min(resource, STEPS) - 1)


@dataclass(frozen=True)
class ScalePoint:
    """One row of the scale table for a single workload size."""

    size: int
    seconds: float
    throughput: float
    peak_mib: float
    regret: float
    savings: float


def measure(size: int, *, seed: int = _SEED) -> ScalePoint:
    """Schedule ``size`` configurations with successive halving and measure the cost."""

    tracemalloc.start()
    tracemalloc.reset_peak()
    configurations = sample_configurations(size, seed=seed)
    successive_halving(configurations, _objective, min_resource=1, max_resource=STEPS, eta=3)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    start = time.perf_counter()
    bracket = successive_halving(
        configurations, _objective, min_resource=1, max_resource=STEPS, eta=3
    )
    seconds = time.perf_counter() - start

    ground_truth = min(final_loss(config) for config in configurations)
    return ScalePoint(
        size=size,
        seconds=seconds,
        throughput=size / seconds if seconds > 0 else 0.0,
        peak_mib=peak / 1048576,
        regret=bracket.best.loss - ground_truth,
        savings=(size * STEPS) / bracket.total_resource,
    )


def main() -> None:
    print("Synthetic learning-curve objective; a pure-Python, from-scratch scheduler.")
    print("Wall-clock is not competitive with compiled numerical libraries.")
    print("Regret is the selected configuration's loss minus the ground-truth best.\n")

    header = f"{'configs':>8}  {'seconds':>8}  {'configs/sec':>12}  {'peak MiB':>9}"
    print(f"{header}  {'regret':>10}  {'savings':>8}")
    for size in WORKLOADS:
        point = measure(size)
        print(
            f"{point.size:>8}  {point.seconds:>8.4f}  {point.throughput:>12.0f}  "
            f"{point.peak_mib:>9.2f}  {point.regret:>10.4f}  {point.savings:>7.2f}x"
        )


if __name__ == "__main__":
    main()
