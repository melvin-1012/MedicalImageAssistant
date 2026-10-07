"""
Tests for Multimodal AI (Person 4) module integration with FastAPI backend.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pytest
from app.services.genai_service import generate_clinical_report, GenAIResult
from genai_module.pipeline import GenAIPipeline


@pytest.mark.asyncio
async def test_genai_pipeline_offline_fallback():
    """Verify GenAIPipeline produces structured output in offline/demo mode."""
    pipeline = GenAIPipeline()
    vision_data = {
        "status": "success",
        "modality": "X-Ray",
        "findings": [
            {
                "finding": "opacity",
                "confidence": 0.85,
                "location": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
                "heatmap_available": True,
                "requires_physician_review": True,
            }
        ],
    }
    raw_notes = "Patient reports shortness of breath and fever."
    result = pipeline.run_analysis(vision_data=vision_data, raw_notes=raw_notes)

    assert result is not None
    assert "summary" in result
    assert "findings" in result
    assert len(result["findings"]) == 1
    assert result["findings"][0]["finding"] == "opacity"
    assert result["findings"][0]["confidence"] == 0.85
    assert "limitations" in result
    assert result["validation_status"]["is_valid"] is True


@pytest.mark.asyncio
async def test_genai_pipeline_poor_quality_fast_fail():
    """Verify GenAIPipeline aborts analysis gracefully if image quality is poor."""
    pipeline = GenAIPipeline()
    vision_data = {
        "status": "poor_quality",
        "modality": "CT Scan",
        "findings": [],
    }
    result = pipeline.run_analysis(vision_data=vision_data, raw_notes="Patient routine checkup")
    assert "aborted" in result["summary"].lower()
    assert len(result["findings"]) == 0


@pytest.mark.asyncio
async def test_genai_service_integration():
    """Verify backend genai_service delegates to GenAIPipeline."""
    result: GenAIResult = await generate_clinical_report(
        vision_finding="mild consolidation",
        vision_location="Left mid-zone",
        confidence_score=0.91,
        imaging_type="xray",
        patient_symptoms="cough, chest tightness",
        patient_age=52,
        patient_gender="female",
    )

    assert isinstance(result, GenAIResult)
    assert len(result.clinical_context) > 0
    assert len(result.explanation) > 0
    assert "mild consolidation" in result.explanation.lower()
    assert result.raw_output is not None
    assert "findings" in result.raw_output


@pytest.mark.asyncio
async def test_genai_router_endpoint(client):
    """Verify POST /genai/analyze endpoint mounted on FastAPI app."""
    payload = {
        "vision_data": {
            "status": "success",
            "modality": "MRI",
            "findings": [
                {
                    "finding": "normal_parenchyma",
                    "confidence": 0.95,
                }
            ],
        },
        "raw_notes": "Mild headaches for 3 days",
    }
    resp = await client.post("/genai/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "findings" in data
    assert len(data["findings"]) == 1
    assert data["findings"][0]["finding"] == "normal_parenchyma"
