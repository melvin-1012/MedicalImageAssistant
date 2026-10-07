"""
Tests: Imaging Upload Validation & AI Analysis Pipeline

Covers:
- Image validation (valid and invalid formats, size limits)
- Vision AI and GenAI service interface outputs
- Triggering analysis pipeline
- Separation of AI findings from doctor clinical assessments
"""

import pytest
from unittest.mock import patch, MagicMock
from app.utils.validation import (
    validate_image_file,
    validate_mr_number,
    validate_imaging_type,
    sanitise_filename,
    MAX_IMAGE_SIZE_BYTES,
)
from app.services.vision_service import analyze_image, VisionResult
from app.services.genai_service import generate_clinical_context, GenAIResult
from tests.conftest import SPECIALIST_HEADERS, DOCTOR_HEADERS, PATIENT_HEADERS
from fastapi import HTTPException


def test_validation_utilities():
    # MR Number
    assert validate_mr_number("mr-2024-0001") == "MR-2024-0001"
    with pytest.raises(HTTPException):
        validate_mr_number("INVALID-MR")

    # Imaging type
    assert validate_imaging_type("XRAY") == "xray"
    assert validate_imaging_type("CT_SCAN") == "ct_scan"
    assert validate_imaging_type("MRI") == "mri"
    with pytest.raises(HTTPException):
        validate_imaging_type("PET_SCAN")

    # Filename sanitization
    assert sanitise_filename("scan../../test.png") == "scan______test.png"

    # Valid image file
    validate_image_file("scan.jpg", "image/jpeg", 1024 * 1024)

    # Invalid extension
    with pytest.raises(HTTPException):
        validate_image_file("malicious.exe", "image/jpeg", 1024)

    # Invalid MIME type
    with pytest.raises(HTTPException):
        validate_image_file("scan.jpg", "application/x-msdownload", 1024)

    # File too large (>50MB)
    with pytest.raises(HTTPException):
        validate_image_file("huge.png", "image/png", MAX_IMAGE_SIZE_BYTES + 100)


@pytest.mark.asyncio
async def test_vision_service_interface():
    """Verify Vision AI interface returns compliant VisionResult."""
    result: VisionResult = await analyze_image(
        image_path="test/path.jpg",
        imaging_type="xray",
    )
    assert isinstance(result, VisionResult)
    assert result.is_mock is True
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.finding is not None
    assert result.location is not None
    assert result.model_name is not None


@pytest.mark.asyncio
async def test_genai_service_interface():
    """Verify GenAI multimodal interface returns compliant GenAIResult."""
    vision_mock = VisionResult(
        finding="Consolidation in right lower lobe",
        location="Right lung",
        confidence_score=0.88,
    )
    result: GenAIResult = await generate_clinical_context(
        vision_result=vision_mock,
        patient_context={"symptoms": "Cough and fever", "age": 45, "gender": "male"},
        imaging_type="xray",
    )
    assert isinstance(result, GenAIResult)
    assert isinstance(result.is_mock, bool)
    assert len(result.clinical_context) > 0
    assert len(result.explanation) > 0
    assert len(result.limitations) > 0


@pytest.mark.asyncio
async def test_ai_analysis_endpoint(client):
    """GET /analysis/{study_id} returns AI analysis without mixing doctor assessment."""
    mock_db = MagicMock()
    analysis_row = {
        "id": "analysis-001",
        "imaging_study_id": "study-001",
        "finding": "Test Finding",
        "location": "Lung",
        "confidence_score": 0.85,
        "model_name": "mock-vision-v0",
        "model_version": "0.0.1",
        "analysis_status": "completed",
    }
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = analysis_row
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [analysis_row]

    with patch("app.database._override_admin", mock_db):
        resp = await client.get("/analysis/study-001", headers=DOCTOR_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["finding"] == "Test Finding"
    # Ensure doctor assessment keys are not injected into AI analysis result
    assert "doctor_assessment" not in data
