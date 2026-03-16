# backend/app/routers/orders.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, text

from ..database import get_db
from ..models.user import User
from ..models.order import Order, OrderService
from ..models.worker import Worker
from ..models.workshop import Workshop, user_workshop_link
from ..schemas.order import OrderCreate, OrderUpdate, OrderRead
from ..dependencies import get_current_user, role_required

router = APIRouter()


@router.get("/", response_model=list[OrderRead])
def list_orders(
    status: Optional[str] = None,
    workshop_id: Optional[int] = None,
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
    Список заявок с фильтрацией.
    
    - Client: видит только свои заявки
    - Master: видит заявки своих мастерских
    - Admin: видит все заявки
    
    Фильтры: status, workshop_id, search (по клиенту или авто), date_from, date_to
    """
    role_name = user.role.name if user.role else None
    q = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master),
        joinedload(Order.workshop),
        joinedload(Order.order_services).joinedload(OrderService.service),
    )

    if role_name == "client":
        q = q.filter(Order.client_id == user.id)
    elif role_name == "master":
        # Мастер видит только заявки своих мастерских
        workshop_ids = [w.id for w in user.workshops]
        q = q.filter(Order.workshop_id.in_(workshop_ids))
    # Admin видит все заявки

    # Дополнительные фильтры
    if status:
        q = q.filter(Order.status == status)
    if workshop_id is not None:
        q = q.filter(Order.workshop_id == workshop_id)

    if search:
        search_pattern = f"%{search}%"
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
    """Заявки текущего пользователя (для клиента)."""
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
    """
    Создание новой заявки.

    Клиент может выбрать любую мастерскую.
    Мастер создаёт заявку в своей мастерской.
    """
    role_name = user.role.name if user.role else None

    # Определяем workshop_id
    if role_name == "master":
        # Мастер создаёт заявку в своей мастерской
        from sqlalchemy import select
        stmt = select(user_workshop_link.c.workshop_id).where(user_workshop_link.c.user_id == user.id).limit(1)
        result = db.execute(stmt).scalar()
        if not result:
            raise HTTPException(400, "Мастер не привязан ни к одной мастерской")
        # Мастер может создавать только в своих мастерских
        workshop_id = result
        client_id = user.id
    else:
        # Клиент может выбрать любую мастерскую
        workshop_id = data.workshop_id
        if not workshop_id:
            # Если не указана, берём первую доступную
            first_workshop = db.query(Workshop).first()
            if not first_workshop:
                raise HTTPException(400, "Нет доступных мастерских")
            workshop_id = first_workshop.id
        client_id = user.id

    order = Order(
        client_id=client_id,
        workshop_id=workshop_id,
        car_brand=data.car_brand,
        car_model=data.car_model,
        car_year=data.car_year,
        description=data.description,
        status="new",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Добавляем услуги
    if data.service_ids and len(data.service_ids) > 0:
        for sid in data.service_ids:
            db.add(OrderService(order_id=order.id, service_id=sid))
        db.commit()
        db.refresh(order)

    # Загружаем связанные данные для ответа
    return db.query(Order).filter(Order.id == order.id).first()


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
    """Обновление заявки. Можно изменить все поля + данные клиента."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заявка не найдена")

    role_name = user.role.name if user.role else None

    # Мастер может изменять только заявки своих мастерских
    if role_name == "master":
        workshop_ids = [w.id for w in user.workshops]
        if order.workshop_id not in workshop_ids:
            raise HTTPException(403, "Нет доступа к заявке другой мастерской")
        # Если master_id не назначен, назначаем текущего мастера
        if order.master_id is None:
            order.master_id = user.id

    # Админ может назначить любого мастера
    if role_name == "admin" and data.master_id is not None:
        order.master_id = data.master_id
        # Если статус new и не указан новый статус, меняем на in_progress
        if order.status == "new" and (data.status is None or data.status == "new"):
            order.status = "in_progress"

    # Обновляем данные клиента (только для admin)
    if role_name == "admin":
        client = db.query(User).filter(User.id == order.client_id).first()
        if client:
            if data.client_first_name is not None:
                client.first_name = data.client_first_name
            if data.client_last_name is not None:
                client.last_name = data.client_last_name
            if data.client_phone is not None:
                client.phone = data.client_phone

    if data.worker_id is not None:
        # Проверяем, что работник принадлежит той же мастерской
        worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
        if not worker:
            raise HTTPException(400, "Работник не найден")
        if order.workshop_id and worker.workshop_id != order.workshop_id:
            raise HTTPException(400, "Нельзя назначить работника из другой мастерской")
        order.worker_id = data.worker_id

    if data.description is not None:
        order.description = data.description
    
    # Статус можно менять явно через data.status
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

    role_name = user.role.name if user.role else None
    
    # Мастер может удалять только заявки своих мастерских и только в статусах new/in_progress
    if role_name == "master":
        workshop_ids = [w.id for w in user.workshops]
        if order.workshop_id not in workshop_ids:
            raise HTTPException(403, "Нет доступа к заявке другой мастерской")
        if order.status not in ("new", "in_progress"):
            raise HTTPException(400, "Мастер может удалять только заявки в статусах 'Новая' или 'В работе'")
    
    # Админ может удалять заявки в любом статусе
    db.delete(order)
    db.commit()
    return {"message": "Заявка удалена"}
