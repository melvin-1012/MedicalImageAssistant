from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, get_current_user_id, require_doctor, require_patient
from app.database import get_supabase_admin
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from datetime import date

router = APIRouter()


@router.post("")
@router.post("/")
async def create_appointment(body: AppointmentCreate, user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """Book an appointment. Can be created by patient or doctor."""
    db = get_supabase_admin()

    # Validate appointment date is in the future
    if body.appointment_date < date.today():
        raise HTTPException(status_code=400, detail="Appointment date must be in the future")

    # Resolve patient_id from profile if not provided
    patient_id = body.patient_id
    role = (user.get("user_metadata") or {}).get("role", "patient")
    if role == "patient" and not patient_id:
        p = db.table("patients").select("id, mr_number").eq("profile_id", user_id).single().execute()
        if p.data:
            patient_id = p.data["id"]

    # Resolve doctor_id from name if provided
    doctor_id = body.doctor_id
    if not doctor_id and body.preferred_doctor:
        d = db.table("doctors").select("id").ilike("doctor_name", f"%{body.preferred_doctor}%").limit(1).execute()
        if d.data:
            doctor_id = d.data[0]["id"]

    data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "full_name": body.full_name,
        "mr_number": body.mr_number,
        "symptoms": body.symptoms,
        "department": body.department,
        "preferred_doctor": body.preferred_doctor,
        "appointment_date": body.appointment_date.isoformat(),
        "appointment_time": str(body.appointment_time),
        "notes": body.notes,
        "phone": body.phone,
        "email": body.email,
        "gender": body.gender,
        "status": "pending",
    }
    resp = db.table("appointments").insert(data).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create appointment")
    return resp.data[0]


@router.get("")
@router.get("/")
async def list_appointments(user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    role = (user.get("user_metadata") or {}).get("role", "patient")

    if role == "patient":
        # Get own patient profile
        p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
        if not p.data:
            return []
        resp = db.table("appointments").select("*").eq("patient_id", p.data["id"]).order("appointment_date", desc=True).execute()
    elif role == "doctor":
        d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
        if not d.data:
            return []
        resp = db.table("appointments").select("*").eq("doctor_id", d.data["id"]).order("appointment_date", desc=True).execute()
    else:
        resp = db.table("appointments").select("*").order("appointment_date", desc=True).execute()

    return resp.data or []


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str, user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("appointments").select("*").eq("id", appointment_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return resp.data


@router.patch("/{appointment_id}")
async def update_appointment_status(appointment_id: str, body: AppointmentUpdate, user: dict = Depends(get_current_user)):
    role = (user.get("user_metadata") or {}).get("role")
    if role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only doctors/admins can update appointment status")
    db = get_supabase_admin()
    resp = db.table("appointments").update({"status": body.status.value}).eq("id", appointment_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return resp.data[0]
