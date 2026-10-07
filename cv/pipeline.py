"""Pipeline orchestration for the Medical Computer Vision Engine (Batch 1 + Batch 2).

Connects:
Load (Phase 1)
-> Validate (Phase 1)
-> Quality (Phase 3 on original)
-> Preprocess (Phase 2)
-> Model Inference (Phase 4)
-> Localization (Phase 5)
-> Heatmap / Explainability (Phase 6)
-> Visualization artifacts
-> CVAnalysisResult
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import config
from cv.detector import BaseDetector, NullDetector, create_detector
from cv.classifier import BaseClassifier, NullClassifier
from cv.heatmap import BaseHeatmapGenerator, ModelHeatmapGenerator, NullHeatmapGenerator
from cv.image_loader import ImageLoader
from cv.localization import Localizer
from cv.preprocessing import Preprocessor
from cv.quality import QualityAnalyzer
from cv.schemas import (
    AnalysisStatus,
    CVAnalysisResult,
    FindingEvidence,
    FindingLocation,
)
from cv.segmentation import BaseSegmenter, NullSegmenter
from cv.validator import ImageValidator
from cv.visualization import Visualizer
from utils.file_utils import ensure_dirs
from utils.logger import get_logger

logger = get_logger("pipeline")


class MedicalCVPipeline:
    """Orchestrates image intake, validation, quality, preprocessing, inference, and explainability."""

    def __init__(
        self,
        app_config: config.AppConfig = config.CONFIG,
        detector: Optional[BaseDetector] = None,
        classifier: Optional[BaseClassifier] = None,
        heatmap: Optional[BaseHeatmapGenerator] = None,
        segmenter: Optional[BaseSegmenter] = None,
    ) -> None:
        self.config = app_config
        # 1. Image processing components (Phases 1-3)
        self.loader = ImageLoader(config.SUPPORTED_EXTENSIONS)
        self.validator = ImageValidator(app_config.validation)
        self.quality = QualityAnalyzer(app_config.quality)
        self.preprocessor = Preprocessor(app_config.preprocess)
        # 2. Model inference (Phase 4): auto-detect weights or safe NullDetector fallback
        self.detector: BaseDetector = detector or create_detector(
            app_config.detector.model_path,
            confidence_threshold=app_config.detector.confidence_threshold,
            iou_threshold=app_config.detector.iou_threshold,
        )
        self.classifier: BaseClassifier = classifier or NullClassifier()
        # 3. Visual explainability (Phases 5-6)
        self.localizer = Localizer()
        self.heatmap: BaseHeatmapGenerator = heatmap or (
            ModelHeatmapGenerator(is_available=True) if self.detector.is_loaded else NullHeatmapGenerator()
        )
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
            self.localizer,
            self.segmenter,
            self.visualizer,
        ):
            if not comp.ready:
                raise RuntimeError(f"{comp.name} failed to initialize")
            logger.info("%s ready", comp.name)

    def run(self, image_path: Path | str, output_dir: Optional[Path | str] = None) -> CVAnalysisResult:
        """Analyze one medical image through active pipeline phases 1-9.

        Args:
            image_path: Path to input image or DICOM file.
            output_dir: Optional directory to save output artifacts (defaults to config.PROCESSED_DIR).

        Returns:
            CVAnalysisResult containing metadata, quality evaluation, detections, findings evidence,
            segmentation status, and visualization paths.
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

            # 5. Phase 2: OpenCV Preprocessing (produces display uint8 + normalized float32 model input)
            preprocessed = self.preprocessor.preprocess(loaded.image)

            # 6. Phase 4: Model Inference (YOLO Detection)
            orig_size = (loaded.metadata.width, loaded.metadata.height)
            raw_model_detections = []
            if self.detector.is_loaded:
                raw_model_detections = self.detector.predict(preprocessed.image)
                result.model_loaded = True
            else:
                result.model_loaded = False

            # Phase 4b: Image Classification (DenseNet-121)
            if self.classifier.is_loaded:
                result.classification = self.classifier.predict(loaded.image)

            # 7. Phase 5: Localization (map model-space boxes to original image coordinates)
            if raw_model_detections:
                localized_detections = self.localizer.localize(
                    raw_model_detections, preprocessed.transform, orig_size
                )
            else:
                localized_detections = []

            result.detections = localized_detections

            # 8. Phase 6: Heatmap / Model-grounded explainability
            aligned_heatmap = None
            if self.heatmap.is_available and raw_model_detections:
                model_heatmap = self.heatmap.generate(preprocessed.image, detections=raw_model_detections)
                if model_heatmap is not None:
                    aligned_heatmap = BaseHeatmapGenerator.align_to_original(
                        model_heatmap, preprocessed.transform, orig_size
                    )

            # 9. Phase 7: Segmentation (handles graceful unavailability when masks are not in dataset)
            aligned_mask = None
            if self.segmenter.is_available:
                raw_mask = self.segmenter.segment(preprocessed.image)
                if raw_mask is not None:
                    aligned_mask = BaseSegmenter.align_to_original(
                        raw_mask, preprocessed.transform, orig_size
                    )
            seg_info = self.segmenter.get_segmentation_info()
            result.segmentation_status = str(seg_info.get("status", "unavailable"))
            result.segmentation_note = str(seg_info.get("reason", ""))

            # 10. Phase 8: Confidence + Evidence aggregation for CV -> GenAI contract
            findings_list: List[FindingEvidence] = []
            for det in localized_detections:
                loc = FindingLocation(
                    x1=round(float(det.bbox.x_min), 1) if det.bbox else 0.0,
                    y1=round(float(det.bbox.y_min), 1) if det.bbox else 0.0,
                    x2=round(float(det.bbox.x_max), 1) if det.bbox else 0.0,
                    y2=round(float(det.bbox.y_max), 1) if det.bbox else 0.0,
                )
                fe = FindingEvidence(
                    finding="possible_abnormal_opacity",
                    finding_label="Possible abnormal opacity",
                    confidence=round(float(det.confidence), 4),
                    location=loc,
                    heatmap_available=(aligned_heatmap is not None),
                    segmentation_available=bool(self.segmenter.is_available and aligned_mask is not None),
                    requires_physician_review=True,
                )
                findings_list.append(fe)
            result.findings = findings_list

            # 11. Visualization: Render outputs (processed, comparison, detection overlay, heatmap, mask)
            vis_res = self.visualizer.render(
                original=loaded.image,
                processed=preprocessed.image,
                detections=localized_detections,
                heatmap=aligned_heatmap,
                mask=aligned_mask,
                output_dir=out_dir,
                stem=path.stem,
            )
            result.visualization = vis_res

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
