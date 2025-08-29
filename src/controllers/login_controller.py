from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated

from sqlalchemy.orm import Session

from config import get_db
from src.dto.auth_dto import UserLoginDTO, UserCreateDTO,TokenResponseDTO
from src.services.auth_service import AuthService
from dependency_injector.wiring import inject,Provide
from src.core.container import Container
from src.services.user_service import UserService

login_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency để get UserService instance"""
    return UserService(db)

@login_router.post("/register",
                status_code=status.HTTP_201_CREATED,
                summary="Register new user",
                description="Create a new user account"
)
@inject
async def register(
        user_data: UserCreateDTO,
        auth_service: AuthService = Depends(Provide[Container.auth_service]),
        user_service: UserService = Depends(get_user_service)
):
    try:
        # Check if username already exists in auth
        exist_user = await auth_service.get_user(user_data.username)
        if exist_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Create user profile (username, email, password) in user table first
        created_user = user_service.create_user(user_data)

        # Then create credentials in auth table
        new_user = await auth_service.create_user(user_data)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Best-effort cleanup if auth creation failed after user was created
        try:
            if 'created_user' in locals() and getattr(created_user, 'id', None) is not None:
                user_service.delete_user(created_user.id)
        except Exception:
            # Swallow cleanup errors to not hide original error
            pass
        raise HTTPException(status_code=500, detail="api register " + str(e))
    return new_user


@login_router.post("/token",
                  response_model=TokenResponseDTO,
                  status_code=status.HTTP_201_CREATED,
                  summary="Get access token",
                  description="Get JWT token")
@inject
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(Provide[Container.auth_service])
) -> TokenResponseDTO:
   return await auth_service.authenticate_and_create_user(form_data.username, form_data.password)

@login_router.post("/login",
                  response_model=TokenResponseDTO,
                  status_code=status.HTTP_201_CREATED,
                  summary="login the user",
                  description="Get JWT token")
@inject
async def login(
    user_data: UserLoginDTO,
    auth_service: AuthService = Depends(Provide[Container.auth_service])
) -> TokenResponseDTO:
   return await auth_service.authenticate_and_create_user(user_data.username, user_data.password)


