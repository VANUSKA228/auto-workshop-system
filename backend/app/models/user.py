# backend/app/models/user.py
"""
ORM-модели: Role и User.
Связь: User.role_id -> Role.id (Many-to-One).
Связь с мастерскими: Many-to-Many через user_workshop_link.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base
from .workshop import user_workshop_link


class Role(Base):
    """
    Роль пользователя: client | master | admin.
    ТЗ: roles — справочник ролей.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    # Обратная связь: все пользователи с этой ролью
    users = relationship("User", back_populates="role")


class User(Base):
    """
    Пользователь системы.

    Связи:
    - role_id -> Role (роль: клиент/мастер/админ)
    - workshops -> Workshop[] (Many-to-Many: пользователь в нескольких мастерских)
    - orders_as_client -> Order (заявки, где пользователь — клиент)
    - orders_as_master -> Order (заявки, где назначен мастером)

    # ==========================================================================
    # ЗОНА РАБОТЫ СЕМЁНА
    # ==========================================================================
    # СЕМЁН, ТУТ: Проверь уникальность email на уровне БД (UNIQUE constraint).
    # Добавь индекс idx_users_email для ускорения поиска при логине.
    # ==========================================================================
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    role = relationship("Role", back_populates="users")
    
    # Many-to-Many связь с мастерскими
    workshops = relationship("Workshop", secondary=user_workshop_link, back_populates="users")
    
    orders_as_client = relationship(
        "Order", back_populates="client", foreign_keys="Order.client_id"
    )
    orders_as_master = relationship(
        "Order", back_populates="master", foreign_keys="Order.master_id"
    )
