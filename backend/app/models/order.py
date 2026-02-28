# backend/app/models/order.py
"""
ORM-модели: Order и OrderService (связь заявка-услуга).
Order связан с User (client, master) и Service (через OrderService).
"""

from sqlalchemy import Column, Integer, String, Text, SmallInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Order(Base):
    """
    Заявка клиента на ремонт.
    
    Связи:
    - client_id -> User (кто создал заявку)
    - master_id -> User (назначенный мастер, может быть NULL)
    - order_services -> OrderService[] (услуги в заявке, many-to-many)
    - payments -> Payment[] (платежи по заявке; по ТЗ — один платёж-заглушка)
    
    Статусы (ТЗ): new | in_progress | in_repair | done
    
    # ==========================================================================
    # ЗОНА РАБОТЫ СЕМЁНА
    # ==========================================================================
    # СЕМЁН, ТУТ: Индексы уже частично заданы в миграциях (idx_orders_client, status, created).
    # Добавь составной индекс для фильтрации: (status, created_at DESC) — частые запросы списка.
    # Рассмотри индекс на master_id для отчёта "заявки мастера".
    # ForeignKey на master_id — ON DELETE SET NULL, т.к. при удалении мастера заявка остаётся.
    # ==========================================================================
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    master_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    # Работник-исполнитель (механик) для заявки.
    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"))
    # Мастерская, в которой обслуживается заявка.
    workshop_id = Column(Integer, ForeignKey("workshops.id", ondelete="RESTRICT"), nullable=True)
    car_brand = Column(String(100), nullable=False)
    car_model = Column(String(100), nullable=False)
    car_year = Column(SmallInteger, nullable=False)
    description = Column(Text)
    status = Column(String(30), nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи
    client = relationship("User", back_populates="orders_as_client", foreign_keys=[client_id])
    master = relationship("User", back_populates="orders_as_master", foreign_keys=[master_id])
    worker = relationship("Worker", back_populates="orders")
    workshop = relationship("Workshop")
    order_services = relationship(
        "OrderService",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")


class OrderService(Base):
    """
    Промежуточная таблица Order-Service (many-to-many).
    Одна заявка — много услуг, одна услуга — много заявок.
    
    # ==========================================================================
    # ЗОНА РАБОТЫ СЕМЁНА
    # ==========================================================================
    # СЕМЁН, ТУТ: PRIMARY KEY (order_id, service_id) уже обеспечивает уникальность пары.
    # ON DELETE CASCADE на order_id — при удалении заявки удаляются связи.
    # Добавь ForeignKey на service_id с ON DELETE RESTRICT — нельзя удалить услугу, если она в заявках.
    # ==========================================================================
    """
    __tablename__ = "order_services"

    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="RESTRICT"), primary_key=True)

    order = relationship("Order", back_populates="order_services")
    service = relationship("Service", back_populates="orders")
