"""Visual output: comparison renderer, bounding box overlays, and heatmap blending (Phases 1-6).

All rendering functions preserve array immutability and never mutate input buffers.
Annotations use medically conservative wording (never claiming diagnostic certainty).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import cv2
import numpy as np

from cv.heatmap import BaseHeatmapGenerator
from cv.image_loader import scale_to_8bit
from cv.schemas import Detection, VisualizationResult
from utils.logger import get_logger

logger = get_logger("visualization")


class Visualizer:
    """Renders visual artifacts: comparisons, bounding box overlays, and heatmaps."""

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

    def draw_detections(
        self,
        image: np.ndarray,
        detections: List[Detection],
        box_color: tuple[int, int, int] = (0, 165, 255),  # High-contrast amber/orange
        thickness: int = 2,
    ) -> np.ndarray:
        """Render localized bounding boxes and confidence labels onto image copy."""
        if image is None:
            raise ValueError("Input image cannot be None")

        img_copy = image.copy()
        if img_copy.dtype != np.uint8:
            img_copy = scale_to_8bit(img_copy)

        if img_copy.ndim == 2:
            canvas = cv2.cvtColor(img_copy, cv2.COLOR_GRAY2BGR)
        elif img_copy.shape[2] == 3:
            canvas = img_copy
        else:
            canvas = cv2.cvtColor(img_copy[:, :, 0], cv2.COLOR_GRAY2BGR)

        h, w = canvas.shape[:2]

        for idx, det in enumerate(detections, start=1):
            if det.bbox is None:
                continue

            x1 = int(round(max(0, min(w - 1, det.bbox.x_min))))
            y1 = int(round(max(0, min(h - 1, det.bbox.y_min))))
            x2 = int(round(max(0, min(w - 1, det.bbox.x_max))))
            y2 = int(round(max(0, min(h - 1, det.bbox.y_max))))

            # 1. Draw bounding box rectangle
            cv2.rectangle(canvas, (x1, y1), (x2, y2), box_color, thickness)

            # 2. Format clinically cautious label (e.g. "Possible abnormal opacity (87%)")
            conf_pct = int(round(det.confidence * 100))
            label_text = f"{det.label} ({conf_pct}%)"

            # 3. Draw text background banner for high-contrast legibility
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thick = 1
            (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, font_thick)

            text_bg_y1 = max(0, y1 - text_h - baseline - 4)
            text_bg_y2 = y1
            text_bg_x2 = min(w, x1 + text_w + 6)

            cv2.rectangle(canvas, (x1, text_bg_y1), (text_bg_x2, text_bg_y2), (20, 20, 20), -1)
            cv2.rectangle(canvas, (x1, text_bg_y1), (text_bg_x2, text_bg_y2), box_color, 1)

            # 4. Draw label text inside banner
            cv2.putText(
                canvas,
                label_text,
                (x1 + 3, y1 - baseline - 2),
                font,
                font_scale,
                (255, 255, 255),
                font_thick,
                cv2.LINE_AA,
            )

        return canvas

    def render(
        self,
        original: np.ndarray,
        processed: Optional[np.ndarray],
        detections: List[Detection],
        heatmap: Optional[np.ndarray] = None,
        mask: Optional[np.ndarray] = None,
        output_dir: Optional[Path | str] = None,
        stem: str = "scan",
    ) -> VisualizationResult:
        """Render all active visual outputs and save to output directory."""
        out_dir = Path(output_dir) if output_dir else Path(".")
        out_dir.mkdir(parents=True, exist_ok=True)

        res = VisualizationResult()

        # 1. Processed scan
        if processed is not None:
            proc_path = out_dir / f"{stem}_processed.png"
            cv2.imwrite(str(proc_path), processed)
            res.processed_path = str(proc_path)

            # Comparison side-by-side
            comp_img = self.create_comparison(original, processed)
            comp_path = out_dir / f"{stem}_comparison.png"
            cv2.imwrite(str(comp_path), comp_img)
            res.comparison_path = str(comp_path)

        # 2. Phase 5: Detection bounding-box overlay
        if detections:
            overlay_img = self.draw_detections(original, detections)
            overlay_path = out_dir / f"{stem}_overlay.png"
            cv2.imwrite(str(overlay_path), overlay_img)
            res.overlay_path = str(overlay_path)

        # 3. Phase 6: Heatmap / explainability overlay
        if heatmap is not None:
            heatmap_img = BaseHeatmapGenerator.create_overlay(original, heatmap)
            heat_path = out_dir / f"{stem}_heatmap.png"
            cv2.imwrite(str(heat_path), heatmap_img)
            res.heatmap_path = str(heat_path)

        # 4. Phase 7: Segmentation mask (if available)
        if mask is not None:
            mask_path = out_dir / f"{stem}_mask.png"
            cv2.imwrite(str(mask_path), mask)
            res.mask_path = str(mask_path)

        return res
