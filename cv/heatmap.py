"""Heatmap / Grad-CAM architecture. No synthetic heatmaps."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class BaseHeatmapGenerator(ABC):
    """Implemented in Phase 6 against a real model."""

    @property
    def is_available(self) -> bool:
        return False

    @abstractmethod
    def generate(self, image: np.ndarray, target: Optional[str] = None) -> np.ndarray:
        """Return a 0..1 float map aligned to `image`."""


class NullHeatmapGenerator(BaseHeatmapGenerator):
    def generate(self, image: np.ndarray, target: Optional[str] = None) -> np.ndarray:
        raise NotImplementedError("No heatmap generator configured (Phase 6).")
