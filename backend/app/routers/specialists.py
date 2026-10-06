"""
Specialists Router

Provides endpoints for:
- Listing all specialists (doctors/admin)
- Getting a specific specialist (authenticated)
- Getting the current specialist's own profile
- Getting imaging requests assigned to current specialist
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_supabase_admin
from app.dependencies import (
    get_current_user,
    get_current_user_id,
    require_specialist,
    require_doctor_or_admin,
)

router = APIRouter()


@router.get("", summary="List all specialists")
@router.get("/", summary="List all specialists")
async def list_specialists(
    user: dict = Depends(require_doctor_or_admin),
):
    """
    Return all specialists.
    Role required: doctor or admin.
    """
    db = get_supabase_admin()
    resp = db.table("specialists").select("*").order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/me", summary="Current specialist's own profile")
async def get_my_specialist_profile(
    user_id: str = Depends(get_current_user_id),
    user: dict = Depends(require_specialist),
):
    """
    Return the specialist profile for the currently authenticated specialist.
    Role required: specialist.
    """
    db = get_supabase_admin()
    resp = db.table("specialists").select("*").eq("profile_id", user_id).single().execute()
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist profile not found for current user",
        )
    return resp.data


@router.get("/me/imaging-requests", summary="Imaging requests for current specialist")
async def get_my_imaging_requests(
    status_filter: str = None,
    user_id: str = Depends(get_current_user_id),
    user: dict = Depends(require_specialist),
):
    """
    Return imaging requests relevant to the current specialist:
    - Requests where specialist_id matches, OR
    - Requests with status 'requested' (available for any specialist to pick up)

    Optional query param: status_filter (e.g. 'requested', 'assigned', 'image_uploaded')
    Role required: specialist.
    """
    db = get_supabase_admin()

    # Resolve specialist row id
    s_resp = db.table("specialists").select("id").eq("profile_id", user_id).single().execute()
    specialist_db_id = s_resp.data["id"] if s_resp.data else None

    # Base query with patient join
    query = db.table("imaging_requests").select(
        "*, patients(full_name, mr_number, age, gender), "
        "doctors(doctor_name, specialization)"
    ).order("created_at", desc=True)

    if status_filter:
        query = query.eq("status", status_filter.lower())

    resp = query.execute()
    all_requests = resp.data or []

    # Filter: own requests OR unassigned 'requested' status
    filtered = [
        r for r in all_requests
        if r.get("specialist_id") == specialist_db_id
        or r.get("status") == "requested"
    ]

    return filtered


@router.get("/{specialist_id}", summary="Get specialist by ID")
async def get_specialist(
    specialist_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Return a specific specialist by their DB id.
    Role required: any authenticated user.
    """
    db = get_supabase_admin()
    resp = db.table("specialists").select("*").eq("id", specialist_id).single().execute()
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialist not found: {specialist_id}",
        )
    return resp.data


@router.patch("/imaging-requests/{request_id}/assign", summary="Assign specialist to imaging request")
async def assign_to_imaging_request(
    request_id: str,
    user_id: str = Depends(get_current_user_id),
    user: dict = Depends(require_specialist),
):
    """
    Specialist self-assigns to an imaging request.
    Updates status from 'requested' → 'assigned'.
    Role required: specialist.
    """
    db = get_supabase_admin()

    # Resolve specialist row id
    s_resp = db.table("specialists").select("id").eq("profile_id", user_id).single().execute()
    if not s_resp.data:
        raise HTTPException(status_code=404, detail="Specialist profile not found")
    specialist_db_id = s_resp.data["id"]

    # Check request exists and is still available
    req = db.table("imaging_requests").select("id, status").eq("id", request_id).single().execute()
    if not req.data:
        raise HTTPException(status_code=404, detail="Imaging request not found")
    if req.data["status"] not in ("requested", "assigned"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot assign: request is already in status '{req.data['status']}'",
        )

    db.table("imaging_requests").update({
        "specialist_id": specialist_db_id,
        "status": "assigned",
    }).eq("id", request_id).execute()

    return {"message": "Imaging request assigned successfully", "request_id": request_id}
