# backend/app/routers/auth.py
"""
Роутер авторизации: логин и регистрация.
POST /auth/login — принимает email+password, возвращает JWT и данные пользователя.
POST /auth/register — создание пользователя (только Admin).
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models.user import User
from ..schemas.auth import LoginRequest, LoginResponse
from ..schemas.user import UserCreate, UserRead
from ..dependencies import get_current_user, role_required

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
settings = get_settings()


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет пароль против bcrypt-хэша. ТЗ: cost factor 12."""
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    """Хэширует пароль через bcrypt. ТЗ: cost factor 12."""
    return pwd_context.hash(password)


def create_access_token(user_id: int, role_name: str) -> str:
    """
    Создаёт JWT access-токен.
    Payload: user_id, role (для проверки прав на фронте), exp (срок жизни 8 часов).
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "user_id": user_id, "role": role_name, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Вход в систему.
    
    Логика:
    1. Ищем пользователя по email.
    2. Проверяем пароль через bcrypt.
    3. Если is_active=False — отказ.
    4. Генерируем JWT, возвращаем token и краткие данные user для фронта.
    """
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
    """
    Регистрация нового пользователя. Только Admin.
    Admin создаёт мастеров и клиентов через этот эндпоинт.
    Пароль хэшируется перед сохранением в БД.
    """
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже занят")

    from ..models.user import User
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
