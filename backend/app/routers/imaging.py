import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional
from app.dependencies import get_current_user, get_current_user_id, require_doctor, require_specialist
from app.database import get_supabase_admin
from app.schemas.imaging import ImagingRequestCreate
from app.services.storage_service import validate_medical_image, upload_medical_image
from app.services.analysis_service import run_analysis_pipeline

router = APIRouter()


# ── Imaging Requests ──────────────────────────────────────────────────────────

@router.post("/requests")
@router.post("")
@router.post("/")
async def create_imaging_request(body: ImagingRequestCreate, user_id: str = Depends(get_current_user_id), user: dict = Depends(require_doctor)):
    """Doctor creates an imaging request for a patient."""
    db = get_supabase_admin()

    # Resolve doctor record
    d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
    if not d.data:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    doctor_id = d.data["id"]

    # Get patient MR number
    p = db.table("patients").select("mr_number").eq("id", body.patient_id).single().execute()
    mr_number = p.data["mr_number"] if p.data else None

    data = {
        "patient_id": body.patient_id,
        "doctor_id": doctor_id,
        "mr_number": mr_number,
        "imaging_type": body.imaging_type.value,
        "reason": body.reason,
        "symptoms": body.symptoms,
        "notes": body.notes,
        "status": "requested",
        "requested_at": "now()",
    }
    resp = db.table("imaging_requests").insert(data).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create imaging request")
    return resp.data[0]


@router.get("/requests")
@router.get("")
@router.get("/")
async def list_imaging_requests(user_id: str = Depends(get_current_user_id), user: dict = Depends(get_current_user)):
    """List imaging requests. Role-filtered."""
    db = get_supabase_admin()
    role = (user.get("user_metadata") or {}).get("role", "patient")

    query = db.table("imaging_requests").select(
        "*, patients(full_name, mr_number, age, gender), doctors(doctor_name)"
    )

    if role == "doctor":
        d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
        if d.data:
            query = query.eq("doctor_id", d.data["id"])
    elif role in ("specialist", "imaging_staff"):
        # Specialists see all non-completed requests
        query = query.not_.eq("status", "completed")

    resp = query.order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/requests/{request_id}")
@router.get("/{request_id}")
async def get_imaging_request(request_id: str, user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("imaging_requests").select(
        "*, patients(full_name, mr_number, age, gender, date_of_birth), doctors(doctor_name, specialization)"
    ).eq("id", request_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Imaging request not found")
    return resp.data


@router.patch("/requests/{request_id}/assign")
@router.patch("/{request_id}/assign")
async def assign_specialist(request_id: str, user_id: str = Depends(get_current_user_id), user: dict = Depends(require_specialist)):
    """Specialist claims an imaging request."""
    db = get_supabase_admin()
    s = db.table("specialists").select("id").eq("profile_id", user_id).single().execute()
    spec_id = s.data["id"] if s.data else None
    resp = db.table("imaging_requests").update({
        "specialist_id": spec_id,
        "status": "assigned",
    }).eq("id", request_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Request not found")
    return resp.data[0]


@router.patch("/requests/{request_id}/status")
@router.patch("/{request_id}/status")
async def update_imaging_request_status(
    request_id: str,
    status_payload: dict,
    user: dict = Depends(get_current_user),
):
    """Update status of an imaging request."""
    db = get_supabase_admin()
    new_status = status_payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing 'status' in request body")
    valid_statuses = {
        "requested", "assigned", "image_uploaded",
        "analysis_pending", "analyzed", "report_generated",
        "doctor_review", "completed"
    }
    if new_status.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(sorted(valid_statuses))}")

    resp = db.table("imaging_requests").update({"status": new_status.lower()}).eq("id", request_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Imaging request not found")
    return resp.data[0]


# ── Image Upload ──────────────────────────────────────────────────────────────

@router.post("/requests/{request_id}/upload")
@router.post("/{request_id}/upload")
async def upload_imaging_study(
    request_id: str,
    background_tasks: BackgroundTasks,
    imaging_type: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    user: dict = Depends(get_current_user),
):
    """Specialist uploads a medical image for an imaging request."""
    db = get_supabase_admin()

    # Verify request exists
    req = db.table("imaging_requests").select("*").eq("id", request_id).single().execute()
    if not req.data:
        raise HTTPException(status_code=404, detail="Imaging request not found")

    # Verify imaging type matches request
    req_imaging_type = req.data.get("imaging_type", "")
    if imaging_type.lower() != req_imaging_type.lower():
        raise HTTPException(
            status_code=400,
            detail=f"Imaging type mismatch: request requires '{req_imaging_type}', got '{imaging_type}'"
        )

    # Read file
    file_bytes = await file.read()
    content_type = file.content_type or "image/jpeg"
    file_size = len(file_bytes)

    # Validate
    try:
        validate_medical_image(file.filename, content_type, file_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Upload to storage
    storage_path = await upload_medical_image(file_bytes, file.filename, content_type, request_id)

    # Save study metadata
    study_data = {
        "imaging_request_id": request_id,
        "patient_id": req.data.get("patient_id"),
        "imaging_type": imaging_type.lower(),
        "storage_path": storage_path,
        "original_filename": file.filename,
        "mime_type": content_type,
        "file_size": file_size,
        "uploaded_by": user_id,
        "analysis_status": "pending",
    }
    study_resp = db.table("imaging_studies").insert(study_data).execute()
    study = study_resp.data[0] if study_resp.data else {}
    study_id = study.get("id")

    # Update request status
    db.table("imaging_requests").update({"status": "image_uploaded"}).eq("id", request_id).execute()

    # Trigger analysis in background
    background_tasks.add_task(run_analysis_pipeline, study_id)

    return {
        "study_id": study_id,
        "storage_path": storage_path,
        "status": "uploaded",
        "message": "Image uploaded. Analysis has started in the background.",
    }


@router.get("/studies/{study_id}")
async def get_imaging_study(study_id: str, user: dict = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("imaging_studies").select(
        "*, ai_analysis_results(*), imaging_requests(imaging_type, reason, symptoms)"
    ).eq("id", study_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Study not found")
    return resp.data


@router.get("/studies/{study_id}/image-url")
async def get_image_url(study_id: str, user: dict = Depends(get_current_user)):
    """Get a signed download URL for the medical image."""
    from app.services.storage_service import get_signed_image_url
    db = get_supabase_admin()
    resp = db.table("imaging_studies").select("storage_path").eq("id", study_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Study not found")
    url = get_signed_image_url(resp.data["storage_path"])
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate signed URL")
    return {"url": url}
