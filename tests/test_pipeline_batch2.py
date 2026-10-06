"""Unit tests for integrated MedicalCVPipeline across Batch 2 (Phases 1-6)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
import numpy as np
import pytest

from cv.detector import MedicalDetector, NullDetector
from cv.heatmap import ModelHeatmapGenerator
from cv.pipeline import MedicalCVPipeline
from cv.schemas import AnalysisStatus, BoundingBox, Detection


class MockMedicalDetector(MedicalDetector):
    name = "Mock Medical Detector"

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


def test_pipeline_null_detector_fallback(tmp_path: Path) -> None:
    # Uses sample DICOM from input/sample_images
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    pipeline = MedicalCVPipeline(detector=NullDetector())
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert not result.model_loaded
    assert result.detections == []
    assert result.visualization is not None
    assert result.visualization.processed_path is not None
    assert result.visualization.comparison_path is not None
    assert result.visualization.overlay_path is None
    assert result.visualization.heatmap_path is None


def test_pipeline_auto_loads_real_model(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    assert pipeline.detector.is_loaded is True

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert result.model_loaded is True


def test_pipeline_mock_detector_single_detection(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    # Detection in 640x640 model space
    model_box = BoundingBox(x_min=150.0, y_min=200.0, x_max=350.0, y_max=450.0)
    det = Detection(label="Possible abnormal opacity", confidence=0.89, bbox=model_box)

    mock_detector = MockMedicalDetector(detections=[det])
    mock_heatmap = ModelHeatmapGenerator(is_available=True)

    pipeline = MedicalCVPipeline(detector=mock_detector, heatmap=mock_heatmap)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert result.model_loaded
    assert len(result.detections) == 1

    d = result.detections[0]
    assert d.label == "Possible abnormal opacity"
    assert d.confidence == 0.89
    assert d.bbox is not None

    # Sample_01 is 1024x1024 -> scale is 640 / 1024 = 0.625
    # Original coordinates must be restored: 150 / 0.625 = 240.0, 200 / 0.625 = 320.0
    assert pytest.approx(d.bbox.x_min, abs=1.0) == 240.0
    assert pytest.approx(d.bbox.y_min, abs=1.0) == 320.0

    # Visual artifacts generated
    assert result.visualization is not None
    assert result.visualization.overlay_path is not None
    assert Path(result.visualization.overlay_path).exists()
    assert result.visualization.heatmap_path is not None
    assert Path(result.visualization.heatmap_path).exists()


def test_pipeline_mock_detector_zero_detections(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    mock_detector = MockMedicalDetector(detections=[])
    mock_heatmap = ModelHeatmapGenerator(is_available=True)

    pipeline = MedicalCVPipeline(detector=mock_detector, heatmap=mock_heatmap)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert result.model_loaded
    assert result.detections == []
    # No fake overlays or heatmaps created
    assert result.visualization is not None
    assert result.visualization.overlay_path is None
    assert result.visualization.heatmap_path is None


def test_pipeline_mock_detector_multiple_detections(tmp_path: Path) -> None:
    sample_dcm = Path("input/sample_images/sample_01.dcm")
    if not sample_dcm.exists():
        pytest.skip("sample_01.dcm not found")

    # Bilateral findings in model space
    det_left = Detection(
        label="Possible abnormal opacity",
        confidence=0.85,
        bbox=BoundingBox(x_min=100.0, y_min=150.0, x_max=250.0, y_max=350.0),
    )
    det_right = Detection(
        label="Possible abnormal opacity",
        confidence=0.74,
        bbox=BoundingBox(x_min=380.0, y_min=180.0, x_max=520.0, y_max=390.0),
    )

    mock_detector = MockMedicalDetector(detections=[det_left, det_right])
    mock_heatmap = ModelHeatmapGenerator(is_available=True)

    pipeline = MedicalCVPipeline(detector=mock_detector, heatmap=mock_heatmap)
    pipeline.initialize()

    result = pipeline.run(sample_dcm, output_dir=tmp_path)
    assert result.status == AnalysisStatus.OK
    assert len(result.detections) == 2
    assert result.visualization is not None
    assert result.visualization.overlay_path is not None
    assert Path(result.visualization.overlay_path).exists()
    assert result.visualization.heatmap_path is not None
    assert Path(result.visualization.heatmap_path).exists()
