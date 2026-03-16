from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from ..database import Base


# Связь Many-to-Many между пользователями и мастерскими
# Один пользователь может работать в нескольких мастерских
user_workshop_link = Table(
    "user_workshop_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("workshop_id", Integer, ForeignKey("workshops.id", ondelete="CASCADE"), primary_key=True),
    Column("role_in_workshop", String(50), nullable=True),  # Должность в конкретной мастерской
)


class Workshop(Base):
    """
    Мастерская (филиал сети) с адресом.

    Примеры: Москва — Центральная, Санкт-Петербург — Север.
    У мастерской есть адрес, телефон, и свои сотрудники.
    """

    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    address = Column(String(255), nullable=True)  # Улица, дом
    phone = Column(String(20), nullable=True)     # Телефон мастерской

    # Связь Many-to-Many с пользователями
    users = relationship("User", secondary=user_workshop_link, back_populates="workshops")
    
    # Заявки в этой мастерской
    orders = relationship("Order", back_populates="workshop")

