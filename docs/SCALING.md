# Scaling and Design Tradeoffs - Sweep Orchestrator

How the reference design grows, and the tradeoffs taken.

## Reference architecture (today)

A single process schedules configurations with multi-fidelity brackets and a parallel
early-stopping runner, records trials in a resumable store, and exposes sweeps, importance, and
Pareto fronts over a standard-library HTTP service. Deterministic in single-worker mode.

## Scaling path

| Stage | Bottleneck | Change |
|---|---|---|
| One process | CPU, global interpreter lock | One replica per core for CPU-bound objectives |
| Real training objectives | Objective cost, not the orchestrator | Overlap waiting with the worker pool; add remote workers |
| Cross-machine execution | In-process threads | Asynchronous successive halving (ASHA) over distributed workers |
| Durable sweeps | In-memory store | Persist the resumable store; resume on restart |
| Large Pareto sets | Pairwise non-dominated sorting | Use the linear-time NSGA-II front construction |

## Substantial tradeoffs

- **Multi-fidelity vs full evaluation.** Early stopping saves roughly a measured factor of
  three in compute at no loss of solution quality, at the cost of assuming intermediate values
  rank configurations. When that assumption fails (losers do not separate early), pruning is
  unsafe; the project documents this rather than hiding it.
- **Pareto front vs a weighted sum.** A front exposes the real tradeoff surface and never bakes
  in a weighting, at the cost of returning a set the caller must choose from. A weighted sum is
  a single number but hides the tradeoff and misses non-convex regions.
- **Threads vs processes vs remote workers.** In-process threads overlap waiting for real
  objectives but do not add CPU throughput; processes scale CPU-bound orchestration; remote
  workers (ASHA) scale across machines at the cost of a transport and fault handling.
- **Synchronous brackets vs asynchronous promotion.** Synchronous successive halving is simple
  and reproducible but idles fast trials waiting for slow ones; ASHA promotes asynchronously for
  better utilization at the cost of determinism.

## What would change under real load

Persist the store, run process-per-core replicas for CPU-bound work, and move to asynchronous
successive halving across remote workers for real training objectives. The schedulers, the
pruner, and the analysis are unchanged; only the execution substrate changes.
