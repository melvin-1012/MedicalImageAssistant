from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.dependencies import get_current_user, require_doctor_or_admin
from app.database import get_supabase_admin
from app.services.analysis_service import run_analysis_pipeline

router = APIRouter()


@router.post("/{study_id}")
async def trigger_analysis(
    study_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_doctor_or_admin),
):
    """Manually trigger analysis pipeline for a study (admin/doctor use)."""
    db = get_supabase_admin()
    study = db.table("imaging_studies").select("id").eq("id", study_id).single().execute()
    if not study.data:
        raise HTTPException(status_code=404, detail="Imaging study not found")

    background_tasks.add_task(run_analysis_pipeline, study_id)
    return {"message": "Analysis pipeline triggered", "study_id": study_id}


@router.get("/{study_id}/results")
async def get_analysis_results(study_id: str, user: dict = Depends(get_current_user)):
    """Get AI analysis results for a study."""
    db = get_supabase_admin()
    resp = db.table("ai_analysis_results").select("*").eq("imaging_study_id", study_id).order("created_at", desc=True).limit(1).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Analysis results not found yet")
    return resp.data[0]
