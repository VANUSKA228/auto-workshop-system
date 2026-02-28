from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from .service import ServiceRead
from .user import UserBrief
from .workshop import WorkshopRead
from .worker import WorkerRead


class OrderServiceRead(BaseModel):
    service_id: int
    service: ServiceRead | None = None
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    car_brand: str
    car_model: str
    car_year: int
    description: str | None = None
    service_ids: list[int]


class OrderUpdate(BaseModel):
    master_id: int | None = None
    worker_id: int | None = None
    description: str | None = None
    status: str | None = None
    service_ids: list[int] | None = None


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
    workshop_id: int | None = None
    workshop: WorkshopRead | None = None
    worker: WorkerRead | None = None
    client: UserBrief | None = None
    master: UserBrief | None = None
    order_services: list[OrderServiceRead] = []
    model_config = {"from_attributes": True}
