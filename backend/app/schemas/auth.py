"""Auth-related schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    """Login request."""

    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """User registration."""

    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User in response."""

    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Payload stored in JWT."""

    sub: str  # user id as string
    exp: Optional[datetime] = None
