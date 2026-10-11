import os
import hashlib
import secrets
from typing import Tuple

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt (with salt cost factor 12).
    Falls back to salted PBKDF2-HMAC-SHA256 if bcrypt is unavailable.
    """
    if _HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    else:
        # Fallback PBKDF2
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return f"pbkdf2:sha256:100000${salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    Supports both bcrypt and PBKDF2 formats safely with constant-time comparison.
    """
    if not hashed_password or not plain_password:
        return False

    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$") or hashed_password.startswith("$2y$"):
        if _HAS_BCRYPT:
            try:
                return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
            except Exception:
                return False
        return False
    elif hashed_password.startswith("pbkdf2:"):
        try:
            parts = hashed_password.split("$")
            if len(parts) != 3:
                return False
            _, salt, key_hex = parts
            computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
            return secrets.compare_digest(computed.hex(), key_hex)
        except Exception:
            return False

    return False
