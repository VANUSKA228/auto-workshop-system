from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Workshop(Base):
    """
    Мастерская (филиал сети).

    Примеры: Москва, Санкт-Петербург, Новосибирск.
    У мастерской есть свои сотрудники и клиенты.
    """

    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)

    # Пользователи, привязанные к этой мастерской (клиенты и мастера).
    users = relationship("User", back_populates="workshop")

