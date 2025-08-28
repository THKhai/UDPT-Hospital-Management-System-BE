from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from src.dto.auth_dto import UserLoginDTO, UserCreateDTO,TokenResponseDTO
from src.services.auth_service import AuthService
from dependency_injector.wiring import inject,Provide
from src.core.container import Container
login_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@login_router.post("/register",
                response_model=UserCreateDTO,
                status_code=status.HTTP_201_CREATED,
                summary="Register new user",
                description="Create a new user account"
)
@inject
async def register(
        user_data: UserCreateDTO,
        auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    try:
        exist_user = await auth_service.get_user(user_data.username)
        if exist_user:
            raise HTTPException(status_code=400, detail="User already exists")
        else:
            new_user = await auth_service.create_user(user_data)
    except Exception as e:
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


