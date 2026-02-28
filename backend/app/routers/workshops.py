from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.workshop import Workshop
from ..schemas.workshop import WorkshopCreate, WorkshopUpdate, WorkshopRead
from ..dependencies import role_required


router = APIRouter()


@router.get("/", response_model=list[WorkshopRead])
def list_workshops(
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Список всех мастерских сети (для администратора)."""
    return db.query(Workshop).order_by(Workshop.city, Workshop.name).all()


@router.post("/", response_model=WorkshopRead)
def create_workshop(
    data: WorkshopCreate,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Создание новой мастерской (админ)."""
    ws = Workshop(name=data.name, city=data.city)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@router.patch("/{workshop_id}", response_model=WorkshopRead)
def update_workshop(
    workshop_id: int,
    data: WorkshopUpdate,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    ws = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not ws:
        raise HTTPException(404, "Мастерская не найдена")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(ws, k, v)
    db.commit()
    db.refresh(ws)
    return ws


@router.delete("/{workshop_id}")
def delete_workshop(
    workshop_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    ws = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not ws:
        raise HTTPException(404, "Мастерская не найдена")
    db.delete(ws)
    db.commit()
    return {"message": "Мастерская удалена"}

