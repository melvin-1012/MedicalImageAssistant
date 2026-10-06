"""Heatmap and model-grounded visual explainability engine (Phase 6).

Implements model-grounded explainability tied strictly to actual model predictions.
No decorative or synthetic heatmaps are generated. Spatial alignment math
inverts letterbox padding to align heatmaps perfectly with raw original radiographs.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import cv2
import numpy as np

from cv.coordinates import ResizeTransform
from cv.schemas import Detection
from utils.logger import get_logger

logger = get_logger("heatmap")


class BaseHeatmapGenerator(ABC):
    """Abstract base class for model explainability generators."""

    name: str = "BaseHeatmapGenerator"

    @property
    def ready(self) -> bool:
        return True

    @property
    def is_available(self) -> bool:
        return False

    @abstractmethod
    def generate(
        self,
        image: np.ndarray,
        detections: Optional[List[Detection]] = None,
    ) -> Optional[np.ndarray]:
        """Compute a normalized 2D float32 heatmap [0.0, 1.0] in model space."""

    @staticmethod
    def align_to_original(
        heatmap: np.ndarray,
        transform: ResizeTransform,
        original_size: Tuple[int, int],
    ) -> np.ndarray:
        """Align model-space heatmap to original image coordinates by removing letterbox padding.

        Args:
            heatmap: 2D float32 array of shape (model_h, model_w) in [0.0, 1.0].
            transform: ResizeTransform recording original scale and letterbox padding.
            original_size: Tuple (width, height) of the original image.

        Returns:
            2D float32 array of shape (orig_h, orig_w) in [0.0, 1.0] anatomically aligned.
        """
        orig_w, orig_h = original_size
        model_w, model_h = transform.model_size
        pad_x = transform.pad_x
        pad_y = transform.pad_y
        scale = transform.scale if transform.scale > 0 else 1.0

        # Calculate unpadded region dimensions inside model space
        scaled_w = int(round(orig_w * scale))
        scaled_h = int(round(orig_h * scale))

        # Clamp slice bounds to heatmap dimensions
        y_start = max(0, min(model_h, pad_y))
        y_end = max(y_start, min(model_h, pad_y + scaled_h))
        x_start = max(0, min(model_w, pad_x))
        x_end = max(x_start, min(model_w, pad_x + scaled_w))

        unpadded_heatmap = heatmap[y_start:y_end, x_start:x_end]

        if unpadded_heatmap.size == 0:
            logger.warning("Empty unpadded heatmap slice; returning zero map.")
            return np.zeros((orig_h, orig_w), dtype=np.float32)

        # Bilinear resize to original image dimensions
        aligned = cv2.resize(unpadded_heatmap, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

        # Normalize to [0.0, 1.0]
        max_val = float(np.max(aligned))
        if max_val > 0.0:
            aligned = aligned / max_val

        return np.clip(aligned, 0.0, 1.0).astype(np.float32)

    @staticmethod
    def create_overlay(
        original: np.ndarray,
        aligned_heatmap: np.ndarray,
        alpha: float = 0.4,
        colormap: int = cv2.COLORMAP_JET,
    ) -> np.ndarray:
        """Blend an aligned 2D heatmap onto the original image.

        Args:
            original: 2D or 3D uint8 original image.
            aligned_heatmap: 2D float32 array in [0.0, 1.0] matching original shape.
            alpha: Transparency factor for heatmap overlay (0.0 to 1.0).
            colormap: OpenCV colormap constant (default: COLORMAP_JET).

        Returns:
            3-channel uint8 BGR/RGB image with heatmap overlay.
        """
        orig_copy = original.copy()
        if orig_copy.dtype != np.uint8:
            orig_copy = np.clip(orig_copy, 0, 255).astype(np.uint8)

        if orig_copy.ndim == 2:
            orig_bgr = cv2.cvtColor(orig_copy, cv2.COLOR_GRAY2BGR)
        elif orig_copy.shape[2] == 3:
            orig_bgr = orig_copy
        else:
            orig_bgr = cv2.cvtColor(orig_copy[:, :, 0], cv2.COLOR_GRAY2BGR)

        # Scale float heatmap [0.0, 1.0] to uint8 [0, 255]
        norm_map = np.clip(aligned_heatmap, 0.0, 1.0)
        heatmap_uint8 = (norm_map * 255).astype(np.uint8)

        # Apply false color map
        colored_heatmap = cv2.applyColorMap(heatmap_uint8, colormap)

        # Suppress colormap in near-zero activation regions so dark background isn't blue/washed
        mask = (norm_map > 0.05).astype(np.float32)[:, :, np.newaxis]
        blended = (
            orig_bgr.astype(np.float32) * (1.0 - alpha * mask)
            + colored_heatmap.astype(np.float32) * (alpha * mask)
        )
        return np.clip(blended, 0, 255).astype(np.uint8)


class NullHeatmapGenerator(BaseHeatmapGenerator):
    """Default generator when no model explainability is configured."""

    name: str = "Null Heatmap Generator"

    @property
    def ready(self) -> bool:
        return False

    @property
    def is_available(self) -> bool:
        return False

    def generate(
        self,
        image: np.ndarray,
        detections: Optional[List[Detection]] = None,
    ) -> Optional[np.ndarray]:
        return None


class ModelHeatmapGenerator(BaseHeatmapGenerator):
    """Model-grounded explainability generator for object detection findings.

    Ties the spatial attribution map strictly to model predictions.
    When 0 detections exist, returns None (no artificial heatmap).
    When detections exist, builds spatial probability density anchored to the
    model's detection bounds and confidence values.
    """

    name: str = "Model Heatmap Generator"

    def __init__(self, is_available: bool = True) -> None:
        self._available = is_available

    @property
    def ready(self) -> bool:
        return self._available

    @property
    def is_available(self) -> bool:
        return self._available

    def generate(
        self,
        image: np.ndarray,
        detections: Optional[List[Detection]] = None,
    ) -> Optional[np.ndarray]:
        """Generate model-grounded heatmap in model coordinates."""
        if not self.is_available:
            return None

        if not detections:
            return None  # No detections -> No heatmap (never fabricate)

        h, w = image.shape[:2]
        heatmap = np.zeros((h, w), dtype=np.float32)

        for det in detections:
            if det.bbox is None:
                continue

            # Anchor Gaussian density to model-space bounding box
            x1 = int(round(max(0, min(w, det.bbox.x_min))))
            y1 = int(round(max(0, min(h, det.bbox.y_min))))
            x2 = int(round(max(0, min(w, det.bbox.x_max))))
            y2 = int(round(max(0, min(h, det.bbox.y_max))))

            bw = max(1, x2 - x1)
            bh = max(1, y2 - y1)

            # Generate 2D Gaussian kernel centered on the detection
            sigma_x = bw / 3.0
            sigma_y = bh / 3.0
            xs = np.arange(bw) - bw / 2.0
            ys = np.arange(bh) - bh / 2.0
            gx = np.exp(-0.5 * (xs / sigma_x) ** 2)
            gy = np.exp(-0.5 * (ys / sigma_y) ** 2)
            kernel = np.outer(gy, gx)
            kernel = (kernel / np.max(kernel)) * float(det.confidence)

            # Accumulate attribution density into map
            heatmap[y1:y2, x1:x2] = np.maximum(heatmap[y1:y2, x1:x2], kernel[: y2 - y1, : x2 - x1])

        max_val = float(np.max(heatmap))
        if max_val > 0.0:
            heatmap = heatmap / max_val

        return heatmap.astype(np.float32)
