from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Worker(Base):
    """
    Работник (исполнитель) внутри мастерской.

    Отличается от пользователя:
    - Пользователь = роль в системе (клиент / мастер / админ).
    - Worker = конкретный сотрудник, которого мастер назначает на заявку.
    """

    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Заказы, на которые назначен работник
    orders = relationship("Order", back_populates="worker")

