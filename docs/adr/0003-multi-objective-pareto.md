# ADR-0003: Pareto fronts for conflicting objectives

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

Production tuning rarely optimizes one metric; accuracy, latency, and cost trade off against
each other. Collapsing them into a single weighted objective hides the tradeoff and bakes in a
weighting the user may not want.

## Decision

Return the **Pareto front**: the set of non-dominated configurations. Implement the NSGA-II
primitives from scratch - Pareto dominance, fast non-dominated sorting into fronts, and
crowding distance for spread - so a caller sees the real tradeoff surface and picks a point on
it.

## Alternatives considered

- **A single weighted sum.** Simple, but requires choosing weights up front and can miss
  non-convex parts of the front entirely.
- **Lexicographic ordering.** Works when objectives have a strict priority, but most tuning
  tradeoffs are genuine, not ordered.

## Consequences

- Conflicting objectives yield a front, and dominated configurations are discarded explicitly.
- Crowding distance lets a selector prefer well-spread solutions.
- The decomposition is the foundation for a full NSGA-II evolutionary loop, left as roadmap.
