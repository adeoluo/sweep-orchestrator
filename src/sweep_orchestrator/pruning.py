"""Early-stopping pruners for the parallel runner.

A pruner decides, from a trial's intermediate values, whether it is clearly worse
than its peers and should be stopped before consuming its full budget. The median
pruner stops a trial whose latest intermediate value is worse than the median of
the completed trials at the same step, the policy behind Optuna's default and the
asynchronous successive-halving family.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Pruner(Protocol):
    """Decides whether a running trial should be stopped early."""

    def should_prune(self, step: int, value: float, peers: Sequence[float]) -> bool:
        """Return whether to stop a trial reporting ``value`` at ``step``."""


class NoPruner:
    """Never prunes; every trial runs to its full budget."""

    def should_prune(self, step: int, value: float, peers: Sequence[float]) -> bool:
        return False


class MedianPruner:
    """Prune a trial whose value is worse than the median of its peers at the step.

    A warmup of ``n_warmup`` reported steps and a minimum number of peers avoid
    pruning on noisy early signals or with too little evidence.
    """

    def __init__(self, *, n_warmup: int = 1, min_peers: int = 3) -> None:
        if n_warmup < 0:
            raise ValueError("n_warmup must be non-negative")
        if min_peers < 1:
            raise ValueError("min_peers must be at least 1")
        self._n_warmup = n_warmup
        self._min_peers = min_peers

    def should_prune(self, step: int, value: float, peers: Sequence[float]) -> bool:
        if step < self._n_warmup or len(peers) < self._min_peers:
            return False
        ordered = sorted(peers)
        middle = len(ordered) // 2
        median = (
            ordered[middle]
            if len(ordered) % 2 == 1
            else 0.5 * (ordered[middle - 1] + ordered[middle])
        )
        return value > median
