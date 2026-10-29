# Operations Guide - Sweep Orchestrator

The operational contract of the sweep service.

## Running the service

```bash
uv run python -m sweep_orchestrator serve --host 0.0.0.0 --port 8000
```

A standard-library HTTP server with **zero runtime dependencies**.

## Endpoints

| Method | Path | Body | Success |
|---|---|---|---|
| GET | `/health` | none | status and available strategies |
| GET | `/ready` | none | readiness of the orchestrator |
| GET | `/metrics` | none | per-route request, error, and latency metrics (Prometheus text) |
| POST | `/sweep` | `{"count"?}` | best loss and resource for each strategy |
| POST | `/importance` | `{"count"?}` | parameters ranked by variance explained |
| POST | `/pareto` | `{"points": [[...], ...]}` | the Pareto front and the dominated set |

Errors return JSON `{"error": ...}` with a 4xx status. `count` and the number of points are
bounded.

## Service level objectives

Measured by `benchmarks/stress.py` (each request runs a full three-strategy sweep over 27
configurations) on a developer laptop:

| Objective | Target | Observed (single worker) |
|---|---|---|
| Sweep latency p50 | < 1 ms | about 0.25 ms |
| Sweep latency p99 (1 worker) | < 1 ms | about 0.42 ms |
| Throughput (1 worker) | > 1000 sweeps/second | about 3700/second |

Observed with the simulated objective; a real training objective would dominate the time and
is the reason the orchestrator prunes.

## Operational constraints

- **The orchestration is CPU bound and holds the global interpreter lock.** The internal
  worker pool overlaps evaluations within a process but does not add throughput for a
  CPU-bound objective; scale the service with **processes**. For a real objective (training
  runs), the pool overlaps the waiting, which is where parallelism pays off.
- **The runner's state is in memory.** The resumable store records every trial, but durability
  across a crash would require persisting it; cross-machine execution needs a transport.
- **Requests are bounded**: the configuration count is capped (243) and the Pareto point list
  is capped, so a single request cannot exhaust resources.
- **Sweeps are deterministic** under the bundled sampler, so results are reproducible and
  cacheable by configuration count.
- **No persistence, no authentication.** Front the service with a gateway.

## Failure modes and responses

| Symptom | Likely cause | Response |
|---|---|---|
| No savings from pruning | Objective where losers do not separate early | Expected; multi-fidelity needs informative intermediate values |
| Rising p99 under load | Concurrency above one worker per core | Add replicas; cap concurrency |
| `400` on sweep/pareto | Count out of range or malformed points | Inspect the `error` field |

## Capacity planning

For the simulated objective, a single core serves thousands of sweeps per second. For real
training objectives, capacity is set by the objective's cost, which the pruner reduces by
roughly the measured savings factor.
