from sqlalchemy.orm import Session

from src.repositories.doctor_repository import DoctorRepository


class DoctorService:
    def __init__(self,db:Session):
        self.doctor = DoctorRepository(db)
    def get_doctor_by_user_id(self,user_id):
        """get doctor by the user id"""
        return self.doctor.get_by_user_id(user_id)