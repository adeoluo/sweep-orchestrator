# Evaluation Report - Sweep Orchestrator

> Reproduce with `python -m sweep_orchestrator evaluate`. Deterministic and offline.

## Setup

- **Problem:** the bundled learning-curve sweep with a known optimum.
- **Configurations:** 27 sampled learning-rate and depth settings.
- **Strategies:** full evaluation (no pruning), median pruning, successive halving.
- **Metrics:** best final loss found and total resource (step-evaluations) spent.

## Results

| Strategy | best loss | resource | savings |
|---|---:|---:|---:|
| full (no pruning) | 0.2021 | 243 | 1.00x |
| median pruning | 0.2021 | 90 | 2.70x |
| successive halving | 0.2021 | 81 | 3.00x |

(At 81 configurations the savings grow to 2.87x and 3.00x; see `benchmarks/benchmark.py`.)

## Interpretation

Every strategy finds the same optimal configuration (final loss 0.2021, matching the
ground-truth best), but median pruning and successive halving reach it at roughly a third of
the compute by stopping clearly-losing trials before they consume their full budget. This is
the central claim of multi-fidelity tuning, measured directly: identical solution quality at a
fraction of the cost. The saving grows with the number of configurations, because more losers
can be pruned early.

## Reproducibility

Sampling and single-worker execution are deterministic; the numbers regenerate exactly.
