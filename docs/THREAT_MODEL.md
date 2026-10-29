# Threat Model - Sweep Orchestrator

## Assets

- Integrity of the scheduling decisions, the Pareto front, and the reported savings.

## Trust boundaries

- **Counts and objective vectors are untrusted input to the service.** They are validated for
  type and bounds; the objective is a bundled function, never caller-supplied code over the wire.

## Threats and mitigations

| Threat | Vector | Impact | Mitigation |
|---|---|---|---|
| Unbounded compute | Huge configuration count | Resource exhaustion | Count bounded (service caps at 243) |
| Malformed objective vectors | Ragged or non-numeric points | Crash | Point validation (shape and type) |
| Irreproducible sweeps | Unseeded sampling | Flaky numbers | Deterministic sampling and single-worker mode |
| Supply-chain compromise | Malicious dependency | Code execution | Zero runtime dependencies; Dependabot and CodeQL in continuous integration |

## Residual risk

The parallel runner uses threads within one process, so a crash loses in-memory state; the
resumable store is the basis for durable, restartable sweeps, left as a roadmap item.
