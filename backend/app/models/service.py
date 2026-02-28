# backend/app/models/service.py
"""
ORM-модель: Service (услуги автосервиса).
Связь с Order — через промежуточную таблицу OrderService (many-to-many).
"""

from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from ..database import Base


class Service(Base):
    """
    Классификатор услуг: название и цена.
    ТЗ: services — справочник услуг.
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2))

    # Обратная связь через order_services (заявки, в которых эта услуга)
    orders = relationship(
        "OrderService",
        back_populates="service",
        cascade="all, delete-orphan",
    )
