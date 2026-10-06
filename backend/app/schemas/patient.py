from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    date_of_birth: date
    gender: GenderEnum
    phone: str = Field(..., min_length=7, max_length=20)
    email: EmailStr
    address: Optional[str] = None


class PatientOut(BaseModel):
    id: str
    profile_id: Optional[str] = None
    mr_number: str
    full_name: str
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
