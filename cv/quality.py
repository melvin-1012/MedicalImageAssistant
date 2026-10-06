"""Image quality assessment: blur, exposure, contrast, resolution, noise."""
from __future__ import annotations

import numpy as np

from config import QualityConfig
from cv.schemas import ImageQualityResult


class QualityAnalyzer:
    """Scores an image and labels it GOOD / MODERATE / POOR."""

    name = "Quality analyzer"

    def __init__(self, config: QualityConfig | None = None) -> None:
        self.config = config or QualityConfig()

    @property
    def ready(self) -> bool:
        return True

    def assess(self, image: np.ndarray) -> ImageQualityResult:
        """Compute quality metrics and overall score. Phase 3."""
        raise NotImplementedError("QualityAnalyzer.assess: Phase 3")
