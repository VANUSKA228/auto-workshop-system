# backend/app/schemas/user.py
"""Pydantic-схемы для User и Role."""

from pydantic import BaseModel, EmailStr


class RoleRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: str | None = None
    email: EmailStr
    phone: str | None = None
    password: str
    role_id: int


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = None
    role_id: int | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str | None
    email: str
    phone: str | None
    role_id: int
    role: RoleRead | None = None
    is_active: bool
    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    id: int
    first_name: str
    last_name: str
    model_config = {"from_attributes": True}
