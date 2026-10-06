from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ImagingType(str, Enum):
    xray = "xray"
    ct_scan = "ct_scan"
    mri = "mri"


class ImagingRequestStatus(str, Enum):
    requested = "requested"
    assigned = "assigned"
    image_uploaded = "image_uploaded"
    analysis_pending = "analysis_pending"
    analyzed = "analyzed"
    report_generated = "report_generated"
    doctor_review = "doctor_review"
    completed = "completed"


class ImagingRequestCreate(BaseModel):
    patient_id: str
    imaging_type: ImagingType
    reason: str = Field(..., min_length=3)
    symptoms: Optional[str] = None
    notes: Optional[str] = None


class ImagingRequestOut(BaseModel):
    id: str
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    specialist_id: Optional[str] = None
    mr_number: Optional[str] = None
    imaging_type: Optional[str] = None
    reason: Optional[str] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    requested_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    # Joined fields
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True


class ImagingStudyOut(BaseModel):
    id: str
    imaging_request_id: str
    patient_id: Optional[str] = None
    imaging_type: Optional[str] = None
    storage_path: Optional[str] = None
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
