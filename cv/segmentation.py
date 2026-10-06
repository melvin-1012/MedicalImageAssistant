"""Segmentation architecture: model interface, mask processing, contours."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import numpy as np


class BaseSegmenter(ABC):
    """Implemented in Phase 7 against a real model."""

    @property
    def is_available(self) -> bool:
        return False

    @abstractmethod
    def segment(self, image: np.ndarray) -> np.ndarray:
        """Return a binary/label mask aligned to `image`."""


class NullSegmenter(BaseSegmenter):
    def segment(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError("No segmentation model configured (Phase 7).")


class MaskProcessor:
    """Mask cleanup and contour extraction. Phase 7."""

    def clean(self, mask: np.ndarray) -> np.ndarray:
        raise NotImplementedError("MaskProcessor.clean: Phase 7")

    def contours(self, mask: np.ndarray) -> List[np.ndarray]:
        raise NotImplementedError("MaskProcessor.contours: Phase 7")
