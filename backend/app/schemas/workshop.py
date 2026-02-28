from pydantic import BaseModel


class WorkshopBase(BaseModel):
    name: str
    city: str


class WorkshopCreate(WorkshopBase):
    pass


class WorkshopUpdate(BaseModel):
    name: str | None = None
    city: str | None = None


class WorkshopRead(WorkshopBase):
    id: int
    model_config = {"from_attributes": True}

