"""OpenCV preprocessing. Never mutates the original image."""
from __future__ import annotations

import numpy as np

from config import PreprocessConfig
from cv.schemas import PreprocessedImage


class Preprocessor:
    """Grayscale, resize (aspect-preserving), CLAHE, denoise, sharpen, normalise."""

    name = "Preprocessor"

    def __init__(self, config: PreprocessConfig | None = None) -> None:
        self.config = config or PreprocessConfig()

    @property
    def ready(self) -> bool:
        return True

    def preprocess(self, image: np.ndarray) -> PreprocessedImage:
        """Return a model-ready COPY plus its ResizeTransform. Phase 2."""
        raise NotImplementedError("Preprocessor.preprocess: Phase 2")

    # Phase 2: to_grayscale, resize_with_padding, apply_clahe,
    #          denoise, sharpen, normalize
