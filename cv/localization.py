"""Bounding-box handling and region helpers."""
from __future__ import annotations

from typing import List

from cv.coordinates import ResizeTransform
from cv.schemas import BoundingBox, Detection


class Localizer:
    """Clips/validates boxes and maps detections to original coordinates."""

    name = "Localizer"

    @property
    def ready(self) -> bool:
        return True

    def localize(self, detections: List[Detection], transform: ResizeTransform,
                 original_size: tuple[int, int]) -> List[Detection]:
        """Restore model-space boxes to the original image. Phase 5."""
        raise NotImplementedError("Localizer.localize: Phase 5")

    @staticmethod
    def area(box: BoundingBox) -> float:
        return max(0.0, box.x_max - box.x_min) * max(0.0, box.y_max - box.y_min)
