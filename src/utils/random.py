"""
Seeded randomness management (Task 8 Phase 15's explicit requirement:
"All random processes must be seeded.").

Provides one place that derives per-component seeds from a single
top-level experiment seed, so a run is fully reproducible from one
`--seed` value while still giving each stochastic component (workload
generator, network loss model, bootstrap resampling) its own
independent random.Random instance rather than sharing global state.
"""

from __future__ import annotations

import random


class SeedManager:
    """Derives deterministic sub-seeds from one top-level seed.

    Using a distinct sub-seed per component (rather than one shared
    random.Random) avoids one component's draws perturbing another's
    sequence -- e.g., adding a new workload transaction shouldn't change
    the network's packet-loss random sequence.
    """

    def __init__(self, top_level_seed: int):
        self.top_level_seed = top_level_seed
        self._deriver = random.Random(top_level_seed)
        self._issued: dict[str, int] = {}

    def sub_seed(self, name: str) -> int:
        """Returns the same sub-seed every time it's called with the
        same `name`, for the lifetime of this SeedManager -- so
        repeated calls (e.g., re-fetching the "workload" seed in two
        different modules) stay consistent."""
        if name not in self._issued:
            self._issued[name] = self._deriver.randrange(0, 2**32 - 1)
        return self._issued[name]

    def rng(self, name: str) -> random.Random:
        return random.Random(self.sub_seed(name))
