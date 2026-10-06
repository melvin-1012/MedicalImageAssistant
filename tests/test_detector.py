"""Unit tests for MedicalDetector interface and YOLOMedicalDetector."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
import numpy as np
import pytest

from cv.detector import (
    ModelNotLoadedError,
    NullDetector,
    YOLOMedicalDetector,
)
from cv.schemas import BoundingBox, Detection


def test_null_detector() -> None:
    detector = NullDetector()
    assert not detector.is_loaded
    assert detector.ready

    with pytest.raises(ModelNotLoadedError):
        detector.load_model()

    dummy_img = np.zeros((640, 640), dtype=np.uint8)
    with pytest.raises(ModelNotLoadedError):
        detector.predict(dummy_img)

    info = detector.get_model_info()
    assert info["name"] == "NullDetector"
    assert not info["is_loaded"]


def test_yolo_detector_initialization() -> None:
    detector = YOLOMedicalDetector(confidence_threshold=0.3, iou_threshold=0.5)
    assert not detector.is_loaded
    assert detector.ready
    assert detector.confidence_threshold == 0.3
    assert detector.iou_threshold == 0.5
    assert detector.target_label == "Possible abnormal opacity"


def test_yolo_detector_missing_weights() -> None:
    detector = YOLOMedicalDetector(model_path=Path("non_existent_weights.pt"))
    with pytest.raises(FileNotFoundError):
        detector.load_model()


def test_yolo_detector_predict_not_loaded() -> None:
    detector = YOLOMedicalDetector()
    dummy_img = np.zeros((640, 640), dtype=np.uint8)
    with pytest.raises(ModelNotLoadedError):
        detector.predict(dummy_img)


def test_yolo_detector_mock_predict_no_detections() -> None:
    detector = YOLOMedicalDetector()
    # Mock loaded model
    mock_model = MagicMock()
    mock_result = MagicMock()
    mock_result.boxes = []
    mock_model.predict.return_value = [mock_result]
    detector._model = mock_model

    dummy_img = np.zeros((640, 640), dtype=np.uint8)
    detections = detector.predict(dummy_img)
    assert detections == []


def test_yolo_detector_mock_predict_single_and_multiple() -> None:
    detector = YOLOMedicalDetector()
    mock_model = MagicMock()

    # Simulate 2 detections
    box1 = MagicMock()
    box1.xyxy = [np.array([100.0, 150.0, 250.0, 350.0])]
    box1.conf = [np.float32(0.85)]

    box2 = MagicMock()
    box2.xyxy = [np.array([320.0, 180.0, 480.0, 390.0])]
    box2.conf = [np.float32(0.72)]

    mock_result = MagicMock()
    mock_result.boxes = [box1, box2]
    mock_model.predict.return_value = [mock_result]
    detector._model = mock_model

    dummy_img = np.zeros((640, 640), dtype=np.uint8)
    detections = detector.predict(dummy_img)

    assert len(detections) == 2
    assert detections[0].label == "Possible abnormal opacity"
    assert detections[0].confidence == 0.85
    assert detections[0].bbox == BoundingBox(x_min=100.0, y_min=150.0, x_max=250.0, y_max=350.0)

    assert detections[1].label == "Possible abnormal opacity"
    assert detections[1].confidence == 0.72
    assert detections[1].bbox == BoundingBox(x_min=320.0, y_min=180.0, x_max=480.0, y_max=390.0)


def test_yolo_detector_empty_input_validation() -> None:
    detector = YOLOMedicalDetector()
    detector._model = MagicMock()

    with pytest.raises(ValueError):
        detector.predict(np.array([]))


def test_yolo_detector_get_model_info() -> None:
    detector = YOLOMedicalDetector(confidence_threshold=0.25)
    info = detector.get_model_info()
    assert info["architecture"] == "YOLO"
    assert info["target_label"] == "Possible abnormal opacity"
    assert info["confidence_threshold"] == 0.25
    assert not info["is_loaded"]


def test_create_detector_fallback_to_null() -> None:
    from cv.detector import create_detector, NullDetector
    det = create_detector(model_path="non_existent_weights_12345.pt")
    assert isinstance(det, NullDetector)
    assert not det.is_loaded


def test_find_available_weights_handles_missing(tmp_path: Path) -> None:
    from cv.detector import find_available_weights
    # If no weights exist in standard dirs, returns None safely
    weights = find_available_weights()
    assert weights is None or isinstance(weights, Path)

