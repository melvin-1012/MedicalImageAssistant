"""Segmentation architecture: model interface, mask processing, and graceful unavailability (Phase 7).

The RSNA Pneumonia Detection Challenge provides bounding-box annotations, not pixel-level segmentation masks.
This module defines the standard `BaseSegmenter` interface, provides a legitimate `NullSegmenter`
that explicitly reports segmentation as unavailable without fabricating data,
and provides `MaskProcessor` for morphological cleaning and contour extraction.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger("segmentation")


class BaseSegmenter(ABC):
    """Abstract interface for medical image segmentation models."""

    name = "BaseSegmenter"

    @property
    def is_available(self) -> bool:
        """Indicates whether a trained segmentation model and masks are available."""
        return False

    @property
    def ready(self) -> bool:
        """Indicates whether the segmenter component is initialized and ready for pipeline queries."""
        return True

    @abstractmethod
    def segment(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Generate a binary or multi-class mask for the input image.

        Returns:
            np.ndarray: 2D uint8 mask matching input image dimensions, or None if unavailable.
        """

    @abstractmethod
    def get_segmentation_info(self) -> Dict[str, Any]:
        """Return metadata about segmentation capability, model, and availability status."""

    @staticmethod
    def align_to_original(
        mask: Optional[np.ndarray],
        transform: Any,
        orig_size: Tuple[int, int],
    ) -> Optional[np.ndarray]:
        """Unpad letterbox margins and scale mask back to original radiograph dimensions.

        Args:
            mask: 2D or 3D binary mask in model space (e.g. 640x640).
            transform: ResizeTransform containing scale and padding offsets.
            orig_size: Tuple (width, height) of original radiograph.

        Returns:
            np.ndarray: Binary mask scaled to (height, width) with INTER_NEAREST, or None.
        """
        if mask is None or mask.size == 0:
            return None

        orig_w, orig_h = orig_size
        if hasattr(transform, "pad_x") and hasattr(transform, "pad_y"):
            pad_x, pad_y = int(transform.pad_x), int(transform.pad_y)
        elif hasattr(transform, "pad"):
            pad_x, pad_y = transform.pad
        else:
            pad_x, pad_y = 0, 0
        model_h, model_w = mask.shape[:2]

        # Crop letterbox padding
        valid_h = max(1, model_h - 2 * pad_y)
        valid_w = max(1, model_w - 2 * pad_x)
        cropped = mask[pad_y : pad_y + valid_h, pad_x : pad_x + valid_w]

        # Nearest-neighbor interpolation preserves discrete binary pixel values {0, 255}
        aligned = cv2.resize(
            cropped,
            (orig_w, orig_h),
            interpolation=cv2.INTER_NEAREST,
        )
        return aligned


class NullSegmenter(BaseSegmenter):
    """Graceful fallback when legitimate segmentation ground truth or models are unavailable.

    The RSNA Pneumonia Detection Challenge dataset provides bounding boxes only.
    NullSegmenter correctly declares unavailability without fabricating artificial masks.
    """

    name = "NullSegmenter (Unavailable)"
    UNAVAILABLE_REASON = (
        "Pixel-level segmentation is unavailable because the RSNA Pneumonia Detection "
        "Challenge dataset provides bounding-box annotations, not pixel-level segmentation masks."
    )

    @property
    def is_available(self) -> bool:
        return False

    def segment(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Explicitly returns None to signal that segmentation output is not available."""
        logger.debug("Segmentation requested but unavailable: %s", self.UNAVAILABLE_REASON)
        return None

    def get_segmentation_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "is_available": False,
            "status": "unavailable",
            "reason": self.UNAVAILABLE_REASON,
            "model_type": None,
        }


class MaskProcessor:
    """Morphological cleanup, contour extraction, and spatial statistics for binary masks."""

    def __init__(self, kernel_size: int = 3) -> None:
        self.kernel_size = kernel_size
        self._kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )

    def clean(self, mask: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """Perform morphological opening and closing to remove noise and close small holes."""
        if mask is None or mask.size == 0:
            return None

        clean_copy = mask.copy()
        if clean_copy.dtype != np.uint8:
            clean_copy = (clean_copy > 0).astype(np.uint8) * 255

        # Morphological opening (remove false positive flecks) followed by closing (fill pinholes)
        opened = cv2.morphologyEx(clean_copy, cv2.MORPH_OPEN, self._kernel)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, self._kernel)
        return closed

    def contours(self, mask: Optional[np.ndarray]) -> List[np.ndarray]:
        """Extract external boundary contours from a binary mask."""
        if mask is None or mask.size == 0:
            return []

        binary = (mask > 0).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return list(cnts)

    def compute_mask_area(self, mask: Optional[np.ndarray]) -> int:
        """Return the count of positive (non-zero) mask pixels."""
        if mask is None or mask.size == 0:
            return 0
        return int(np.count_nonzero(mask > 0))
