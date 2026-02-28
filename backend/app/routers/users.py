# backend/app/routers/users.py
"""
Роутер пользователей. Только Admin.
CRUD: список, создание, редактирование, деактивация (is_active=False).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserRead
from ..routers.auth import get_password_hash
from ..dependencies import role_required

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
    role: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Список пользователей. Фильтр role=? для выбора мастеров (назначение в заявку)."""
    q = db.query(User)
    if role:
        from ..models.user import Role
        role_obj = db.query(Role).filter(Role.name == role).first()
        if role_obj:
            q = q.filter(User.role_id == role_obj.id)
    return q.all()


@router.post("/", response_model=UserRead)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Создание пользователя."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email уже занят")
    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role_id=data.role_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Редактирование пользователя."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "Пользователь не найден")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "password" and v:
            u.password_hash = get_password_hash(v)
        elif k != "password":
            setattr(u, k, v)
    db.commit()
    db.refresh(u)
    return u


@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Деактивация (is_active=False). ТЗ: не физическое удаление."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "Пользователь не найден")
    u.is_active = False
    db.commit()
    return {"message": "Пользователь деактивирован"}
