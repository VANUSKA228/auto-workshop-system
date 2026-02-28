# backend/app/routers/orders.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ..database import get_db
from ..models.user import User
from ..models.order import Order, OrderService
from ..models.worker import Worker
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
    role_name = user.role.name if user.role else None
    q = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master),
        joinedload(Order.order_services).joinedload(OrderService.service),
    )

    if role_name == "client":
        q = q.filter(Order.client_id == user.id)
    elif role_name == "master":
        # Мастер видит только заявки своей мастерской.
        q = q.filter(Order.workshop_id == user.workshop_id)

    if status:
        q = q.filter(Order.status == status)

    if search:
        search_pattern = f"%{search}%"
        # Используем subquery чтобы не конфликтовал с join client
        client_ids = db.query(User.id).filter(
            or_(
                User.last_name.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
            )
        ).subquery()
        q = q.filter(
            or_(
                Order.client_id.in_(client_ids),
                Order.car_model.ilike(search_pattern),
                Order.car_brand.ilike(search_pattern),
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

    return q.offset(offset).limit(limit).all()


@router.get("/my", response_model=list[OrderRead])
def list_my_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Order)
        .filter(Order.client_id == user.id)
        .options(
            joinedload(Order.client),
            joinedload(Order.master),
            joinedload(Order.order_services).joinedload(OrderService.service),
        )
        .order_by(Order.created_at.desc())
        .all()
    )


@router.post("/", response_model=OrderRead)
def create_order(data: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = Order(
        client_id=user.id,
        workshop_id=user.workshop_id,
        car_brand=data.car_brand,
        car_model=data.car_model,
        car_year=data.car_year,
        description=data.description,
        status="new",
    )
    db.add(order)
    db.flush()
    for sid in data.service_ids:
        db.add(OrderService(order_id=order.id, service_id=sid))
    db.commit()
    return db.query(Order).options(
        joinedload(Order.client), joinedload(Order.master),
        joinedload(Order.order_services).joinedload(OrderService.service),
    ).filter(Order.id == order.id).first()


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
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
    order_id: int, data: OrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(role_required("master", "admin")),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заявка не найдена")
    # Мастер может изменять только заявки своей мастерской.
    role_name = user.role.name if user.role else None
    if role_name == "master" and order.workshop_id != user.workshop_id:
        raise HTTPException(403, "Нет доступа к заявке другой мастерской")

    # Для мастера поле master_id не выбираем в UI — считаем,
    # что мастер один на мастерскую и просто проставляем его,
    # если ещё не задан.
    if role_name == "master" and order.master_id is None:
        order.master_id = user.id

    # Для администратора при наличии master_id всё ещё можно
    # назначить любого мастера (например, при правках через API).
    if role_name == "admin" and data.master_id is not None:
        order.master_id = data.master_id
        if order.status not in ("in_repair", "done"):
            order.status = "in_repair"

    if data.worker_id is not None:
        # проверяем, что работник принадлежит той же мастерской
        worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
        if not worker:
            raise HTTPException(400, "Работник не найден")
        if order.workshop_id and worker.workshop_id != order.workshop_id:
            raise HTTPException(400, "Нельзя назначить работника из другой мастерской")
        order.worker_id = data.worker_id
    if data.description is not None:
        order.description = data.description
    if data.status is not None:
        order.status = data.status
    if data.service_ids is not None:
        db.query(OrderService).filter(OrderService.order_id == order_id).delete()
        for sid in data.service_ids:
            db.add(OrderService(order_id=order_id, service_id=sid))
    db.commit()
    return (
        db.query(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.master),
            joinedload(Order.worker),
            joinedload(Order.order_services).joinedload(OrderService.service),
        )
        .filter(Order.id == order_id)
        .first()
    )


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(role_required("master", "admin")),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заявка не найдена")
    if user.role.name == "master" and order.workshop_id != user.workshop_id:
        raise HTTPException(403, "Нет доступа к заявке другой мастерской")
    if order.status not in ("new", "in_progress"):
        raise HTTPException(400, "Нельзя удалить заявку в статусе in_repair или done")
    db.delete(order)
    db.commit()
    return {"message": "Заявка удалена"}
