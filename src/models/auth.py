from config import Base
from sqlalchemy import Column, Integer, String
from src.auth.security import verify_password as _verify_password

class Auth(Base):
    __tablename__ = "auth"
    __table_args__ = {"schema": "admin"}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    user_ref_id = Column(Integer, nullable=True)
    user_type = Column(String(50), nullable=True)
    last_login = Column(String(50), nullable=True)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)


    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a plain password against the stored hashed password.
        """
        return _verify_password(plain_password, self.password)



