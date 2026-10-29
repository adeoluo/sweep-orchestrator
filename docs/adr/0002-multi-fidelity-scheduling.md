# ADR-0002: Multi-fidelity scheduling as the core

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

The dominant cost in a hyperparameter sweep is evaluating configurations that were never going
to win. Reducing that waste is the biggest lever available to an orchestrator.

## Decision

Make multi-fidelity scheduling the core: successive halving evaluates many configurations at a
low resource, keeps the best fraction, and promotes them to higher resource; Hyperband hedges
over the pruning aggressiveness by running several brackets. A median pruner provides the same
early-stopping idea for the asynchronous parallel runner.

## Alternatives considered

- **Full evaluation of every configuration.** Simple and exact per-trial, but wastes most of
  the budget (measured: three times the compute for the same result here).
- **A fixed early-stopping rule.** Cheaper to implement but brittle; successive halving and
  Hyperband adapt the stopping to the observed distribution of trials.

## Consequences

- The orchestrator reaches the optimal configuration at roughly a third of the compute.
- Brackets and rungs follow directly from ``eta`` and the resource range, so there are few
  knobs.
- Multi-fidelity assumes intermediate values rank configurations; noisy early signals are
  handled by warmup and promotion of multiple survivors.
