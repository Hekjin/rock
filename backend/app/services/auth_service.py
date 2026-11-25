from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserLoginRequest, UserRegisterRequest


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register_user(self, data: UserRegisterRequest) -> User:
        existing = self.db.scalar(
            select(User).where(
                or_(User.email == data.email, User.username == data.username)
            )
        )
        if existing:
            raise EmailAlreadyExistsError("Бұл email немесе username тіркелген")

        hashed = hash_password(data.password)
        user = User(
            username=data.username,
            email=data.email,
            role=data.role,
            hashed_password=hashed,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login_user(self, data: UserLoginRequest) -> User:
        user = self.db.scalar(select(User).where(User.email == data.email))
        if not user or not user.hashed_password:
            raise InvalidCredentialsError("Email немесе құпиясөз қате")

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError("Email немесе құпиясөз қате")

        return user
