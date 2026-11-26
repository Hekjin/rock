from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import UserLoginRequest, UserRead, UserRegisterRequest
from app.services.auth_service import (
    AuthService,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    data: UserRegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserRead:
    try:
        return service.register_user(data)
    except EmailAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err


@router.post("/login", response_model=UserRead, status_code=status.HTTP_200_OK)
def login(
    data: UserLoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserRead:
    try:
        return service.login_user(data)
    except InvalidCredentialsError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
        ) from err
