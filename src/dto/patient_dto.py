from typing import Optional
from pydantic import BaseModel, EmailStr


class PatientUpdateDTO(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientEmailResponseDTO(BaseModel):
    """Response DTO for patient email lookup"""
    patient_id: int
    name: str
    email: Optional[str] = None
    message: str

    class Config:
        from_attributes = True
