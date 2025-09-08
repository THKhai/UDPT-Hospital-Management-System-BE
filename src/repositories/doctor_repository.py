from typing import Optional

from sqlalchemy.orm import Session
from src.models.doctor import Doctors

class DoctorRepository:
    def __init__(self, db:Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[type[Doctors]]:
        """Lấy bác sĩ theo user_id"""
        return self.db.query(Doctors).filter(Doctors.user_id == user_id).first()
