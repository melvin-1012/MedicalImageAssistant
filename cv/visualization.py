"""Visual output: boxes, confidence labels, overlays, comparisons."""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from cv.schemas import Detection, VisualizationResult


class Visualizer:
    """Renders results; heatmap/mask layers appear only when provided."""

    name = "Visualization engine"

    @property
    def ready(self) -> bool:
        return True

    def render(self, original: np.ndarray, processed: Optional[np.ndarray],
               detections: List[Detection], heatmap: Optional[np.ndarray] = None,
               mask: Optional[np.ndarray] = None) -> VisualizationResult:
        """Draw and save outputs. Implemented progressively (Phase 5-7)."""
        raise NotImplementedError("Visualizer.render: Phase 5")
