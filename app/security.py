import secrets
from datetime import datetime, timedelta

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SESSION_TTL_DAYS = 7


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def generate_session_token() -> str:
    return secrets.token_urlsafe(48)


def session_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=SESSION_TTL_DAYS)
