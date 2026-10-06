"""Model-agnostic detector interface.

The pipeline depends only on `BaseDetector`. Plug in YOLO/torch/etc. later
by subclassing; no OpenCV code changes. No fake detections are produced.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import numpy as np

from cv.schemas import Detection


class ModelNotLoadedError(RuntimeError):
    """Raised when inference is requested without a loaded model."""


class BaseDetector(ABC):
    name = "Detector interface"

    @property
    @abstractmethod
    def is_loaded(self) -> bool: ...

    @property
    def ready(self) -> bool:
        return True  # interface is usable even without a model

    @abstractmethod
    def load_model(self) -> None: ...

    @abstractmethod
    def predict(self, image: np.ndarray) -> List[Detection]:
        """Run inference on a preprocessed image (model coordinates)."""


class NullDetector(BaseDetector):
    """Placeholder used when no trained model exists."""

    @property
    def is_loaded(self) -> bool:
        return False

    def load_model(self) -> None:
        raise ModelNotLoadedError("No model available. Implement in Phase 4.")

    def predict(self, image: np.ndarray) -> List[Detection]:
        raise ModelNotLoadedError("No medical model loaded.")
