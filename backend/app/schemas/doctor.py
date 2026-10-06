from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class DoctorOut(BaseModel):
    id: str
    profile_id: Optional[str] = None
    doctor_name: str
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DoctorCreate(BaseModel):
    doctor_name: str = Field(..., min_length=2)
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None


class SpecialistOut(BaseModel):
    id: str
    profile_id: Optional[str] = None
    specialist_name: str
    specialization: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SpecialistCreate(BaseModel):
    specialist_name: str = Field(..., min_length=2)
    specialization: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
