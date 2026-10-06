from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReportStatus(str, Enum):
    generated = "generated"
    under_review = "under_review"
    finalized = "finalized"
    available_to_patient = "available_to_patient"


class DoctorAssessmentCreate(BaseModel):
    conclusion: str = Field(..., min_length=5)
    diagnosis: str = Field(..., min_length=3)
    medications: Optional[str] = None
    recommendations: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    additional_notes: Optional[str] = None


class ReportOut(BaseModel):
    id: str
    patient_id: Optional[str] = None
    imaging_study_id: Optional[str] = None
    ai_analysis_id: Optional[str] = None
    report_pdf_path: Optional[str] = None
    report_status: Optional[str] = None
    generated_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    created_at: Optional[datetime] = None
    # Joined
    patient_name: Optional[str] = None
    mr_number: Optional[str] = None
    imaging_type: Optional[str] = None
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True


class DoctorAssessmentOut(BaseModel):
    id: str
    report_id: str
    doctor_id: Optional[str] = None
    conclusion: Optional[str] = None
    diagnosis: Optional[str] = None
    medications: Optional[str] = None
    recommendations: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    additional_notes: Optional[str] = None
    finalized_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIAnalysisOut(BaseModel):
    id: str
    imaging_study_id: str
    finding: Optional[str] = None
    location: Optional[str] = None
    confidence_score: Optional[float] = None
    clinical_context: Optional[str] = None
    explanation: Optional[str] = None
    limitations: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    analysis_status: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
