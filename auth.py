"""JWT Authentication and Password Hashing"""

from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import json
import os

SECRET_KEY = os.getenv("SECRET_KEY", "blostem-fd-optimizer-secret-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """Simple SHA-256 hash (in production use bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def create_token(payload: dict) -> str:
    """Create a simple JWT token"""
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload_copy = {**payload, "exp": exp.isoformat()}
    body = _b64encode(json.dumps(payload_copy).encode())
    message = f"{header}.{body}"
    sig = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    return f"{message}.{_b64encode(sig)}"


def verify_token(token: str) -> dict | None:
    """Verify and decode JWT token"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, body, sig = parts
        message = f"{header}.{body}"
        expected_sig = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64encode(expected_sig), sig):
            return None
        payload = json.loads(_b64decode(body))
        if datetime.fromisoformat(payload["exp"]) < datetime.utcnow():
            return None
        return payload
    except Exception:
        return None
