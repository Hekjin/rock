from collections.abc import Callable
from typing import Annotated

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import KeycloakVerifier, identity_from_claims
from app.models.user import User

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=(
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
        "/protocol/openid-connect/auth"
    ),
    tokenUrl=(
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
        "/protocol/openid-connect/token"
    ),
    auto_error=False,
)

# Singleton — JWKS keys fetched once and cached
_verifier = KeycloakVerifier(
    issuer=settings.keycloak_issuer,
    jwks_url=settings.keycloak_jwks_url,
    audience=settings.keycloak_audience,
)


def _user_from_identity(db: Session, identity) -> User:
    """Find or auto-create a local User row from a verified Keycloak identity."""
    stmt = select(User).where(User.email == identity.email)
    user = db.scalar(stmt)
    if user is None:
        user = User(
            username=identity.username,
            email=identity.email,
            role=identity.role or "student",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Promote role if Keycloak says higher role
        APP_PRIORITY = {"admin": 0, "teacher": 1, "student": 2}
        new_role = identity.role or "student"
        if APP_PRIORITY.get(new_role, 99) < APP_PRIORITY.get(user.role, 99):
            user.role = new_role
            db.commit()
            db.refresh(user)
    return user


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    x_user_email: Annotated[str | None, Header(alias="X-User-Email")] = None,
) -> User:
    # --- Keycloak JWT path (RS256, JWKS-verified) ---
    if token:
        try:
            claims = _verifier.verify(token)
            identity = identity_from_claims(claims)
            return _user_from_identity(db, identity)
        except pyjwt.exceptions.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    # --- Fallback: X-User-Email header or demo_user_email ---
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
