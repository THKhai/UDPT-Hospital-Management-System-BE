from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from config import get_db
from src.dto.patient_dto import PatientUpdateDTO
from src.services.doctor_service import DoctorService
from src.services.patient_service import PatientService
patient_router = APIRouter(
    prefix="/patients",
    tags=["patients"]
)
from src.services.user_service import UserService

def get_user_service(db:Session = Depends(get_db)) -> UserService:
    return UserService(db)
def get_patient_service(db: Session = Depends(get_db)) -> PatientService :
    return PatientService(db)
def get_doctor_service(db: Session = Depends(get_db)) -> DoctorService:
    return DoctorService(db)
@patient_router.get("/patient_profile",
                    status_code=status.HTTP_200_OK,
                    summary="Get patient profile",
                    description="Retrieve patient profile")
def get_patient_profile(username: str,
                        patient_service: PatientService = Depends(get_patient_service),
                        user_service: UserService = Depends(get_user_service)
                        ):
    """
        Lấy thôn tin người bệnh nhân
    :param user_service:
    :param patient_service:
    :param username:
    :return:
    """
    user = user_service.get_user_by_username(username)
    if not user:
        return {"message": "User not found"}
    return patient_service.get_patient_by_user_id(user.id)

@patient_router.put("/patients_update",
                    status_code=status.HTTP_200_OK,
                    summary="Update patient profile",
                    description="Update patient profile")
def update_patient_profile(
    username: str,
    payload: PatientUpdateDTO,
    patient_service: PatientService = Depends(get_patient_service),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật thông tin bệnh nhân theo username:
    - Cho phép cập nhật: name, phone, email (truyền cái nào thì cập nhật cái đó).
    """
    user = user_service.get_user_by_username(username)
    if not user:
        return {"message": "User not found"}

    patients = patient_service.get_patient_by_user_id(user.id)
    if not patients:
        return {"message": "Patient profile not found for this user"}

    # Giả sử mỗi user chỉ có 1 hồ sơ bệnh nhân
    patient = patients[0]

    if payload.name is not None:
        patient.name = payload.name
    if payload.phone is not None:
        patient.phone = payload.phone
    if payload.email is not None:
        patient.email = payload.email
    updated = patient_service.update_patient(patient)
    return {
        "message": "Patient profile updated successfully",
        "data": {
            "id": updated.id,
            "name": updated.name,
            "phone": updated.phone,
            "email": updated.email,
            "user_id": updated.user_id,
            "updated_at": updated.updated_at,
        },
    }
@patient_router.get('/get_email',
            status_code=status.HTTP_200_OK,
            summary="Get user by email",
            description="Retrieve detailed information of a user by email"
            )
def get_email_by_id(
        patient_id:int,
        patient_service: PatientService = Depends(get_patient_service)
):
    return patient_service.get_patient_email(patient_id=patient_id)

@patient_router.get("/doctor_profile",
                   status_code=status.HTTP_200_OK,
                   summary="Get doctor profile",
                   description="Retrieve doctor profile")
def get_doctor_profile(username: str,
                       doctor_service: DoctorService = Depends(get_doctor_service),
                       user_service: UserService = Depends(get_user_service)
                       ):
    """
        Lấy thông tin bác sĩ
    :param user_service:
    :param doctor_service:
    :param username:
    :return:
    """
    user = user_service.get_user_by_username(username)
    if not user:
        return {"message": "User not found"}
    return doctor_service.get_doctor_by_user_id(user.id)
