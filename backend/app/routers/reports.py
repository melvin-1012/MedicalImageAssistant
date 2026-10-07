from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, get_current_user_id, require_doctor
from app.database import get_supabase_admin
from app.schemas.report import DoctorAssessmentCreate
from app.services.storage_service import get_signed_report_url
from app.services.report_service import generate_report
from datetime import datetime

router = APIRouter()


@router.get("/")
async def list_reports(user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """List reports. Role-filtered."""
    db = get_supabase_admin()
    role = (user.get("user_metadata") or {}).get("role", "patient")

    query = db.table("medical_reports").select(
        "*, patients(full_name, mr_number, age, gender), "
        "imaging_studies(imaging_type, original_filename), "
        "ai_analysis_results(finding, confidence_score, limitations, explanation, clinical_context, location, model_name), "
        "doctor_assessments(diagnosis, conclusion, medications, recommendations, follow_up_instructions, additional_notes, finalized_at)"
    ).order("created_at", desc=True)

    if role == "patient":
        p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
        if not p.data:
            return []
        query = query.eq("patient_id", p.data["id"]).eq("report_status", "available_to_patient")
    elif role == "doctor":
        # Doctors see all reports for their patients
        d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
        if d.data:
            # Get patient IDs from imaging requests
            req_resp = db.table("imaging_requests").select("patient_id").eq("doctor_id", d.data["id"]).execute()
            patient_ids = list({r["patient_id"] for r in (req_resp.data or []) if r.get("patient_id")})
            if patient_ids:
                query = query.in_("patient_id", patient_ids)

    resp = query.execute()
    return resp.data or []


@router.get("/search/{mr_number}")
async def search_report_by_mr(mr_number: str, user: dict = Depends(get_current_user)):
    """Search reports by MR Number."""
    db = get_supabase_admin()
    # Find patient
    p = db.table("patients").select("id").eq("mr_number", mr_number.upper()).single().execute()
    if not p.data:
        raise HTTPException(status_code=404, detail=f"No patient found with MR Number: {mr_number}")
    patient_id = p.data["id"]

    role = (user.get("user_metadata") or {}).get("role", "patient")
    query = db.table("medical_reports").select(
        "*, patients(full_name, mr_number, age, gender, date_of_birth), "
        "imaging_studies(imaging_type, original_filename, uploaded_at), "
        "ai_analysis_results(finding, confidence_score, limitations, explanation, clinical_context, location, model_name, model_version), "
        "doctor_assessments(diagnosis, conclusion, medications, recommendations, follow_up_instructions, additional_notes, finalized_at)"
    ).eq("patient_id", patient_id).order("created_at", desc=True)

    if role == "patient":
        query = query.eq("report_status", "available_to_patient")

    resp = query.execute()
    return resp.data or []


@router.get("/{report_id}")
async def get_report(report_id: str, user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("medical_reports").select(
        "*, patients(full_name, mr_number, age, gender, date_of_birth), "
        "imaging_studies(imaging_type, original_filename, uploaded_at, storage_path), "
        "ai_analysis_results(finding, confidence_score, limitations, explanation, clinical_context, location, model_name, model_version, heatmap_storage_path), "
        "doctor_assessments(diagnosis, conclusion, medications, recommendations, follow_up_instructions, additional_notes, finalized_at)"
    ).eq("id", report_id).single().execute()

    if not resp.data:
        raise HTTPException(status_code=404, detail="Report not found")

    report = resp.data
    # Patient auth check
    role = (user.get("user_metadata") or {}).get("role", "patient")
    if role == "patient":
        p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
        if not p.data or p.data["id"] != report.get("patient_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        if report.get("report_status") != "available_to_patient":
            raise HTTPException(status_code=403, detail="Report not yet available")

    return report


@router.get("/{report_id}/pdf-url")
async def get_pdf_url(report_id: str, user: dict = Depends(get_current_user)):
    """Get a signed URL to download the report PDF."""
    db = get_supabase_admin()
    resp = db.table("medical_reports").select("report_pdf_path, report_status, patient_id").eq("id", report_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Report not found")

    role = (user.get("user_metadata") or {}).get("role", "patient")
    if role == "patient" and resp.data.get("report_status") != "available_to_patient":
        raise HTTPException(status_code=403, detail="Report not yet finalized")

    url = get_signed_report_url(resp.data["report_pdf_path"])
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate PDF URL")
    return {"url": url}


@router.post("/{report_id}/assessment")
@router.patch("/{report_id}/assessment")
async def submit_doctor_assessment(
    report_id: str,
    body: DoctorAssessmentCreate,
    user_id: str = Depends(get_current_user_id),
    user: dict = Depends(require_doctor),
):
    """Doctor submits their final clinical assessment."""
    db = get_supabase_admin()

    d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
    if not d.data:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    doctor_id = d.data["id"]

    # Check report exists
    report = db.table("medical_reports").select("id").eq("id", report_id).single().execute()
    if not report.data:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check for existing assessment
    existing = db.table("doctor_assessments").select("id").eq("report_id", report_id).execute()
    assessment_data = {
        "report_id": report_id,
        "doctor_id": doctor_id,
        "conclusion": body.conclusion,
        "diagnosis": body.diagnosis,
        "medications": body.medications,
        "recommendations": body.recommendations,
        "follow_up_instructions": body.follow_up_instructions,
        "additional_notes": body.additional_notes,
    }
    if existing.data:
        resp = db.table("doctor_assessments").update(assessment_data).eq("report_id", report_id).execute()
    else:
        resp = db.table("doctor_assessments").insert(assessment_data).execute()

    # Update report to under_review
    db.table("medical_reports").update({
        "report_status": "under_review",
        "reviewed_by": doctor_id,
        "reviewed_at": datetime.utcnow().isoformat(),
    }).eq("id", report_id).execute()

    return resp.data[0] if resp.data else {}


@router.patch("/{report_id}/finalize")
@router.post("/{report_id}/finalize")
async def finalize_report(report_id: str, user_id: str = Depends(get_current_user_id), user: dict = Depends(require_doctor)):
    """Doctor finalizes the report — this makes it available to the patient."""
    db = get_supabase_admin()

    d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
    if not d.data:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    # Check assessment exists
    assessment = db.table("doctor_assessments").select("*").eq("report_id", report_id).single().execute()
    if not assessment.data:
        raise HTTPException(status_code=400, detail="Cannot finalize without a doctor assessment")

    now = datetime.utcnow().isoformat()

    # Stamp finalized_at on assessment
    db.table("doctor_assessments").update({"finalized_at": now}).eq("report_id", report_id).execute()

    # Update report status
    db.table("medical_reports").update({
        "report_status": "finalized",
        "finalized_at": now,
        "reviewed_by": d.data["id"],
    }).eq("id", report_id).execute()

    # Update imaging request
    report = db.table("medical_reports").select("imaging_study_id").eq("id", report_id).single().execute()
    if report.data:
        study = db.table("imaging_studies").select("imaging_request_id").eq("id", report.data["imaging_study_id"]).single().execute()
        if study.data:
            db.table("imaging_requests").update({"status": "completed", "completed_at": now}).eq("id", study.data["imaging_request_id"]).execute()

    # Create/update medical record
    rep_full = db.table("medical_reports").select("patient_id").eq("id", report_id).single().execute()
    if rep_full.data and assessment.data:
        db.table("medical_records").insert({
            "patient_id": rep_full.data["patient_id"],
            "report_id": report_id,
            "visit_date": now[:10],
            "diagnosis": assessment.data.get("diagnosis", ""),
            "summary": assessment.data.get("conclusion", ""),
        }).execute()

    return {"message": "Report finalized successfully", "report_id": report_id}


@router.patch("/{report_id}/send-to-patient")
async def send_report_to_patient(report_id: str, user: dict = Depends(require_doctor)):
    """Make the finalized report visible to the patient."""
    db = get_supabase_admin()
    report = db.table("medical_reports").select("report_status").eq("id", report_id).single().execute()
    if not report.data:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.data["report_status"] not in ("finalized", "available_to_patient"):
        raise HTTPException(status_code=400, detail="Report must be finalized before sending to patient")

    db.table("medical_reports").update({"report_status": "available_to_patient"}).eq("id", report_id).execute()
    return {"message": "Report sent to patient", "report_id": report_id}
