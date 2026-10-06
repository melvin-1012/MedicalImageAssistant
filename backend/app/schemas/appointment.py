from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class AppointmentCreate(BaseModel):
    patient_id: Optional[str] = None  # filled from auth token server-side
    doctor_id: Optional[str] = None
    full_name: str = Field(..., min_length=2)
    mr_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: str
    email: Optional[str] = None
    symptoms: str = Field(..., min_length=3)
    department: Optional[str] = None
    preferred_doctor: Optional[str] = None
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    id: str
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    full_name: Optional[str] = None
    mr_number: Optional[str] = None
    symptoms: Optional[str] = None
    department: Optional[str] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus
