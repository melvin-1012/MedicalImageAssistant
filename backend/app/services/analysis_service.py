"""
Analysis Orchestration Service

Coordinates the full AI analysis pipeline:
  1. Call Vision AI (vision_service)
  2. Call GenAI (genai_service)
  3. Store results in ai_analysis_results table
  4. Trigger report generation (report_service)
"""

import logging
from typing import Optional
from app.database import get_supabase_admin
from app.services import vision_service, genai_service

logger = logging.getLogger(__name__)


async def run_analysis_pipeline(study_id: str) -> dict:
    """
    Full analysis pipeline for a given imaging study.

    Args:
        study_id: UUID of the imaging_studies row

    Returns:
        dict with 'analysis_id' and 'report_id' on success
    """
    db = get_supabase_admin()

    # 1. Fetch imaging study
    study_resp = db.table("imaging_studies").select(
        "*, imaging_requests(imaging_type, symptoms, reason, patient_id, doctor_id), "
        "patients:patients(full_name, age, gender)"
    ).eq("id", study_id).single().execute()

    if not study_resp.data:
        raise ValueError(f"Imaging study {study_id} not found")

    study = study_resp.data
    request = study.get("imaging_requests", {}) or {}
    imaging_type = study.get("imaging_type", request.get("imaging_type", "xray"))
    storage_path = study.get("storage_path", "")
    patient_id = study.get("patient_id") or request.get("patient_id")
    symptoms = request.get("symptoms", "")

    # Fetch patient info
    patient_resp = db.table("patients").select("*").eq("id", patient_id).single().execute()
    patient = patient_resp.data or {}

    # 2. Vision AI
    logger.info(f"[AnalysisService] Running Vision AI for study {study_id}")
    vision_result = await vision_service.analyze_image(
        image_path=storage_path,
        imaging_type=imaging_type,
        patient_context={"symptoms": symptoms},
    )

    # 3. GenAI
    logger.info(f"[AnalysisService] Running GenAI for study {study_id}")
    genai_result = await genai_service.generate_clinical_report(
        vision_finding=vision_result.finding,
        vision_location=vision_result.location,
        confidence_score=vision_result.confidence_score,
        imaging_type=imaging_type,
        patient_symptoms=symptoms,
        patient_age=patient.get("age"),
        patient_gender=patient.get("gender"),
    )

    # 4. Store analysis result
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
    analysis_resp = db.table("ai_analysis_results").insert(analysis_data).execute()
    analysis = analysis_resp.data[0] if analysis_resp.data else {}
    analysis_id = analysis.get("id")

    # 5. Update imaging request status → analyzed
    request_id = study.get("imaging_request_id")
    if request_id:
        db.table("imaging_requests").update({"status": "analyzed"}).eq("id", request_id).execute()

    # 6. Update imaging study status
    db.table("imaging_studies").update({"analysis_status": "completed"}).eq("id", study_id).execute()

    logger.info(f"[AnalysisService] Analysis complete. analysis_id={analysis_id}")

    # 7. Generate PDF report
    from app.services.report_service import generate_report
    report_id = await generate_report(
        patient=patient,
        study=study,
        analysis_id=analysis_id,
        analysis=analysis_data,
    )

    return {"analysis_id": analysis_id, "report_id": report_id}
