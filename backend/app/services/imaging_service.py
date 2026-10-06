"""
Imaging Service

Orchestrates the full imaging analysis pipeline:
  Image upload complete
    → Vision AI analysis
    → GenAI clinical explanation
    → Store ai_analysis_results
    → Generate PDF report
    → Update imaging_requests status
"""

import logging
from datetime import datetime
from app.database import get_supabase_admin
from app.services.vision_service import analyze_image, VisionResult
from app.services.genai_service import generate_clinical_context, GenAIResult
from app.services.report_service import generate_report

logger = logging.getLogger(__name__)


async def run_analysis_pipeline(study_id: str) -> dict:
    """
    Full analysis pipeline for a given imaging study.

    Steps:
    1. Fetch imaging study from DB
    2. Fetch patient context
    3. Run Vision AI → VisionResult
    4. Run GenAI → GenAIResult
    5. Store ai_analysis_results
    6. Generate PDF report
    7. Update imaging_request status → report_generated

    Returns: dict with analysis_id and report_id
    """
    db = get_supabase_admin()

    # 1. Fetch study
    study_resp = db.table("imaging_studies").select(
        "*, imaging_requests(patient_id, symptoms, reason, imaging_type)"
    ).eq("id", study_id).single().execute()

    if not study_resp.data:
        raise ValueError(f"Imaging study not found: {study_id}")

    study = study_resp.data
    imaging_type = study.get("imaging_type", "xray")
    storage_path = study.get("storage_path", "")
    request_data = study.get("imaging_requests") or {}
    patient_id = study.get("patient_id") or request_data.get("patient_id")

    # 2. Fetch patient context
    patient_context = {}
    if patient_id:
        p_resp = db.table("patients").select(
            "full_name, age, gender, mr_number, blood_group, allergies"
        ).eq("id", patient_id).single().execute()
        if p_resp.data:
            patient_context = p_resp.data
            patient_context["symptoms"] = request_data.get("symptoms", "")
            patient_context["reason"] = request_data.get("reason", "")

    # 3. Update status → analysis_pending
    request_id = study.get("imaging_request_id")
    if request_id:
        db.table("imaging_requests").update(
            {"status": "analysis_pending"}
        ).eq("id", request_id).execute()

    # 4. Run Vision AI
    logger.info(f"[ImagingService] Running Vision AI for study {study_id}")
    vision_result: VisionResult = await analyze_image(
        image_path=storage_path,
        imaging_type=imaging_type,
        patient_context=patient_context,
    )

    # 5. Run GenAI
    logger.info(f"[ImagingService] Running GenAI for study {study_id}")
    genai_result: GenAIResult = await generate_clinical_context(
        vision_result=vision_result,
        patient_context=patient_context,
        imaging_type=imaging_type,
    )

    # 6. Store ai_analysis_results
    analysis_data = {
        "imaging_study_id": study_id,
        "finding": vision_result.finding,
        "location": vision_result.location,
        "confidence_score": vision_result.confidence_score,
        "heatmap_storage_path": vision_result.heatmap_storage_path,
        "clinical_context": genai_result.clinical_context,
        "explanation": genai_result.explanation,
        "limitations": genai_result.limitations,
        "model_name": vision_result.model_name,
        "model_version": vision_result.model_version,
        "analysis_status": "completed",
    }

    # Check if analysis already exists (idempotent)
    existing = db.table("ai_analysis_results").select("id").eq(
        "imaging_study_id", study_id
    ).execute()

    if existing.data:
        analysis_resp = db.table("ai_analysis_results").update(
            {**analysis_data, "updated_at": datetime.utcnow().isoformat()}
        ).eq("imaging_study_id", study_id).execute()
    else:
        analysis_resp = db.table("ai_analysis_results").insert(analysis_data).execute()

    analysis_id = analysis_resp.data[0]["id"] if analysis_resp.data else None
    logger.info(f"[ImagingService] Stored analysis: {analysis_id}")

    # Update imaging_study analysis_status
    db.table("imaging_studies").update(
        {"analysis_status": "completed"}
    ).eq("id", study_id).execute()

    # Update imaging_request status → analyzed
    if request_id:
        db.table("imaging_requests").update(
            {"status": "analyzed"}
        ).eq("id", request_id).execute()

    # 7. Generate PDF report
    report_id = await generate_report(study_id=study_id, analysis_id=analysis_id)
    logger.info(f"[ImagingService] Generated report: {report_id}")

    return {"analysis_id": analysis_id, "report_id": report_id}
