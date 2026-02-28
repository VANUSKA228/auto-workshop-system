"""Тесты заявок."""

import bcrypt
import pytest
from app.models import User, Order, OrderService, Service


def test_create_order(client, admin_token, db):
    # Создаём клиента
    client_hash = bcrypt.hashpw(b"client123", bcrypt.gensalt(rounds=12)).decode()
    client_user = User(
        first_name="Иван",
        last_name="Иванов",
        email="client@test.ru",
        password_hash=client_hash,
        role_id=1,
    )
    db.add(client_user)
    db.commit()
    # Создаём услугу
    svc = Service(name="Тест", price=1000)
    db.add(svc)
    db.commit()
    # Логинимся как клиент и создаём заявку
    login = client.post("/auth/login", json={"email": "client@test.ru", "password": "client123"})
    assert login.status_code == 200
    token = login.json()["token"]
    r = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "car_brand": "Toyota",
            "car_model": "Camry",
            "car_year": 2020,
            "description": "Тест",
            "service_ids": [svc.id],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["car_brand"] == "Toyota"
    assert data["status"] == "new"
    assert len(data["order_services"]) == 1


def test_list_orders_admin(client, admin_token):
    r = client.get("/orders/", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
