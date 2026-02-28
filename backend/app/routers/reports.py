# backend/app/routers/reports.py
"""
Роутер отчётов.
GET /reports/personal — Master (заполняет), Admin (просматривает).
GET /reports/finance — только Admin.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.order import Order
from ..models.payment import Payment
from ..models.user import User
from ..dependencies import role_required

router = APIRouter()


@router.get("/personal")
def personal_report(
    db: Session = Depends(get_db),
    user=Depends(role_required("master", "admin")),
):
    """Отчёт по персоналу: заявки по мастерам. Заглушка — расширить по ТЗ."""
    # Пример: заявки по мастерам
    q = db.query(User.last_name, User.first_name, func.count(Order.id).label("orders_count")).join(
        Order, User.id == Order.master_id
    ).group_by(User.id, User.last_name, User.first_name)
    return [{"master": f"{r.last_name} {r.first_name}", "orders_count": r.orders_count} for r in q.all()]


@router.get("/finance")
def finance_report(
    db: Session = Depends(get_db),
    user=Depends(role_required("admin")),
):
    """Финансовый отчёт. Заглушка — расширить по ТЗ."""
    total = db.query(func.sum(Payment.amount)).filter(Payment.status == "stub_ok").scalar()
    return {"total_payments": float(total or 0), "currency": "RUB"}
