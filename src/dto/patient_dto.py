from typing import Optional
from pydantic import BaseModel, EmailStr


class PatientUpdateDTO(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
