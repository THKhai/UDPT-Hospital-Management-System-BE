from fastapi import HTTPException
from starlette import status

from src.dto.patient_dto import PatientEmailResponseDTO
from src.repositories.patient_repository import PatientRepository
from src.models.patient import Patient
class PatientService:
    def __init__(self,db):
        self.patients = PatientRepository(db)
    def get_patient_by_id(self, patient_id):
        """get patient by the id"""
        return self.patients.get_patient_by_id(patient_id)
    def update_patient(self, patient):
        """update patient"""
        return self.patients.update_patient(patient)
    def create_patient(self, patient_data: Patient):
        """create a new patient"""
        return self.patients.create_patient(patient_data)
    def get_patient_list(self):
        """get patient list"""
        return self.patients.get_patient_list()
    def get_patient_by_user_id(self, user_id):
        """get patient by the user id"""
        return self.patients.get_patient_by_user_id(user_id)

    def get_patient_email(self, patient_id: int) -> PatientEmailResponseDTO:
        """Lấy email của patient theo ID"""
        # Kiểm tra patient có tồn tại không
        patient = self.patients.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id {patient_id} not found"
            )

        # Kiểm tra patient có email không
        if not patient.email:
            return PatientEmailResponseDTO(
                patient_id=patient.id,
                name=patient.name,
                email=None,
                message=f"Patient {patient.name} doesn't have email address"
            )

        return PatientEmailResponseDTO(
            patient_id=patient.id,
            name=patient.name,
            email=patient.email,
            message="Email found successfully"
        )