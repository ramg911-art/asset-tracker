"""JWT token creation and validation."""
from datetime import datetime, timezone, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(sub: str | int) -> tuple[str, int]:
    """Create JWT access token. Returns (token, expires_in_seconds)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(sub), "exp": expire}
    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return token, settings.access_token_expire_minutes * 60


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate JWT. Returns payload or None."""
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError:
        return None
