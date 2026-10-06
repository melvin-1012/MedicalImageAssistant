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
    pad_x: int = 0                   # left padding in pixels
    pad_y: int = 0                   # top padding in pixels

    @classmethod
    def identity(cls, size: Tuple[int, int]) -> "ResizeTransform":
        return cls(original_size=size, model_size=size, scale=1.0, pad_x=0, pad_y=0)


def to_original(box: BoundingBox, transform: ResizeTransform) -> BoundingBox:
    """Model-space box -> original-image box."""
    orig_w, orig_h = transform.original_size
    scale = transform.scale if transform.scale > 0 else 1.0

    x_min = (box.x_min - transform.pad_x) / scale
    y_min = (box.y_min - transform.pad_y) / scale
    x_max = (box.x_max - transform.pad_x) / scale
    y_max = (box.y_max - transform.pad_y) / scale

    return BoundingBox(
        x_min=float(max(0.0, min(orig_w, x_min))),
        y_min=float(max(0.0, min(orig_h, y_min))),
        x_max=float(max(0.0, min(orig_w, x_max))),
        y_max=float(max(0.0, min(orig_h, y_max))),
    )


def to_model(box: BoundingBox, transform: ResizeTransform) -> BoundingBox:
    """Original-image box -> model-space box."""
    model_w, model_h = transform.model_size
    scale = transform.scale

    x_min = box.x_min * scale + transform.pad_x
    y_min = box.y_min * scale + transform.pad_y
    x_max = box.x_max * scale + transform.pad_x
    y_max = box.y_max * scale + transform.pad_y

    return BoundingBox(
        x_min=float(max(0.0, min(model_w, x_min))),
        y_min=float(max(0.0, min(model_h, y_min))),
        x_max=float(max(0.0, min(model_w, x_max))),
        y_max=float(max(0.0, min(model_h, y_max))),
    )


def normalize(box: BoundingBox, size: Tuple[int, int]) -> BoundingBox:
    """Pixel box -> 0..1 relative box."""
    w, h = size
    w_val = float(w) if w > 0 else 1.0
    h_val = float(h) if h > 0 else 1.0
    return BoundingBox(
        x_min=max(0.0, min(1.0, box.x_min / w_val)),
        y_min=max(0.0, min(1.0, box.y_min / h_val)),
        x_max=max(0.0, min(1.0, box.x_max / w_val)),
        y_max=max(0.0, min(1.0, box.y_max / h_val)),
    )


def denormalize(box: BoundingBox, size: Tuple[int, int]) -> BoundingBox:
    """0..1 relative box -> pixel box."""
    w, h = size
    return BoundingBox(
        x_min=max(0.0, min(float(w), box.x_min * w)),
        y_min=max(0.0, min(float(h), box.y_min * h)),
        x_max=max(0.0, min(float(w), box.x_max * w)),
        y_max=max(0.0, min(float(h), box.y_max * h)),
    )
