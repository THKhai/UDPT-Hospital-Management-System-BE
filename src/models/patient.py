from sqlalchemy import Column, Integer, String
from config import Base


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "appointment_mgmt"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False)
    updated_at = Column(String(50), nullable=False)