import hashlib
import hmac
import secrets
from dataclasses import dataclass

import jwt  # noqa: E402

# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, key = hashed_password.split(":")
        new_key = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode(), salt.encode(), 100_000
        )
        return hmac.compare_digest(key, new_key.hex())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Keycloak JWT verifier  (3-раунд: токенді тексеру)
# ---------------------------------------------------------------------------

APP_ROLES = ("admin", "teacher", "student")


@dataclass
class Identity:
    keycloak_id: str
    email: str
    username: str
    role: str | None


class KeycloakVerifier:
    """Verifies RS256 Keycloak tokens using JWKS (fetched once, cached)."""

    def __init__(self, issuer: str, jwks_url: str, audience: str) -> None:
        self.issuer = issuer
        self.audience = audience
        self._jwks = jwt.PyJWKClient(jwks_url, cache_keys=True)

    def verify(self, token: str) -> dict:
        """Raise jwt.exceptions.* on any verification failure."""
        key = self._jwks.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            issuer=self.issuer,
            audience=self.audience,
            options={"require": ["exp", "iat", "iss", "sub", "aud"]},
        )


def identity_from_claims(claims: dict) -> Identity:
    """Extract the highest-priority role from realm_access.roles."""
    roles = set(claims.get("realm_access", {}).get("roles", []))
    role = next((r for r in APP_ROLES if r in roles), None)
    email = claims.get("email") or claims.get("preferred_username", "")
    username = claims.get("preferred_username") or email.split("@")[0]
    return Identity(
        keycloak_id=claims["sub"],
        email=email,
        username=username,
        role=role,
    )
