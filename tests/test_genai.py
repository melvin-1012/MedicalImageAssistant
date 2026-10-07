"""Pytest suite for the GenAI module functionality and grounding validators."""
import pytest
from genai_module.pipeline import GenAIPipeline
from genai_module.evidence_validator import EvidenceValidator
from genai_module.ai_response_schema import (
    GenAIInput,
    VisionModelOutput,
    VisionFinding,
    BoundingBox,
    ClinicalContext,
    AIAnalysisReport,
    ExplainedFinding,
)


@pytest.fixture
def genai_pipeline():
    return GenAIPipeline()


def test_genai_standard_analysis_offline(genai_pipeline):
    """Test standard analysis flow with valid findings and notes."""
    vision_data = {
        "status": "success",
        "modality": "X-Ray",
        "findings": [
            {
                "finding": "possible_abnormal_opacity",
                "confidence": 0.016742,
                "location": {"x1": 320.0, "y1": 240.0, "x2": 610.0, "y2": 520.0},
                "heatmap_available": True,
                "requires_physician_review": True,
            }
        ],
    }
    notes = "Patient presents with persistent cough for 2 weeks."
    result = genai_pipeline.run_analysis(vision_data=vision_data, raw_notes=notes)

    assert result["validation_status"]["is_valid"] is True
    assert len(result["findings"]) == 1
    finding = result["findings"][0]
    assert finding["finding"] == "possible_abnormal_opacity"
    assert finding["confidence"] == 0.016742
    assert finding["location"] == {"x1": 320.0, "y1": 240.0, "x2": 610.0, "y2": 520.0}
    assert "status" in finding
    assert finding["status"] == "review_required"


def test_genai_fast_fail_poor_quality(genai_pipeline):
    """Test that poor quality triggers fast-fail bypass without medical hallucinations."""
    bad_data = {
        "status": "poor_quality",
        "modality": "X-Ray",
        "findings": [],
    }
    result = genai_pipeline.run_analysis(bad_data, "Patient has chest pain")
    assert result["summary"] == "Image quality is insufficient for reliable AI analysis."
    assert result["findings"] == []
    assert any("insufficient quality" in lim.lower() for lim in result["limitations"])


def test_genai_negative_image_exact_phrasing(genai_pipeline):
    """Test that empty findings produce the exact required phrasing."""
    normal_data = {
        "status": "success",
        "modality": "X-Ray",
        "findings": [],
    }
    result = genai_pipeline.run_analysis(normal_data, "Routine annual physical.")
    assert result["summary"] == "No abnormal opacity was detected by the current computer-vision model. Routine physician review is recommended."
    assert result["findings"] == []


def test_evidence_validator_rejects_hallucinations():
    """Test that EvidenceValidator rejects fabricated findings not in vision output."""
    validator = EvidenceValidator()
    genai_input = GenAIInput(
        vision_output=VisionModelOutput(
            status="success",
            findings=[
                VisionFinding(
                    finding="possible_abnormal_opacity",
                    confidence=0.0165,
                    location=BoundingBox(x1=100.0, y1=100.0, x2=200.0, y2=200.0),
                )
            ],
        ),
        clinical_context=ClinicalContext(raw_notes="Patient cough"),
    )

    # Hallucinated report with 'pleural_effusion'
    bad_report = AIAnalysisReport(
        summary="Test",
        findings=[
            ExplainedFinding(
                finding="pleural_effusion",
                confidence=0.0165,
                location={"x1": 100.0, "y1": 100.0, "x2": 200.0, "y2": 200.0},
                explanation="Hallucinated finding",
                status="review_required",
            )
        ],
    )
    res = validator.validate(genai_input, bad_report)
    assert res["is_valid"] is False
    assert any("Hallucinated finding" in err for err in res["errors"])


def test_evidence_validator_rejects_altered_confidence():
    """Test that EvidenceValidator rejects any alteration of raw confidence score."""
    validator = EvidenceValidator()
    genai_input = GenAIInput(
        vision_output=VisionModelOutput(
            status="success",
            findings=[
                VisionFinding(
                    finding="possible_abnormal_opacity",
                    confidence=0.016789,
                    location=BoundingBox(x1=100.0, y1=100.0, x2=200.0, y2=200.0),
                )
            ],
        ),
        clinical_context=ClinicalContext(raw_notes="Patient cough"),
    )

    bad_report = AIAnalysisReport(
        summary="Test",
        findings=[
            ExplainedFinding(
                finding="possible_abnormal_opacity",
                confidence=0.02,  # Altered / rounded confidence!
                location={"x1": 100.0, "y1": 100.0, "x2": 200.0, "y2": 200.0},
                explanation="Altered confidence test",
                status="review_required",
            )
        ],
    )
    res = validator.validate(genai_input, bad_report)
    assert res["is_valid"] is False
    assert any("Altered confidence" in err for err in res["errors"])


def test_evidence_validator_rejects_altered_location():
    """Test that EvidenceValidator rejects altered bounding box coordinates."""
    validator = EvidenceValidator()
    genai_input = GenAIInput(
        vision_output=VisionModelOutput(
            status="success",
            findings=[
                VisionFinding(
                    finding="possible_abnormal_opacity",
                    confidence=0.0165,
                    location=BoundingBox(x1=100.0, y1=100.0, x2=200.0, y2=200.0),
                )
            ],
        ),
        clinical_context=ClinicalContext(raw_notes="Patient cough"),
    )

    bad_report = AIAnalysisReport(
        summary="Test",
        findings=[
            ExplainedFinding(
                finding="possible_abnormal_opacity",
                confidence=0.0165,
                location={"x1": 105.0, "y1": 100.0, "x2": 200.0, "y2": 200.0},  # Altered x1
                explanation="Altered location test",
                status="review_required",
            )
        ],
    )
    res = validator.validate(genai_input, bad_report)
    assert res["is_valid"] is False
    assert any("Altered location" in err for err in res["errors"])
