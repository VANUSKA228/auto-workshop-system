# backend/app/schemas/auth.py
"""Pydantic-схемы для авторизации."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict  # { id, name, role }
    token_type: str = "bearer"
