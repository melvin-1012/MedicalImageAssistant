"""Coordinate conversion between original and model-input image space."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from cv.schemas import BoundingBox


@dataclass(frozen=True)
class ResizeTransform:
    """Records how an image was resized/padded so boxes can be mapped back."""
    original_size: Tuple[int, int]   # (width, height)
    model_size: Tuple[int, int]      # (width, height)
    scale: float = 1.0
    pad_x: int = 0
    pad_y: int = 0

    @classmethod
    def identity(cls, size: Tuple[int, int]) -> "ResizeTransform":
        return cls(original_size=size, model_size=size)


def to_original(box: BoundingBox, transform: ResizeTransform) -> BoundingBox:
    """Model-space box -> original-image box. Phase 5."""
    raise NotImplementedError("coordinates.to_original: Phase 5")


def to_model(box: BoundingBox, transform: ResizeTransform) -> BoundingBox:
    """Original-image box -> model-space box. Phase 5."""
    raise NotImplementedError("coordinates.to_model: Phase 5")


def normalize(box: BoundingBox, size: Tuple[int, int]) -> BoundingBox:
    """Pixel box -> 0..1 relative box. Phase 5."""
    raise NotImplementedError("coordinates.normalize: Phase 5")


def denormalize(box: BoundingBox, size: Tuple[int, int]) -> BoundingBox:
    """0..1 relative box -> pixel box. Phase 5."""
    raise NotImplementedError("coordinates.denormalize: Phase 5")
