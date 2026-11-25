import base64
import json
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth",
    tokenUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
    auto_error=False,
)


def decode_jwt_payload(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        data = base64.urlsafe_b64decode(padded)
        return json.loads(data)
    except Exception:
        return {}


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    x_user_email: Annotated[str | None, Header(alias="X-User-Email")] = None,
) -> User:
    if token:
        payload = decode_jwt_payload(token)
        email = payload.get("email") or payload.get("preferred_username")
        if email:
            stmt = select(User).where(User.email == email)
            user = db.scalar(stmt)

            roles = payload.get("realm_access", {}).get("roles", [])
            role = "student"
            if "admin" in roles:
                role = "admin"
            elif "teacher" in roles:
                role = "teacher"

            if user is None:
                username = payload.get("preferred_username") or email.split("@")[0]
                user = User(username=username, email=email, role=role)
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                if user.role != role and role != "student":
                    user.role = role
                    db.commit()
                    db.refresh(user)
            return user

    email = x_user_email or settings.demo_user_email
    stmt = select(User).where(User.email == email)
    user = db.scalar(stmt)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with email '{email}' not found or not authenticated",
        )
    return user


def require_role(*roles: str) -> Callable[[User], User]:
    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: required role in {roles}",
            )
        return current_user

    return role_checker
