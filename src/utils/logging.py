"""
Application-level logging (Task 8 Phase 2), deliberately separate from
metrics collection (src/metrics/collector.py). Per Task 7 Part 9: "what
happened, for analysis" (metrics) and "what went wrong, for debugging"
(this module) are different concerns and are kept structurally separate
rather than conflated into one log stream.
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
