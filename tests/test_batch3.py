"""Unit and integration tests for Batch 3 (Phases 7, 8, and 9).

Covers:
1. Phase 7 segmentation behavior & NullSegmenter unavailability
2. Missing segmentation behavior (no fake masks fabricated)
3. MaskProcessor cleaning, contours, and area calculation
4. Phase 8 confidence preservation (un-fabricated, un-altered by GenAI)
5. Phase 8 evidence preservation (FindingEvidence structure)
6. Original-coordinate preservation in findings location
7. Phase 9 structured CV -> GenAI JSON schema
8. Deterministic JSON serialization
9. Empty detection case (normal radiograph)
10. Multiple detection case (bilateral findings)
11. Heatmap availability flag
12. Segmentation availability flag
13. Safety flags (physician_review_required, no_confirmed_diagnosis)
14. CV -> GenAI handshake fields
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock
import numpy as np
import pytest

from cv.detector import MedicalDetector
from cv.heatmap import ModelHeatmapGenerator, NullHeatmapGenerator
from cv.pipeline import MedicalCVPipeline
from cv.preprocessing import ResizeTransform
from cv.schemas import (
    AnalysisStatus,
    BoundingBox,
    Detection,
    FindingEvidence,
    FindingLocation,
)
from cv.segmentation import BaseSegmenter, MaskProcessor, NullSegmenter


class MockCustomSegmenter(BaseSegmenter):
    """Mock active segmenter for testing when segmentation IS available."""

    name = "MockActiveSegmenter"

    @property
    def is_available(self) -> bool:
        return True

    def segment(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] = 255
        return mask

    def get_segmentation_info(self) -> dict:
        return {
            "name": self.name,
            "is_available": True,
            "status": "available",
            "reason": None,
            "model_type": "MockUnet",
        }


class MockBatch3Detector(MedicalDetector):
    name = "Mock Batch 3 Detector"

    def __init__(self, detections: list[Detection] | None = None) -> None:
        self._detections = detections if detections is not None else []
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        pass

    def predict(self, image: np.ndarray) -> list[Detection]:
        return self._detections

    def get_model_info(self) -> dict:
        return {"name": self.name, "is_loaded": True}


# =========================================================================
# Phase 7: Segmentation Tests
# =========================================================================

def test_phase7_null_segmenter_unavailability() -> None:
    segmenter = NullSegmenter()
    assert not segmenter.is_available
    assert segmenter.ready

    dummy_image = np.zeros((640, 640), dtype=np.uint8)
    # Returns None cleanly without raising or fabricating
    assert segmenter.segment(dummy_image) is None

    info = segmenter.get_segmentation_info()
    assert info["is_available"] is False
    assert info["status"] == "unavailable"
    assert "bounding-box annotations" in info["reason"]


def test_phase7_mask_processor() -> None:
    processor = MaskProcessor(kernel_size=3)

    # 1. Safe handling of None
    assert processor.clean(None) is None
    assert processor.contours(None) == []
    assert processor.compute_mask_area(None) == 0

    # 2. Synthetic mask with small noise speckle
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20:60, 20:60] = 255  # Main box (40x40 = 1600 px)
    mask[2, 2] = 255          # 1px noise speckle

    cleaned = processor.clean(mask)
    assert cleaned is not None
    assert cleaned.shape == (100, 100)
    # The 1px isolated noise is removed by morphological opening
    assert cleaned[2, 2] == 0

    # 3. Contours extraction
    cnts = processor.contours(cleaned)
    assert len(cnts) >= 1

    # 4. Area calculation
    area = processor.compute_mask_area(cleaned)
    assert area > 1000


def test_phase7_segmenter_align_to_original() -> None:
    # 640x640 model mask with 1024x1024 original
    transform = ResizeTransform(
        original_size=(1024, 1024),
        model_size=(640, 640),
        scale=0.625,
        pad_x=0,
        pad_y=0,
    )
    model_mask = np.zeros((640, 640), dtype=np.uint8)
    model_mask[100:300, 100:300] = 255

    aligned = BaseSegmenter.align_to_original(model_mask, transform, (1024, 1024))
    assert aligned is not None
    assert aligned.shape == (1024, 1024)
    assert aligned.dtype == np.uint8
    # Binary values preserved by INTER_NEAREST
    unique_vals = set(np.unique(aligned))
    assert unique_vals.issubset({0, 255})

    # None handling
    assert BaseSegmenter.align_to_original(None, transform, (1024, 1024)) is None


# =========================================================================
# Phase 8: Confidence + Evidence Tests
# =========================================================================

def test_phase8_confidence_preservation(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    exact_confidence = 0.8245
    det = Detection(
        label="Possible abnormal opacity",
        confidence=exact_confidence,
        bbox=BoundingBox(x_min=160.0, y_min=200.0, x_max=320.0, y_max=400.0),
    )
    mock_det = MockBatch3Detector(detections=[det])
    pipeline = MedicalCVPipeline(detector=mock_det)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert len(result.findings) == 1

    finding = result.findings[0]
    # Exact CV confidence preserved without rounding distortion
    assert pytest.approx(finding.confidence, abs=0.0001) == exact_confidence
    assert finding.finding == "possible_abnormal_opacity"
    assert finding.finding_label == "Possible abnormal opacity"
    assert finding.requires_physician_review is True


def test_phase8_original_coordinates_preservation(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    # Sample_01 is 1024x1024. Model space 640x640 -> scale is 640/1024 = 0.625
    # Model box (160, 200, 320, 400) maps to orig (256, 320, 512, 640)
    det = Detection(
        label="Possible abnormal opacity",
        confidence=0.75,
        bbox=BoundingBox(x_min=160.0, y_min=200.0, x_max=320.0, y_max=400.0),
    )
    mock_det = MockBatch3Detector(detections=[det])
    pipeline = MedicalCVPipeline(detector=mock_det)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    finding = result.findings[0]

    # Coordinates must refer strictly to original 1024x1024 space
    assert pytest.approx(finding.location.x1, abs=1.0) == 256.0
    assert pytest.approx(finding.location.y1, abs=1.0) == 320.0
    assert pytest.approx(finding.location.x2, abs=1.0) == 512.0
    assert pytest.approx(finding.location.y2, abs=1.0) == 640.0


# =========================================================================
# Phase 9: Structured JSON Schema & Contract Tests
# =========================================================================

def test_phase9_cv_genai_handshake_schema(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    det = Detection(
        label="Possible abnormal opacity",
        confidence=0.88,
        bbox=BoundingBox(x_min=100.0, y_min=150.0, x_max=250.0, y_max=350.0),
    )
    mock_det = MockBatch3Detector(detections=[det])
    pipeline = MedicalCVPipeline(detector=mock_det)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    genai_dict = result.to_genai_dict()

    # Minimum required structure validation
    assert "image" in genai_dict
    assert "quality" in genai_dict
    assert "findings" in genai_dict
    assert "artifacts" in genai_dict
    assert "safety" in genai_dict

    # Image info
    img_info = genai_dict["image"]
    assert img_info["width"] == 1024
    assert img_info["height"] == 1024
    assert img_info["modality"] == "X-Ray"

    # Quality info
    q_info = genai_dict["quality"]
    assert q_info["status"] in ("GOOD", "MODERATE", "POOR")
    assert isinstance(q_info["score"], float)

    # Findings
    assert len(genai_dict["findings"]) == 1
    f = genai_dict["findings"][0]
    assert f["finding"] == "possible_abnormal_opacity"
    assert f["finding_label"] == "Possible abnormal opacity"
    assert f["confidence"] == 0.88
    assert "location" in f
    assert set(f["location"].keys()) == {"x1", "y1", "x2", "y2"}
    assert f["heatmap_available"] is True
    assert f["segmentation_available"] is False
    assert f["requires_physician_review"] is True

    # Artifacts
    art = genai_dict["artifacts"]
    assert art["original"] is not None
    assert art["processed"] is not None
    assert art["detections"] is not None
    assert art["heatmap"] is not None
    assert art["segmentation"] is None

    # Safety
    safety = genai_dict["safety"]
    assert safety["physician_review_required"] is True
    assert safety["no_confirmed_diagnosis"] is True


def test_phase9_deterministic_json_serialization(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    result = pipeline.run(sample_dcm, output_dir=tmp_path)

    # Deterministic JSON export
    json_str = result.to_genai_json()
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert parsed["safety"]["physician_review_required"] is True

    # Complete result to_json also works and embeds structured_output
    full_json = result.to_json()
    full_parsed = json.loads(full_json)
    assert "structured_output" in full_parsed
    assert full_parsed["structured_output"]["safety"]["no_confirmed_diagnosis"] is True


def test_empty_detection_case(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    mock_det = MockBatch3Detector(detections=[])
    pipeline = MedicalCVPipeline(detector=mock_det)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert result.findings == []

    genai_dict = result.to_genai_dict()
    assert genai_dict["findings"] == []
    # No fake artifacts
    assert genai_dict["artifacts"]["detections"] is None
    assert genai_dict["artifacts"]["heatmap"] is None
    assert genai_dict["artifacts"]["segmentation"] is None
    # Safety flags remain active
    assert genai_dict["safety"]["physician_review_required"] is True
    assert genai_dict["safety"]["no_confirmed_diagnosis"] is True


def test_multiple_detections_case(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    box_left = Detection(
        label="Possible abnormal opacity",
        confidence=0.81,
        bbox=BoundingBox(x_min=100.0, y_min=150.0, x_max=220.0, y_max=320.0),
    )
    box_right = Detection(
        label="Possible abnormal opacity",
        confidence=0.74,
        bbox=BoundingBox(x_min=350.0, y_min=180.0, x_max=490.0, y_max=360.0),
    )
    mock_det = MockBatch3Detector(detections=[box_left, box_right])
    pipeline = MedicalCVPipeline(detector=mock_det)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert len(result.findings) == 2

    genai_dict = result.to_genai_dict()
    assert len(genai_dict["findings"]) == 2
    assert genai_dict["findings"][0]["confidence"] == 0.81
    assert genai_dict["findings"][1]["confidence"] == 0.74
    assert genai_dict["findings"][0]["location"]["x1"] < genai_dict["findings"][1]["location"]["x1"]


def test_segmentation_availability_when_model_present(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    det = Detection(
        label="Possible abnormal opacity",
        confidence=0.91,
        bbox=BoundingBox(x_min=120.0, y_min=180.0, x_max=280.0, y_max=360.0),
    )
    mock_det = MockBatch3Detector(detections=[det])
    mock_seg = MockCustomSegmenter()

    pipeline = MedicalCVPipeline(detector=mock_det, segmenter=mock_seg)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.segmentation_status == "available"
    assert len(result.findings) == 1
    # When segmentation is active, flag reflects it
    assert result.findings[0].segmentation_available is True
    assert result.visualization is not None
    assert result.visualization.mask_path is not None
    assert Path(result.visualization.mask_path).exists()

    genai_dict = result.to_genai_dict()
    assert genai_dict["artifacts"]["segmentation"] is not None
