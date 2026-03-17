from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
import bcrypt
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models.user import User, Role
from ..models.workshop import Workshop, user_workshop_link
from ..schemas.auth import LoginRequest, LoginResponse, ClientRegisterRequest
from ..schemas.user import UserCreate, UserRead
from ..dependencies import get_current_user, role_required

router = APIRouter()
BCRYPT_ROUNDS = 12
settings = get_settings()


def verify_password(plain: str, hashed: str) -> bool:
    h = hashed.encode("utf-8") if isinstance(hashed, str) else hashed
    return bcrypt.checkpw(plain.encode("utf-8"), h)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def create_access_token(user_id: int, role_name: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "user_id": user_id, "role": role_name, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь деактивирован")

    role_name = user.role.name if user.role else "client"
    token = create_access_token(user.id, role_name)
    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "name": f"{user.last_name} {user.first_name[0]}." + (f" {user.middle_name[0]}." if user.middle_name else ""),
            "role": role_name,
        },
    )


@router.post("/register", response_model=UserRead)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже занят")

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

    if data.workshop_ids:
        for wid in data.workshop_ids:
            ws = db.query(Workshop).filter(Workshop.id == wid).first()
            if not ws:
                raise HTTPException(400, f"Мастерская с id={wid} не найдена")
            db.execute(
                user_workshop_link.insert().values(
                    user_id=new_user.id,
                    workshop_id=wid,
                    role_in_workshop=None
                )
            )
        db.commit()

    return db.query(User).filter(User.id == new_user.id).first()


@router.post("/register/client", response_model=LoginResponse)
def register_client(
    data: ClientRegisterRequest,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже занят")

    client_role = db.query(Role).filter(Role.name == "client").first()
    if not client_role:
        raise HTTPException(status_code=500, detail="Роль client не найдена")

    workshop = db.query(Workshop).filter(Workshop.id == data.workshop_id).first()
    if not workshop:
        raise HTTPException(status_code=400, detail="Мастерская не найдена")

    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role_id=client_role.id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.execute(
        user_workshop_link.insert().values(
            user_id=new_user.id,
            workshop_id=workshop.id,
            role_in_workshop='client'
        )
    )
    db.commit()

    role_name = "client"
    token = create_access_token(new_user.id, role_name)
    display_name = f"{new_user.last_name} {new_user.first_name[0]}." + (
        f" {new_user.middle_name[0]}." if new_user.middle_name else ""
    )
    return LoginResponse(
        token=token,
        user={"id": new_user.id, "name": display_name, "role": role_name},
    )
