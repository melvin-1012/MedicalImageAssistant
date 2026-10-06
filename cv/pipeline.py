"""Pipeline orchestration. Connects stages; contains no stage logic."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import config
from cv.detector import BaseDetector, NullDetector
from cv.heatmap import BaseHeatmapGenerator, NullHeatmapGenerator
from cv.image_loader import ImageLoader
from cv.localization import Localizer
from cv.preprocessing import Preprocessor
from cv.quality import QualityAnalyzer
from cv.schemas import AnalysisStatus, CVAnalysisResult
from cv.segmentation import BaseSegmenter, NullSegmenter
from cv.validator import ImageValidator
from cv.visualization import Visualizer
from utils.file_utils import ensure_dirs
from utils.logger import get_logger

logger = get_logger("pipeline")


class MedicalCVPipeline:
    """load -> validate -> quality -> preprocess -> detect -> localize -> visualize."""

    def __init__(self, app_config: config.AppConfig = config.CONFIG,
                 detector: Optional[BaseDetector] = None,
                 heatmap: Optional[BaseHeatmapGenerator] = None,
                 segmenter: Optional[BaseSegmenter] = None) -> None:
        self.config = app_config
        # 1. image processing
        self.loader = ImageLoader()
        self.validator = ImageValidator(app_config.validation)
        self.quality = QualityAnalyzer(app_config.quality)
        self.preprocessor = Preprocessor(app_config.preprocess)
        # 2. model inference (swappable)
        self.detector: BaseDetector = detector or NullDetector()
        # 3. visual explainability
        self.localizer = Localizer()
        self.heatmap = heatmap or NullHeatmapGenerator()
        self.segmenter = segmenter or NullSegmenter()
        self.visualizer = Visualizer()

    def initialize(self) -> None:
        """Prepare output dirs and report component readiness."""
        logger.info("Initializing pipeline...")
        ensure_dirs()
        for comp in (self.loader, self.validator, self.preprocessor,
                     self.quality, self.detector, self.visualizer):
            if not comp.ready:
                raise RuntimeError(f"{comp.name} failed to initialize")
            logger.info("%s ready", comp.name)

    def run(self, image_path: Path) -> CVAnalysisResult:
        """Analyse one image. Stages are wired in Phases 1-9."""
        result = CVAnalysisResult(status=AnalysisStatus.NOT_RUN,
                                  model_loaded=self.detector.is_loaded)
        # Phase 1: loaded = self.loader.load(image_path)
        #          check = self.validator.validate(loaded)
        # Phase 3: result.quality = self.quality.assess(loaded.image)
        # Phase 2: prepped = self.preprocessor.preprocess(loaded.image)
        # Phase 4: detections = self.detector.predict(prepped.image)
        # Phase 5: detections = self.localizer.localize(...)
        # Phase 6/7: optional heatmap / segmentation
        # Phase 5+: result.visualization = self.visualizer.render(...)
        self.loader.load(Path(image_path))  # raises NotImplementedError (Phase 1)
        return result
