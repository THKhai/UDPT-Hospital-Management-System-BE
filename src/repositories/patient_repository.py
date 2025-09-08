from sqlalchemy.orm import Session
from src.models.patient import Patient

class PatientRepository:
    def __init__(self, db:Session):
        self.db = db
    def get_patient_by_id(self, patient_id):
        """get patient by the id"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    def update_patient(self, patient: Patient) -> Patient:
        """update patient"""
        self.db.commit()
        self.db.refresh(patient)
        return patient
    def create_patient(self, patient: Patient) -> Patient:
        """create a new patient"""
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    def get_patient_list(self):
        """get patient list"""
        return self.db.query(Patient).all()
    def get_patient_by_user_id(self, user_id):
        """get patient by the user id"""
        return self.db.query(Patient).filter(Patient.user_id == user_id).all()
    def get_email_by_id(self, patient_id):
        """get email by the id"""
        return self.db.query(Patient.email).filter(Patient.id == patient_id).first()
