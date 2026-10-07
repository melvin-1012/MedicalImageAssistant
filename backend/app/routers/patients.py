from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, require_doctor_or_admin, get_current_user_id
from app.database import get_supabase_admin
from app.schemas.patient import PatientOut
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_patients(user: dict = Depends(require_doctor_or_admin)):
    """Doctors can list all patients."""
    db = get_supabase_admin()
    resp = db.table("patients").select("*").order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/me")
async def get_my_profile(user_id: str = Depends(get_current_user_id)):
    """Patient gets their own profile."""
    db = get_supabase_admin()
    resp = db.table("patients").select("*").eq("profile_id", user_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return resp.data


@router.get("/me/records")
async def get_my_records(user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """Patient gets their own medical records."""
    db = get_supabase_admin()
    p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
    if not p.data:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    patient_id = p.data["id"]
    resp = db.table("medical_records").select(
        "*, medical_reports(id, report_pdf_path, report_status)"
    ).eq("patient_id", patient_id).order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/me/reports")
async def get_my_reports(user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """Patient gets their own finalized reports."""
    db = get_supabase_admin()
    p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
    if not p.data:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    patient_id = p.data["id"]
    resp = db.table("medical_reports").select(
        "*, imaging_studies(imaging_type, original_filename), "
        "ai_analysis_results(finding, confidence_score, limitations), "
        "doctor_assessments(diagnosis, conclusion, medications, recommendations, follow_up_instructions)"
    ).eq("patient_id", patient_id).eq("report_status", "available_to_patient").order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/mr/{mr_number}")
async def get_patient_by_mr(mr_number: str, user: dict = Depends(get_current_user)):
    """Lookup a patient by MR Number."""
    db = get_supabase_admin()
    resp = db.table("patients").select("*").eq("mr_number", mr_number.upper()).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail=f"No patient found with MR Number: {mr_number}")
    return resp.data


@router.get("/{patient_id}")
async def get_patient(patient_id: str, user: dict = Depends(require_doctor_or_admin)):
    db = get_supabase_admin()
    resp = db.table("patients").select("*").eq("id", patient_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Patient not found")
    return resp.data


@router.get("/{patient_id}/records")
async def get_patient_records(patient_id: str, user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """Get medical records for a patient. Patients can only access their own."""
    db = get_supabase_admin()
    # Verify patient identity
    role = (user.get("user_metadata") or {}).get("role", "patient")
    if role == "patient":
        # Ensure the patient_id belongs to this user
        p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
        if not p.data or p.data["id"] != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")

    resp = db.table("medical_records").select(
        "*, medical_reports(id, report_pdf_path, report_status, imaging_type)"
    ).eq("patient_id", patient_id).order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/{patient_id}/reports")
async def get_patient_reports(patient_id: str, user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """Get finalized reports for a patient."""
    db = get_supabase_admin()
    role = (user.get("user_metadata") or {}).get("role", "patient")

    query = db.table("medical_reports").select(
        "*, imaging_studies(imaging_type, original_filename), "
        "ai_analysis_results(finding, confidence_score, limitations), "
        "doctor_assessments(diagnosis, conclusion, medications, recommendations, follow_up_instructions)"
    ).eq("patient_id", patient_id).order("created_at", desc=True)

    if role == "patient":
        query = query.eq("report_status", "available_to_patient")

    resp = query.execute()
    return resp.data or []
