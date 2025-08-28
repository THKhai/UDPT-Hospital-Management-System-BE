from sqlalchemy import Column, Integer, String
from config import Base


class Patient(Base):
    __tablename__ = "patient"
    __table_args__ = {"schema": "users"}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)
