from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import require_doctor_or_admin, get_current_user
from app.database import get_supabase_admin

router = APIRouter()


@router.get("")
@router.get("/")
async def list_doctors(user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("doctors").select("*").execute()
    return resp.data or []


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str, user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("doctors").select("*").eq("id", doctor_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return resp.data


@router.get("/{doctor_id}/patients")
async def get_doctor_patients(doctor_id: str, user: dict = Depends(require_doctor_or_admin)):
    """Get all patients with imaging requests for this doctor."""
    db = get_supabase_admin()
    resp = db.table("imaging_requests").select(
        "patient_id, patients(id, mr_number, full_name, age, gender)"
    ).eq("doctor_id", doctor_id).execute()
    # Deduplicate by patient
    seen = set()
    patients = []
    for row in (resp.data or []):
        p = row.get("patients")
        if p and p.get("id") not in seen:
            seen.add(p["id"])
            patients.append(p)
    return patients
