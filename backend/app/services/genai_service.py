"""
GenAI / Multimodal Service — Placeholder / Mock Implementation

This service generates clinical context, evidence-grounded explanations,
and uncertainty statements from Vision AI findings + patient context.

When the actual Multimodal / GenAI model is available, replace the mock
logic in `generate_clinical_report()` with real LLM/multimodal API calls.

Integration points:
- Connect Google Gemini, GPT-4V, Med-PaLM, or similar
- Pass vision findings + patient symptoms/history as context
- Return standardized `GenAIResult` objects
"""

from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class GenAIResult:
    """Standardized output from Multimodal / GenAI analysis."""
    clinical_context: str
    explanation: str
    limitations: str
    raw_output: Optional[dict] = None
    model_name: str = "mock-genai-v0"
    model_version: str = "0.0.1"
    is_mock: bool = True             # ← Always True until real model connected


async def generate_clinical_report(
    vision_finding: str,
    vision_location: str,
    confidence_score: float,
    imaging_type: str,
    patient_symptoms: Optional[str] = None,
    patient_history: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_gender: Optional[str] = None,
) -> GenAIResult:
    """
    Generate an evidence-grounded clinical explanation from vision findings.

    Args:
        vision_finding: Finding text from Vision AI
        vision_location: Anatomical location of finding
        confidence_score: Vision model confidence (0–1)
        imaging_type: 'xray', 'ct_scan', or 'mri'
        patient_symptoms: Patient's reported symptoms
        patient_history: Relevant medical history
        patient_age: Patient's age
        patient_gender: Patient's gender

    Returns:
        GenAIResult with clinical context, explanation, and limitations

    NOTE: This is a MOCK implementation.
    Replace the body with actual LLM/multimodal API calls.
    The return type (GenAIResult) must remain the same.
    """
    logger.info(f"[GenAIService] Generating clinical report for {imaging_type}")

    # ── Multimodal GenAI Pipeline Integration (Person 4) ────────────────────
    import os
    import sys
    from pathlib import Path

    _REPO_ROOT = Path(__file__).resolve().parents[3]
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

    try:
        from genai_module.pipeline import GenAIPipeline
        pipeline = GenAIPipeline()
        modality_map = {"xray": "X-Ray", "ct_scan": "CT Scan", "mri": "MRI"}
        modality = modality_map.get(imaging_type.lower(), imaging_type.upper())

        notes_parts = []
        if patient_age:
            notes_parts.append(f"Age: {patient_age}")
        if patient_gender:
            notes_parts.append(f"Gender: {patient_gender}")
        if patient_symptoms:
            notes_parts.append(f"Symptoms: {patient_symptoms}")
        if patient_history:
            notes_parts.append(f"History/Reason: {patient_history}")
        raw_notes = " | ".join(notes_parts) if notes_parts else "No specific clinical notes provided."

        vision_data = {
            "status": "success",
            "modality": modality,
            "findings": [
                {
                    "finding": vision_finding,
                    "confidence": max(0.0, min(1.0, float(confidence_score))),
                    "location": None,
                    "heatmap_available": True,
                    "requires_physician_review": True,
                }
            ],
        }

        analysis = pipeline.run_analysis(vision_data=vision_data, raw_notes=raw_notes)
        summary = analysis.get("summary", "AI image analysis completed.")
        findings = analysis.get("findings", [])
        limitations_list = analysis.get("limitations", [])

        explanations = []
        supporting = []
        for f in findings:
            if f.get("explanation"):
                explanations.append(f["explanation"])
            for s in f.get("supporting_notes", []):
                if s.get("text"):
                    supporting.append(s["text"])

        clinical_context = f"{summary} Context: {', '.join(supporting) if supporting else raw_notes}"
        explanation = " ".join(explanations) if explanations else f"Detected {vision_finding} in {vision_location} with {int(confidence_score * 100)}% confidence."
        limitations = " ".join(limitations_list) if limitations_list else "AI-generated decision support. Requires physician verification."
        is_mock = not bool(os.getenv("GROQ_API_KEY"))

        return GenAIResult(
            clinical_context=clinical_context,
            explanation=explanation,
            limitations=limitations,
            raw_output=analysis,
            model_name="multimodal-groq-gpt-oss" if not is_mock else "demo-multimodal-v1",
            model_version="1.0.0",
            is_mock=is_mock,
        )
    except Exception as e:
        logger.warning(f"[GenAIService] Multimodal pipeline fallback: {e}")
    # ─────────────────────────────────────────────────────────────────────────

    imaging_label = {"xray": "X-Ray", "ct_scan": "CT Scan", "mri": "MRI"}.get(imaging_type, imaging_type.upper())
    age_str = f"{patient_age}-year-old" if patient_age else "adult"
    gender_str = patient_gender or "patient"
    symptoms_str = patient_symptoms or "reported symptoms"

    clinical_context = (
        f"[DEMO DATA - Not a real medical diagnosis] "
        f"Clinical context: {age_str} {gender_str} presenting with {symptoms_str}. "
        f"{imaging_label} imaging was performed for diagnostic evaluation."
    )

    explanation = (
        f"[DEMO DATA - Not a real medical diagnosis] "
        f"The {imaging_label} demonstrates: {vision_finding}. "
        f"The identified region is: {vision_location}. "
        f"Confidence level: {confidence_score * 100:.0f}%. "
        f"This finding is consistent with the clinical presentation. "
        f"Correlation with clinical history and physical examination is recommended."
    )

    limitations = (
        "IMPORTANT DISCLAIMER: This report was generated by a DEMO AI system "
        "and does NOT constitute a medical diagnosis. This analysis is for demonstration "
        "purposes only. All findings must be reviewed and validated by a qualified "
        "radiologist or physician before any clinical decisions are made. "
        "The AI model used here is a placeholder and has NOT been clinically validated."
    )

    return GenAIResult(
        clinical_context=clinical_context,
        explanation=explanation,
        limitations=limitations,
        model_name="mock-genai-v0",
        model_version="0.0.1",
        is_mock=True,
    )


async def generate_clinical_context(
    vision_result,
    patient_context: Optional[dict] = None,
    imaging_type: str = "xray",
) -> GenAIResult:
    """
    Standard interface adapter for Person 4 (Multimodal AI / GenAI).
    Accepts vision_result and patient_context dict.
    """
    patient_context = patient_context or {}
    return await generate_clinical_report(
        vision_finding=getattr(vision_result, "finding", str(vision_result)),
        vision_location=getattr(vision_result, "location", "Anatomical region"),
        confidence_score=getattr(vision_result, "confidence_score", 0.8),
        imaging_type=imaging_type,
        patient_symptoms=patient_context.get("symptoms"),
        patient_history=patient_context.get("reason"),
        patient_age=patient_context.get("age"),
        patient_gender=patient_context.get("gender"),
    )
