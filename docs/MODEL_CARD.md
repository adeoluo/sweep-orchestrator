# System Card - Sweep Orchestrator

## Overview

- **What it is:** a hyperparameter sweep orchestrator - multi-fidelity scheduling, parallel
  early-stopping, multi-objective Pareto optimization, and importance analysis.
- **What it is not:** a sampler. It schedules, prunes, and analyzes trials; proposing
  configurations is the complementary concern (see the hyperparameter-optimizer project).
- **Version:** 0.1.0.

## Intended use

- **Primary use cases:** running many configurations efficiently, trading off conflicting
  objectives, and understanding which hyperparameters mattered.
- **Primary users:** engineers and researchers tuning models or systems at scale.

## Out-of-scope / prohibited use

- The parallel runner overlaps evaluations in one process; cross-machine execution needs a
  transport.
- The bundled problem is a learning-curve simulation, not a real training run.

## Performance

See the README: all strategies find the optimum, but pruning and successive halving reach it at
about a third of the compute.

## Risks and limitations

- Multi-fidelity assumes intermediate values rank configurations.
- Importance is a single-parameter decomposition without interaction terms.

## Safety mitigations

- Deterministic single-worker mode; bounded request sizes in the service.

## Environmental / cost footprint

The project's purpose is to reduce compute; it is itself negligible and in-memory.
