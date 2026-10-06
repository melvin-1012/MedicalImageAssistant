from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class AnalysisTriggerRequest(BaseModel):
    """Request body to manually trigger analysis for a study."""
    force_rerun: bool = False


class VisionResultOut(BaseModel):
    """Structured output from the Vision AI layer."""
    finding: str
    location: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    heatmap_storage_path: Optional[str] = None
    model_name: str
    model_version: str
    is_mock: bool = True


class GenAIResultOut(BaseModel):
    """Structured output from the GenAI / multimodal layer."""
    clinical_context: str
    explanation: str
    limitations: str
    is_mock: bool = True


class AnalysisResultOut(BaseModel):
    """Full combined AI analysis result returned from the API."""
    id: str
    imaging_study_id: str
    finding: Optional[str] = None
    location: Optional[str] = None
    confidence_score: Optional[float] = None
    heatmap_storage_path: Optional[str] = None
    clinical_context: Optional[str] = None
    explanation: Optional[str] = None
    limitations: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    analysis_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisTriggerResponse(BaseModel):
    """Response when analysis is triggered."""
    study_id: str
    analysis_id: Optional[str] = None
    report_id: Optional[str] = None
    status: str
    message: str
