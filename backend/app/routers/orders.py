# backend/app/routers/orders.py
"""
Роутер заявок. CRUD + фильтрация по статусу, дате, поиску.
Логика доступа: Client — только свои; Master/Admin — все.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from ..database import get_db
from ..models.user import User
from ..models.order import Order, OrderService
from ..schemas.order import OrderCreate, OrderUpdate, OrderRead
from ..dependencies import get_current_user, role_required

router = APIRouter()


@router.get("/", response_model=list[OrderRead])
def list_orders(
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Список заявок с фильтрами.
    
    Client: GET /orders/my вызывается отдельно (см. endpoint ниже).
    Master/Admin: видят все заявки.
    
    Фильтры (query-params):
    - status: new | in_progress | in_repair | done
    - search: по ФИО клиента или модели авто
    - date_from, date_to: диапазон дат
    - sort_by, sort_order: сортировка
    - limit, offset: пагинация (ТЗ: 50 строк на страницу)
    """
    role_name = user.role.name if user.role else None
    if role_name == "client":
        q = db.query(Order).filter(Order.client_id == user.id)
    else:
        q = db.query(Order)

    q = q.options(joinedload(Order.client), joinedload(Order.master), joinedload(Order.order_services).joinedload(OrderService.service))

    if status:
        q = q.filter(Order.status == status)
    if search:
        search_pattern = f"%{search}%"
        q = q.join(User, Order.client_id == User.id).filter(
            or_(
                User.last_name.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                Order.car_model.ilike(search_pattern),
            )
        )
    if date_from:
        q = q.filter(Order.created_at >= date_from)
    if date_to:
        q = q.filter(Order.created_at <= date_to)

    order_col = getattr(Order, sort_by, Order.created_at)
    if sort_order == "asc":
        q = q.order_by(order_col.asc())
    else:
        q = q.order_by(order_col.desc())

    orders = q.offset(offset).limit(limit).all()
    return orders


@router.get("/my", response_model=list[OrderRead])
def list_my_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Список заявок текущего клиента. Client вызывает этот endpoint."""
    q = db.query(Order).filter(Order.client_id == user.id)
    q = q.options(joinedload(Order.client), joinedload(Order.master), joinedload(Order.order_services).joinedload(OrderService.service))
    return q.order_by(Order.created_at.desc()).all()


@router.post("/", response_model=OrderRead)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Создание заявки.
    
    Функция create_order:
    - Принимает данные от клиента (car_brand, car_model, car_year, description, service_ids).
    - client_id берётся из JWT (текущий пользователь).
    - Создаёт Order со статусом 'new'.
    - Создаёт связи OrderService для каждой выбранной услуги.
    - Возвращает созданную заявку (order_id нужен для /payments/stub).
    """
    order = Order(
        client_id=user.id,
        car_brand=data.car_brand,
        car_model=data.car_model,
        car_year=data.car_year,
        description=data.description,
        status="new",
    )
    db.add(order)
    db.flush()
    for sid in data.service_ids:
        os_rel = OrderService(order_id=order.id, service_id=sid)
        db.add(os_rel)
    db.commit()
    db.refresh(order)
    order = db.query(Order).options(
        joinedload(Order.client), joinedload(Order.master),
        joinedload(Order.order_services).joinedload(OrderService.service),
    ).filter(Order.id == order.id).first()
    return order


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Детали заявки. Client — только свои заявки. Master/Admin — любые."""
    order = db.query(Order).options(
        joinedload(Order.client), joinedload(Order.master),
        joinedload(Order.order_services).joinedload(OrderService.service),
    ).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заявка не найдена")
    role_name = user.role.name if user.role else None
    if role_name == "client" and order.client_id != user.id:
        raise HTTPException(403, "Нет доступа")
    return order


@router.patch("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(role_required("master", "admin")),
):
    """
    Редактирование заявки. Только Master/Admin.
    Если назначен мастер (master_id) — статус автоматически in_repair.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заявка не найдена")
    if data.master_id is not None:
        order.master_id = data.master_id
        order.status = "in_repair"
    if data.description is not None:
        order.description = data.description
    if data.status is not None:
        order.status = data.status
    db.commit()
    db.refresh(order)
    order = db.query(Order).options(
        joinedload(Order.client), joinedload(Order.master),
        joinedload(Order.order_services).joinedload(OrderService.service),
    ).filter(Order.id == order_id).first()
    return order


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(role_required("master", "admin")),
):
    """Удаление заявки. Только Master/Admin. ТЗ: только статусы new/in_progress."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заявка не найдена")
    if order.status not in ("new", "in_progress"):
        raise HTTPException(400, "Нельзя удалить заявку в статусе in_repair или done")
    db.delete(order)
    db.commit()
    return {"message": "Заявка удалена"}
