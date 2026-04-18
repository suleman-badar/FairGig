from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=15)
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)
    city_zone: str | None = Field(default=None, max_length=50)
    worker_category: str | None = Field(default=None, max_length=50)
    role: Literal["worker", "verifier", "advocate", "admin"] = "worker"


class LoginRequest(BaseModel):
    phone: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    phone: str
    email: EmailStr | None = None
    full_name: str | None = None
    role: str
    city_zone: str | None = None
    worker_category: str | None = None
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class MeUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    city_zone: str | None = Field(default=None, max_length=50)
    worker_category: str | None = Field(default=None, max_length=50)
