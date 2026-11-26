from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.auth import UserRead
from app.schemas.user import UserUpdate
from app.services.user_service import (
    CannotChangeOwnRoleError,
    CannotDeleteSelfError,
    UserNotFoundError,
    UserService,
)

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


AdminUser = Annotated[User, Depends(require_role("admin"))]


@router.get("", response_model=list[UserRead], status_code=status.HTTP_200_OK)
def list_users(
    _: AdminUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> list[UserRead]:
    return list(service.list_users())


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    _: AdminUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    try:
        return service.get_user(user_id)
    except UserNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from err


@router.patch("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: AdminUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    try:
        return service.update_user(
            user_id=user_id, data=data, current_user_id=current_user.id
        )
    except CannotChangeOwnRoleError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except UserNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from err


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: AdminUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> Response:
    try:
        service.delete_user(user_id=user_id, current_user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except CannotDeleteSelfError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except UserNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from err
