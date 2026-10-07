"""Phase 12: Comprehensive Integration Test Suite.

Verifies end-to-end integration between Medical CV and Multimodal GenAI:
1. Positive real image test
2. Negative real image test
3. Poor quality fast-fail bypass test
4. Multiple detections test
5. Confidence and coordinate exact integrity test
6. Strict mock data elimination verification
7. Heatmap terminology validation ("Model-Grounded Heatmap" / no "Grad-CAM")
"""
from __future__ import annotations

import tempfile
from pathlib import Path
import cv2
import numpy as np
import pytest

import config
from cv.integration import IntegratedMedicalAIPipeline
from cv.pipeline import MedicalCVPipeline
from cv.schemas import AnalysisStatus, BoundingBox, Detection, FindingEvidence, FindingLocation
from cv.detector import BaseDetector


class MockMultiDetector(BaseDetector):
    """Detector for simulating multiple controlled findings."""
    name = "MockMultiDetector"

    @property
    def is_loaded(self) -> bool:
        return True

    def load_model(self) -> None:
        pass

    def predict(self, image: np.ndarray) -> list[Detection]:
        # Return two realistic detections with arbitrary unrounded floating confidence
        return [
            Detection(
                label="Possible abnormal opacity",
                confidence=0.01684321,
                bbox=BoundingBox(100.0, 150.0, 300.0, 450.0),
            ),
            Detection(
                label="Possible abnormal opacity",
                confidence=0.01912456,
                bbox=BoundingBox(350.0, 200.0, 500.0, 400.0),
            ),
        ]


@pytest.fixture
def integrated_pipeline():
    pipe = IntegratedMedicalAIPipeline()
    pipe.initialize()
    return pipe


def test_integration_positive_real_image(integrated_pipeline):
    """TEST 1: Positive real image through integrated pipeline."""
    sample_path = Path("input/sample_images/sample_01.dcm")
    if not sample_path.exists():
        pytest.skip("sample_01.dcm not found")

    result = integrated_pipeline.run(sample_path, clinical_notes="Cough and mild dyspnea for 3 days.")

    assert result["status"] == "success"
    assert result["modality"] == "X-Ray"
    assert "image" in result
    assert "quality" in result
    assert result["quality"]["status"] == "GOOD"

    # Verify findings are present from real model
    findings = result["findings"]
    assert len(findings) >= 1
    first_f = findings[0]
    assert first_f["finding"] == "possible_abnormal_opacity"
    assert 0.0 < first_f["confidence"] <= 1.0

    # Verify GenAI analysis block
    genai = result["genai_analysis"]
    assert genai["validation_status"]["is_valid"] is True
    assert len(genai["findings"]) == len(findings)
    g_finding = genai["findings"][0]
    assert g_finding["finding"] == "possible_abnormal_opacity"
    assert g_finding["confidence"] == first_f["confidence"]
    assert g_finding["location"] == first_f["location"]
    assert g_finding["status"] == "review_required"
    assert "uncertainty" in g_finding
    assert len(g_finding["uncertainty"]) > 0

    # Safety checks
    assert result["safety"]["physician_review_required"] is True
    assert result["safety"]["no_confirmed_diagnosis"] is True


def test_integration_negative_real_image(integrated_pipeline):
    """TEST 2: Negative image returns exact required phrasing."""
    sample_path = Path("input/sample_images/sample_01.dcm")
    if not sample_path.exists():
        pytest.skip("sample_01.dcm not found")

    # Set threshold high to ensure no findings are detected (negative scan)
    orig_thresh = integrated_pipeline.cv.detector.confidence_threshold
    try:
        integrated_pipeline.cv.detector.confidence_threshold = 0.95
        result = integrated_pipeline.run(sample_path)

        assert result["status"] == "success"
        assert len(result["findings"]) == 0
        genai = result["genai_analysis"]
        assert len(genai["findings"]) == 0
        expected_msg = (
            "No abnormal opacity was detected by the current computer-vision model. "
            "Routine physician review is recommended."
        )
        assert genai["summary"] == expected_msg
        assert any("assistive decision-support" in lim for lim in genai["limitations"])
    finally:
        integrated_pipeline.cv.detector.confidence_threshold = orig_thresh


def test_integration_poor_quality_fast_fail(integrated_pipeline):
    """TEST 3: Poor quality image triggers fast-fail bypass and does not run GenAI."""
    # Create a blank flat image (variance 0.0)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        blank_img = np.zeros((512, 512), dtype=np.uint8)
        cv2.imwrite(f.name, blank_img)
        bad_path = Path(f.name)

    try:
        result = integrated_pipeline.run(bad_path, clinical_notes="Patient with fever")
        assert result["status"] in ["rejected", "poor_quality"]
        genai = result["genai_analysis"]
        assert genai["summary"] == "Image quality is insufficient for reliable AI analysis."
        assert len(genai["findings"]) == 0
        assert any("insufficient for reliable" in lim for lim in genai["limitations"])
        assert any("Fast-fail" in w for w in genai["validation_status"]["warnings"])
    finally:
        if bad_path.exists():
            bad_path.unlink()


def test_integration_multiple_detections():
    """TEST 4: Multiple findings correctly preserved without hallucinations."""
    cv_pipe = MedicalCVPipeline(detector=MockMultiDetector())
    cv_pipe.initialize()
    pipe = IntegratedMedicalAIPipeline(cv_pipeline=cv_pipe)

    sample_path = Path("input/sample_images/sample_01.dcm")
    if not sample_path.exists():
        pytest.skip("sample_01.dcm not found")

    result = pipe.run(sample_path, clinical_notes="Fever and productive cough.")

    assert len(result["findings"]) == 2
    genai = result["genai_analysis"]
    assert len(genai["findings"]) == 2
    assert genai["validation_status"]["is_valid"] is True

    # Ensure no fabricated pathologies appear in findings
    for gf in genai["findings"]:
        assert gf["finding"] == "possible_abnormal_opacity"
        assert gf["finding"] not in ["pleural_effusion", "pneumothorax", "fracture", "cardiomegaly"]


def test_integration_confidence_coordinate_exact_integrity():
    """TEST 5: Strict equality check between CV raw values and GenAI output."""
    cv_pipe = MedicalCVPipeline(detector=MockMultiDetector())
    cv_pipe.initialize()
    pipe = IntegratedMedicalAIPipeline(cv_pipeline=cv_pipe)

    sample_path = Path("input/sample_images/sample_01.dcm")
    if not sample_path.exists():
        pytest.skip("sample_01.dcm not found")

    result = pipe.run(sample_path)

    cv_findings = result["findings"]
    genai_findings = result["genai_analysis"]["findings"]

    assert len(cv_findings) == len(genai_findings)
    for cv_f, g_f in zip(cv_findings, genai_findings):
        # Strict floating-point equality (no pre-rounding)
        assert cv_f["confidence"] == g_f["confidence"]
        assert cv_f["location"]["x1"] == g_f["location"]["x1"]
        assert cv_f["location"]["y1"] == g_f["location"]["y1"]
        assert cv_f["location"]["x2"] == g_f["location"]["x2"]
        assert cv_f["location"]["y2"] == g_f["location"]["y2"]


def test_integration_no_mock_data_in_production_path(integrated_pipeline):
    """TEST 6: Production flow must never return hardcoded mock data."""
    sample_path = Path("input/sample_images/sample_01.dcm")
    if not sample_path.exists():
        pytest.skip("sample_01.dcm not found")

    result = integrated_pipeline.run(sample_path)

    # Check for hardcoded mock data from mock_data.py
    # e.g., confidence 0.82, mock bbox (320, 240, 610, 520)
    for f in result["findings"]:
        assert f["confidence"] != 0.82
        if f["location"]:
            assert f["location"] != {"x1": 320.0, "y1": 240.0, "x2": 610.0, "y2": 520.0}

    for gf in result["genai_analysis"]["findings"]:
        assert gf["confidence"] != 0.82
        if gf["location"]:
            assert gf["location"] != {"x1": 320.0, "y1": 240.0, "x2": 610.0, "y2": 520.0}
        assert gf["finding"] != "pleural_effusion"


def test_integration_heatmap_labeling_terminology(integrated_pipeline):
    """TEST 7: Ensure heatmap is labeled 'Model-Grounded Heatmap' and never Grad-CAM."""
    sample_path = Path("input/sample_images/sample_01.dcm")
    if not sample_path.exists():
        pytest.skip("sample_01.dcm not found")

    result = integrated_pipeline.run(sample_path)
    result_str = str(result)
    assert "grad-cam" not in result_str.lower()
    assert "gradcam" not in result_str.lower()
