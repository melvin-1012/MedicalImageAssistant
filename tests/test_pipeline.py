import json
import pytest
from cv.pipeline import MedicalCVPipeline
from cv.schemas import CVAnalysisResult


def test_pipeline_initializes_without_model():
    p = MedicalCVPipeline()
    p.initialize()
    assert p.detector.is_loaded is False


def test_result_serialises_to_json():
    data = json.loads(CVAnalysisResult().to_json())
    assert data["status"] == "not_run"
    assert data["detections"] == []


def test_run_not_implemented_until_phase_1():
    with pytest.raises(NotImplementedError):
        MedicalCVPipeline().run("x.png")
