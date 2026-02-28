# backend/app/schemas/order.py
"""Pydantic-схемы для Order."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .service import ServiceRead
from .user import UserBrief


class OrderServiceRead(BaseModel):
    service_id: int
    service: ServiceRead | None = None
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    """Данные для создания заявки. client_id берётся из токена для Client."""
    car_brand: str
    car_model: str
    car_year: int
    description: str | None = None
    service_ids: list[int]  # ID услуг из справочника


class OrderUpdate(BaseModel):
    master_id: int | None = None
    description: str | None = None
    status: str | None = None


class OrderRead(BaseModel):
    id: int
    client_id: int
    master_id: int | None
    car_brand: str
    car_model: str
    car_year: int
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    client: UserBrief | None = None
    master: UserBrief | None = None
    order_services: list[OrderServiceRead] = []
    model_config = {"from_attributes": True}
