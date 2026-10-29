"""Command line interface for the sweep orchestrator."""

from __future__ import annotations

import argparse

from sweep_orchestrator.data import sample_configurations
from sweep_orchestrator.evaluation import format_table, ground_truth_best, run_evaluation
from sweep_orchestrator.importance import Observation, format_importance, parameter_importance
from sweep_orchestrator.pareto import MultiObjectivePoint, pareto_front


def _cmd_evaluate(args: argparse.Namespace) -> None:
    results = run_evaluation(count=args.count)
    print(format_table(results))
    print(f"\nGround-truth best final loss: {ground_truth_best(count=args.count):.4f}")


def _cmd_importance(args: argparse.Namespace) -> None:
    from sweep_orchestrator.data import final_loss

    configs = sample_configurations(args.count)
    observations = [Observation(config, final_loss(config)) for config in configs]
    print(format_importance(parameter_importance(observations)))


def _cmd_pareto(_: argparse.Namespace) -> None:
    # Accuracy loss versus latency: a classic two-objective tradeoff.
    points = [
        MultiObjectivePoint(0, (0.10, 0.90)),
        MultiObjectivePoint(1, (0.25, 0.60)),
        MultiObjectivePoint(2, (0.50, 0.40)),
        MultiObjectivePoint(3, (0.80, 0.20)),
        MultiObjectivePoint(4, (0.55, 0.65)),
    ]
    front = pareto_front(points)
    print("Pareto-optimal configurations (accuracy loss, latency):")
    for point in front:
        print(f"  config {point.identifier}: {point.objectives}")
    dominated = {p.identifier for p in points} - {p.identifier for p in front}
    print(f"Dominated configurations: {sorted(dominated)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="sweep-orchestrator", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate = sub.add_parser("evaluate", help="compare full, pruned, and multi-fidelity sweeps")
    evaluate.add_argument("--count", type=int, default=27)

    importance = sub.add_parser("importance", help="rank hyperparameters by variance explained")
    importance.add_argument("--count", type=int, default=64)

    sub.add_parser("pareto", help="show a Pareto front over two objectives")

    handlers = {
        "evaluate": _cmd_evaluate,
        "importance": _cmd_importance,
        "pareto": _cmd_pareto,
    }
    args = parser.parse_args(argv)
    handlers[args.command](args)


if __name__ == "__main__":
    main()
