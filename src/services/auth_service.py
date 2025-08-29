from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from passlib.exc import InvalidTokenError

from src.auth.security import create_access_token
from fastapi import HTTPException, Depends
from starlette import status
from src.models.auth import Auth
from src.repositories.auth_repository import AuthRepository
from config.settings import settings
from src.dto.auth_dto import TokenResponseDTO,UserCreateDTO,UserRole
from src.auth.security import hash_password
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token",scheme_name="jwt")

class AuthService:
    def __init__(self, auth_repository:AuthRepository):
        self.auth_repository = auth_repository
        self.SECRET_KEY = settings.jwt.secret_key
        self.ALGORITHM = settings.jwt.algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.jwt_expire_minutes

    async def get_user(self, user_name: str):
        """Lấy thông tin người dùng theo tên đăng nhập"""
        try:
            user =  self.auth_repository.get_user_by_username(user_name)
            if not user:
                return None
        except Exception as e:
            print(f"Error fetching user in Auth service: {e}")
            return None
        return user
    async def create_user(self, user: UserCreateDTO):
        new_user = Auth(
            username=user.username,
            password=hash_password(user.password),
            role=user.role
        )
        return self.auth_repository.create_user(new_user)
    async def authenticate_user(self, user_name: str, password: str):
        """Xác thực người dùng với tên đăng nhập và mật khẩu"""
        try:
            user = await self.get_user(user_name)
            if not user or not user.verify_password(password):
                return None
        except Exception as e:
            print(f"Error authenticating user in Auth service: {e}")
            return None
        return user

    async def get_current_user(self,token: Annotated [str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception
        user = await self.get_user(username)
        if user is None:
            raise credentials_exception
        return user

    async def require_roles(self, allowed_roles: list[UserRole]):
        """Decorator to require specific roles"""
        def role_checker(current_user: Auth = Depends(self.get_current_user)):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user

        return role_checker

    async def authenticate_and_create_user(self, username: str, password: str):
        user = await self.authenticate_user(username,password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return TokenResponseDTO(access_token=access_token, token_type="bearer")