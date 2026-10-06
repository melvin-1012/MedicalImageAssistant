"""Visual output: comparison renderer, overlays, and heatmaps."""
from __future__ import annotations

from typing import List, Optional
import cv2
import numpy as np

from cv.image_loader import scale_to_8bit
from cv.schemas import Detection, VisualizationResult


class Visualizer:
    """Renders results; comparison renderer active in Batch 1; heatmaps/masks in later phases."""

    name = "Visualization engine"

    @property
    def ready(self) -> bool:
        return True

    def create_comparison(self, original: np.ndarray, processed: np.ndarray) -> np.ndarray:
        """Create a clean side-by-side visual comparison between original and processed images."""
        if original is None or processed is None:
            raise ValueError("Original and processed images must both be provided for comparison")

        orig_8bit = original.copy()
        if orig_8bit.dtype != np.uint8:
            orig_8bit = scale_to_8bit(orig_8bit)

        # Standardize to 3-channel RGB/BGR for consistent side-by-side stacking
        if orig_8bit.ndim == 2:
            orig_view = cv2.cvtColor(orig_8bit, cv2.COLOR_GRAY2BGR)
        elif orig_8bit.ndim == 3 and orig_8bit.shape[2] == 3:
            orig_view = orig_8bit
        else:
            orig_view = cv2.cvtColor(orig_8bit[:, :, 0], cv2.COLOR_GRAY2BGR)

        proc_8bit = processed.copy()
        if proc_8bit.dtype != np.uint8:
            proc_8bit = scale_to_8bit(proc_8bit)

        if proc_8bit.ndim == 2:
            proc_view = cv2.cvtColor(proc_8bit, cv2.COLOR_GRAY2BGR)
        elif proc_8bit.ndim == 3 and proc_8bit.shape[2] == 3:
            proc_view = proc_8bit
        else:
            proc_view = cv2.cvtColor(proc_8bit[:, :, 0], cv2.COLOR_GRAY2BGR)

        # Harmonize heights for horizontal stacking
        h_orig, w_orig = orig_view.shape[:2]
        h_proc, w_proc = proc_view.shape[:2]

        target_h = max(h_orig, h_proc)
        if h_orig != target_h:
            scale_orig = target_h / h_orig
            w_target_orig = int(round(w_orig * scale_orig))
            orig_view = cv2.resize(orig_view, (w_target_orig, target_h), interpolation=cv2.INTER_LINEAR)

        if h_proc != target_h:
            scale_proc = target_h / h_proc
            w_target_proc = int(round(w_proc * scale_proc))
            proc_view = cv2.resize(proc_view, (w_target_proc, target_h), interpolation=cv2.INTER_LINEAR)

        # 4px vertical separator bar between images
        separator = np.zeros((target_h, 4, 3), dtype=np.uint8)
        separator[:] = (60, 60, 60)

        comparison = np.hstack([orig_view, separator, proc_view])
        return comparison

    def render(
        self,
        original: np.ndarray,
        processed: Optional[np.ndarray],
        detections: List[Detection],
        heatmap: Optional[np.ndarray] = None,
        mask: Optional[np.ndarray] = None,
    ) -> VisualizationResult:
        """Draw and save outputs. Implemented progressively in Phases 5-7."""
        raise NotImplementedError("Visualizer.render: Phase 5")
