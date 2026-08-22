"""
Configuration loading (Task 8 Phase 2/15).

Reads a YAML experiment config into a plain dict. Deliberately simple --
no schema-validation framework, since the config shape is small and
stable; validation happens by KeyError/type errors surfacing naturally
if a config is malformed, which is acceptable for a research simulation
harness at this scale.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
