from pydantic import BaseModel, EmailStr
from enum import Enum


# User roles
class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    EMPLOYEE = "employee"
# Models
class UserCreateDTO(BaseModel):
    username: str
    password: str
    name: str
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE

    class Config:
        use_enum_values = True
class UserLoginDTO(BaseModel):
    username: str
    password: str

class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str