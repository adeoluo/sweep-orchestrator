# End-to-End Case Study - A Sweep Under a Compute Budget

How to tune many configurations without paying to train the losers, and how to read the result.

## Scenario

A team has 27 candidate configurations and can afford to train, at most, the equivalent of a
handful of them to completion. Training all 27 to full budget is out of the question. The
question is how to spend the budget to still find the best configuration.

## Running the sweep

```bash
curl -s -X POST localhost:8000/sweep -d '{"count": 27}'
```

```json
{
  "ground_truth_best": 0.2021,
  "strategies": [
    {"strategy": "full (no pruning)", "best_loss": 0.2021, "resource": 243},
    {"strategy": "median pruning", "best_loss": 0.2021, "resource": 90},
    {"strategy": "successive halving", "best_loss": 0.2021, "resource": 81}
  ]
}
```

Both early-stopping strategies find the **same best configuration** as the exhaustive sweep
(final loss 0.2021, equal to the ground-truth best), but at **about a third of the compute**.
Under the team's budget, that is the difference between finishing the sweep and not.

## Reading more than the winner

```bash
curl -s -X POST localhost:8000/importance -d '{"count": 64}'   # which knobs mattered
curl -s -X POST localhost:8000/pareto -d '{"points": [[0.1, 0.9], [0.5, 0.5], [0.9, 0.1]]}'
```

The importance ranking shows the learning rate explained far more objective variance than the
depth, so the next sweep can narrow that range. The Pareto endpoint, given accuracy-versus-
latency vectors, returns only the non-dominated configurations, so a product decision is made
on the real tradeoff surface rather than a single blended score.

## What an operator sees

- **Compute saved, quality kept.** The response reports both the best loss and the resource
  spent, so the saving is explicit and auditable.
- **A resumable record.** Every trial, pruned or complete, is stored, so a sweep can be
  analyzed or resumed.
- **Decisions, not just a number.** Importance and Pareto turn a finished sweep into guidance
  for the next one.

## Takeaway

Orchestration - not just sampling - is what makes tuning affordable: stop the losers early,
keep the winner, and read the sweep for what to do next.
