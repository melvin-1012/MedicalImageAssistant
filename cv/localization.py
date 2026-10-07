"""Bounding-box localization, coordinate restoration, and region handling (Phase 5).

Restores model-space bounding boxes to the original medical image space using
`ResizeTransform` so bounding boxes correspond exactly to anatomical locations on the raw radiograph.
"""
from __future__ import annotations

from typing import List, Tuple

from cv.coordinates import ResizeTransform, to_original
from cv.schemas import BoundingBox, Detection
from utils.logger import get_logger

logger = get_logger("localization")


class Localizer:
    """Clips/validates boxes and maps detections to original coordinates."""

    name = "Localizer"

    @property
    def ready(self) -> bool:
        return True

    def localize(
        self,
        detections: List[Detection],
        transform: ResizeTransform,
        original_size: Tuple[int, int],
    ) -> List[Detection]:
        """Restore model-space boxes to the original image coordinate frame.

        Args:
            detections: List of detections with boxes in model-space (e.g. 640x640).
            transform: ResizeTransform containing scale and letterbox padding.
            original_size: Tuple (width, height) of the original image.

        Returns:
            New list of Detection objects with boxes mapped to original image coordinates.
        """
        orig_w, orig_h = original_size
        localized: List[Detection] = []

        for d in detections:
            if d.bbox is None:
                localized.append(
                    Detection(
                        label=d.label,
                        confidence=d.confidence,
                        bbox=None,
                        heatmap_path=d.heatmap_path,
                        mask_path=d.mask_path,
                    )
                )
                continue

            # 1. Map from model coordinates to original coordinates
            orig_box = to_original(d.bbox, transform)

            # 2. Hard-clip to original image boundaries [0, orig_w] x [0, orig_h]
            clipped_x_min = max(0.0, min(float(orig_w), orig_box.x_min))
            clipped_y_min = max(0.0, min(float(orig_h), orig_box.y_min))
            clipped_x_max = max(0.0, min(float(orig_w), orig_box.x_max))
            clipped_y_max = max(0.0, min(float(orig_h), orig_box.y_max))

            # 3. Sanity check: box must have non-zero width and height
            w = clipped_x_max - clipped_x_min
            h = clipped_y_max - clipped_y_min
            if w <= 0.0 or h <= 0.0:
                logger.warning(
                    "Dropping degenerate box after clipping: (%s, %s, %s, %s)",
                    clipped_x_min,
                    clipped_y_min,
                    clipped_x_max,
                    clipped_y_max,
                )
                continue

            mapped_box = BoundingBox(
                x_min=round(clipped_x_min, 2),
                y_min=round(clipped_y_min, 2),
                x_max=round(clipped_x_max, 2),
                y_max=round(clipped_y_max, 2),
            )

            localized.append(
                Detection(
                    label=d.label,
                    confidence=d.confidence,
                    bbox=mapped_box,
                    heatmap_path=d.heatmap_path,
                    mask_path=d.mask_path,
                )
            )

        return localized

    @staticmethod
    def area(box: BoundingBox) -> float:
        """Calculate pixel area of a bounding box."""
        return max(0.0, box.x_max - box.x_min) * max(0.0, box.y_max - box.y_min)

    @staticmethod
    def box_iou(box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        inter_x_min = max(box1.x_min, box2.x_min)
        inter_y_min = max(box1.y_min, box2.y_min)
        inter_x_max = min(box1.x_max, box2.x_max)
        inter_y_max = min(box1.y_max, box2.y_max)

        inter_w = max(0.0, inter_x_max - inter_x_min)
        inter_h = max(0.0, inter_y_max - inter_y_min)
        inter_area = inter_w * inter_h

        area1 = Localizer.area(box1)
        area2 = Localizer.area(box2)
        union_area = area1 + area2 - inter_area

        if union_area <= 0.0:
            return 0.0
        return inter_area / union_area
