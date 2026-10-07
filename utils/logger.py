"""Minimal logger: prints `[CV] message` to stdout."""
from __future__ import annotations

import logging
import sys

import config

_FORMAT = "[CV] %(message)s"


def get_logger(name: str = "cv") -> logging.Logger:
    """Return a configured logger (handlers are attached once)."""
    logger = logging.getLogger(f"medical_cv.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        logger.propagate = False
    return logger
