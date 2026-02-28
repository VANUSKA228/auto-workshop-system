"""Тесты авторизации."""

import pytest


def test_login_success(client):
    r = client.post("/auth/login", json={"email": "admin@test.ru", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["user"]["role"] == "admin"
    assert data["user"]["id"] == 1


def test_login_wrong_password(client):
    r = client.post("/auth/login", json={"email": "admin@test.ru", "password": "wrong"})
    assert r.status_code == 401


def test_login_wrong_email(client):
    r = client.post("/auth/login", json={"email": "nonexistent@test.ru", "password": "admin123"})
    assert r.status_code == 401


def test_protected_route_without_token(client):
    r = client.get("/orders/")
    assert r.status_code == 401  # No credentials (HTTPBearer returns 401)


def test_protected_route_with_token(client, admin_token):
    r = client.get("/orders/", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
