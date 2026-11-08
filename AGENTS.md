# AGENTS.md

Working notes for coding agents and contributors in **Sweep Orchestrator**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

Hyperparameter sweep orchestration built from scratch: multi-fidelity scheduling (successive halving and Hyperband), parallel early stopping, multi-objective Pareto optimization, and hyperparameter importance analysis.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `scripts/`: maintenance scripts (release, assets, data)
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/sweep_orchestrator/__init__.py`: Sweep Orchestrator - multi-fidelity scheduling and multi-objective sweeps from scratch.
- `src/sweep_orchestrator/cli.py`: Command line interface for the sweep orchestrator.
- `src/sweep_orchestrator/data.py`: A bundled, deterministic sweep problem used for demonstrations and evaluation.
- `src/sweep_orchestrator/evaluation.py`: Measure what pruning and multi-fidelity scheduling save.
- `src/sweep_orchestrator/hyperband.py`: Hyperband: hedging over how aggressively to prune.
- `src/sweep_orchestrator/importance.py`: Hyperparameter importance via variance decomposition.
- `src/sweep_orchestrator/observability.py`: In-process request metrics for the HTTP service.
- `src/sweep_orchestrator/pareto.py`: Multi-objective optimization: Pareto fronts over conflicting objectives.
- `src/sweep_orchestrator/pruning.py`: Early-stopping pruners for the parallel runner.
- `src/sweep_orchestrator/runner.py`: The parallel sweep runner: execute trials concurrently with pruning.
- `src/sweep_orchestrator/service.py`: A standard-library HTTP service exposing the sweep orchestrator.
- `src/sweep_orchestrator/successive_halving.py`: Successive halving: the core multi-fidelity primitive.
- `src/sweep_orchestrator/types.py`: Core types for sweeps: configurations, trials, and objective callables.

## Commands

| Command | Purpose |
|---|---|
| `make help` | Show this help |
| `make setup` | Install dependencies and pre-commit hooks |
| `make format` | Format automatically |
| `make lint` | Lint (no fixes) |
| `make type` | Type-check |
| `make test` | Run tests |
| `make coverage` | Tests with coverage gate |
| `make evaluation` | Reproduce the results table |
| `make run` | Run the application entrypoint |
| `make diagram` | Render architecture diagram to SVG |
| `make docker-build` | Build the image |
| `make docker-up` | Run via docker compose |
| `make clean` | Remove caches and artifacts |
| `make all` | Full local gate (mirror of continuous integration) |
| `make changelog` | Regenerate CHANGELOG.md from Conventional Commits (git-cliff) |
| `make cut-release` | Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional) |

Run the full local gate (`make all`) before committing; CI runs the same checks.

## Conventions

- Commits follow Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`).
  The changelog and the next version number are derived from them.
- Every number quoted in the README is produced by a command in this repository. When behavior
  changes, rerun that command and update the number in the same commit.
- When a component is added, removed or renamed, update `docs/architecture/architecture.mmd`
  and re-render `architecture.svg` so the diagram matches the code.
- README sections keep their fixed order. Prose avoids em and en dashes and promotional wording.
- Tests accompany behavior changes; a bug fix comes with a test that fails without it.
- Releases are cut with `make cut-release`.

## Python notes

- Python is managed with `uv`; run commands through `uv run` so the locked environment is used.
- Lint and format with `ruff`; type-check with `mypy`; tests use `pytest`.
- Public functions carry type hints and a docstring that states the contract, not the steps.
