import hashlib
import hmac
import secrets


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
