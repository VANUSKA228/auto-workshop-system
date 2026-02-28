# backend/app/routers/users.py
"""
Роутер пользователей. Только Admin.
CRUD: список, создание, редактирование, деактивация (is_active=False).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models.user import User, Role
from ..schemas.user import UserCreate, UserUpdate, UserRead
from ..routers.auth import get_password_hash
from ..dependencies import role_required

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
    role: str | None = None,
    workshop_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Список пользователей. Фильтр role=? для выбора мастеров (назначение в заявку)."""
    q = db.query(User).options(joinedload(User.role), joinedload(User.workshop))
    if role:
        role_obj = db.query(Role).filter(Role.name == role).first()
        if role_obj:
            q = q.filter(User.role_id == role_obj.id)
    if workshop_id is not None:
        q = q.filter(User.workshop_id == workshop_id)
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

    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(400, "Роль не найдена")
    # Для клиентов и мастеров мастерская обязательна, админ глобальный.
    if role.name in ("client", "master") and data.workshop_id is None:
        raise HTTPException(400, "Укажите мастерскую для клиента или мастера")

    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role_id=data.role_id,
        workshop_id=data.workshop_id,
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
    payload = data.model_dump(exclude_unset=True)
    # Проверяем смену роли/мастерской
    if "role_id" in payload or "workshop_id" in payload:
        role_id = payload.get("role_id", u.role_id)
        ws_id = payload.get("workshop_id", u.workshop_id)
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(400, "Роль не найдена")
        if role.name in ("client", "master") and ws_id is None:
            raise HTTPException(400, "Укажите мастерскую для клиента или мастера")

    for k, v in payload.items():
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
