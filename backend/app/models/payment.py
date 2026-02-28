# backend/app/models/payment.py
"""
ORM-модель: Payment (заглушка оплаты).
ТЗ: никакого реального платёжного шлюза. Статус stub_ok = "заявка зарегистрирована".
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Payment(Base):
    """
    Заглушка платежа. card_last4 — только для UI (последние 4 цифры).
    status: pending | stub_ok.
    
    Связь: order_id -> Order (уникальность: одна заявка — один платёж по ТЗ).
    
    # ==========================================================================
    # ЗОНА РАБОТЫ СЕМЁНА
    # ==========================================================================
    # СЕМЁН, ТУТ: order_id UNIQUE — одна заявка не может иметь два платежа.
    # Индекс на status для отчёта по платежам (если будет).
    # card_last4 — опционально, т.к. данные карты не сохраняются; можно оставить NULL.
    # ==========================================================================
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="RESTRICT"), unique=True)
    card_last4 = Column(String(4))
    amount = Column(Numeric(10, 2))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="payments")
