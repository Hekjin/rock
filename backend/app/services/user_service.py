from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


class UserNotFoundError(Exception):
    pass


class CannotChangeOwnRoleError(Exception):
    pass


class CannotDeleteSelfError(Exception):
    pass


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self) -> Sequence[User]:
        stmt = select(User).order_by(User.id)
        return self.db.scalars(stmt).all()

    def get_user(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def update_user(self, user_id: int, data: UserUpdate, current_user_id: int) -> User:
        user = self.get_user(user_id)
        if (
            user_id == current_user_id
            and data.role is not None
            and data.role != user.role
        ):
            raise CannotChangeOwnRoleError("Свою роль менять нельзя")

        if data.username is not None:
            user.username = data.username
        if data.role is not None:
            user.role = data.role

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int, current_user_id: int) -> None:
        if user_id == current_user_id:
            raise CannotDeleteSelfError("Удалить себя нельзя")

        user = self.get_user(user_id)
        self.db.delete(user)
        self.db.commit()
