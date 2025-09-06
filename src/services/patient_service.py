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