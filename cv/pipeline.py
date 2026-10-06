"""Pipeline orchestration. Connects stages; contains no stage logic."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import cv2

import config
from cv.detector import BaseDetector, NullDetector
from cv.heatmap import BaseHeatmapGenerator, NullHeatmapGenerator
from cv.image_loader import ImageLoader
from cv.localization import Localizer
from cv.preprocessing import Preprocessor
from cv.quality import QualityAnalyzer
from cv.schemas import AnalysisStatus, CVAnalysisResult, VisualizationResult
from cv.segmentation import BaseSegmenter, NullSegmenter
from cv.validator import ImageValidator
from cv.visualization import Visualizer
from utils.file_utils import ensure_dirs
from utils.logger import get_logger

logger = get_logger("pipeline")


class MedicalCVPipeline:
    """load -> validate -> quality (on original) -> preprocess -> save outputs -> return CVAnalysisResult."""

    def __init__(
        self,
        app_config: config.AppConfig = config.CONFIG,
        detector: Optional[BaseDetector] = None,
        heatmap: Optional[BaseHeatmapGenerator] = None,
        segmenter: Optional[BaseSegmenter] = None,
    ) -> None:
        self.config = app_config
        # 1. Image processing components (Phases 1-3)
        self.loader = ImageLoader(config.SUPPORTED_EXTENSIONS)
        self.validator = ImageValidator(app_config.validation)
        self.quality = QualityAnalyzer(app_config.quality)
        self.preprocessor = Preprocessor(app_config.preprocess)
        # 2. Model inference (swappable, untouched in Batch 1)
        self.detector: BaseDetector = detector or NullDetector()
        # 3. Visual explainability
        self.localizer = Localizer()
        self.heatmap = heatmap or NullHeatmapGenerator()
        self.segmenter = segmenter or NullSegmenter()
        self.visualizer = Visualizer()

    def initialize(self) -> None:
        """Prepare output dirs and report component readiness."""
        logger.info("Initializing pipeline...")
        ensure_dirs()
        for comp in (
            self.loader,
            self.validator,
            self.preprocessor,
            self.quality,
            self.detector,
            self.visualizer,
        ):
            if not comp.ready:
                raise RuntimeError(f"{comp.name} failed to initialize")
            logger.info("%s ready", comp.name)

    def run(self, image_path: Path | str, output_dir: Optional[Path | str] = None) -> CVAnalysisResult:
        """Analyze one medical image through active pipeline phases 1-3.

        Args:
            image_path: Path to input image or DICOM file.
            output_dir: Optional directory to save output artifacts (defaults to config.PROCESSED_DIR).

        Returns:
            CVAnalysisResult containing metadata, quality evaluation, and visualization paths.
        """
        path = Path(image_path)
        out_dir = Path(output_dir) if output_dir else config.PROCESSED_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        result = CVAnalysisResult(
            status=AnalysisStatus.NOT_RUN,
            model_loaded=self.detector.is_loaded,
        )

        try:
            # 1. Path existence and pre-check validation
            path_val = self.validator.validate_path(path)
            if not path_val.is_valid:
                result.status = AnalysisStatus.REJECTED
                result.errors.extend(path_val.reasons)
                return result

            # 2. Phase 1: Load image
            loaded = self.loader.load(path)
            result.metadata = loaded.metadata

            # 3. Phase 1: Full validation of decoded image
            validation = self.validator.validate(loaded)
            if not validation.is_valid:
                result.status = AnalysisStatus.REJECTED
                result.errors.extend(validation.reasons)
                logger.warning("Pipeline rejected %s: %s", path.name, "; ".join(validation.reasons))
                return result

            # 4. Phase 3: Quality assessment ON ORIGINAL (never CLAHE or preprocessed)
            quality_result = self.quality.assess(loaded.image)
            result.quality = quality_result
            if quality_result.issues:
                result.warnings.extend(quality_result.issues)

            # 5. Phase 2: OpenCV Preprocessing
            preprocessed = self.preprocessor.preprocess(loaded.image)

            # 6. Save visual artifacts (processed image and side-by-side comparison)
            processed_file = out_dir / f"{path.stem}_processed.png"
            cv2.imwrite(str(processed_file), preprocessed.image)

            comparison_img = self.visualizer.create_comparison(loaded.image, preprocessed.image)
            comparison_file = out_dir / f"{path.stem}_comparison.png"
            cv2.imwrite(str(comparison_file), comparison_img)

            result.visualization = VisualizationResult(
                processed_path=str(processed_file),
                comparison_path=str(comparison_file),
            )

            # 7. Model inference placeholder (NullDetector, no predict called in Batch 1)
            result.model_loaded = False
            result.detections = []

            result.status = AnalysisStatus.OK
            logger.info("Pipeline completed successfully for %s", path.name)

        except (FileNotFoundError, ValueError) as exc:
            result.status = AnalysisStatus.REJECTED
            result.errors.append(str(exc))
            logger.warning("Pipeline caught expected error on %s: %s", path.name, exc)
        except Exception as exc:
            result.status = AnalysisStatus.ERROR
            result.errors.append(str(exc))
            logger.exception("Unexpected pipeline failure on %s", path.name)
            raise

        return result
