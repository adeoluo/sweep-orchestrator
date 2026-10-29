# Data Card - Sweep Orchestrator

The project bundles one synthetic sweep problem, not a dataset. There is no training data and
nothing is downloaded.

## bundled problem (`src/sweep_orchestrator/data.py`)

- **Provenance:** a hand-authored learning-curve simulation. Each configuration (a learning
  rate and a depth) has a true final loss given by a smooth bowl, and an intermediate learning
  curve that approaches it, so good configurations separate from bad ones early.
- **Why this shape:** it makes early stopping meaningful (rank is visible before full budget)
  and has a known optimum, so savings and solution quality can both be measured.
- **Licensing:** authored by this repository; MIT.
- **Known gaps:** a simulation, not a real training run; two parameters only.

## Ethical considerations

The problem is synthetic with no personal, sensitive, or copyrighted content.
