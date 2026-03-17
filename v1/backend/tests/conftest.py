"""Фикстуры pytest для тестов API."""

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import Role, User
from app.models.workshop import Workshop, user_workshop_link

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ADMIN_HASH = bcrypt.hashpw(b"admin123", bcrypt.gensalt(rounds=12)).decode()
MASTER_HASH = bcrypt.hashpw(b"master123", bcrypt.gensalt(rounds=12)).decode()
CLIENT_HASH = bcrypt.hashpw(b"client123", bcrypt.gensalt(rounds=12)).decode()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Создаем роли
    client_role = Role(name="client")
    master_role = Role(name="master")
    admin_role = Role(name="admin")
    db.add_all([client_role, master_role, admin_role])
    db.commit()
    
    # Создаем тестовую мастерскую
    workshop = Workshop(
        name="Тестовая мастерская",
        city="Москва",
        address="ул. Тестовая 1",
        phone="+7 999 000-00-00"
    )
    db.add(workshop)
    db.commit()
    db.refresh(workshop)
    
    # Создаем администратора
    admin = User(
        first_name="Admin",
        last_name="Test",
        email="admin@test.ru",
        password_hash=ADMIN_HASH,
        role_id=admin_role.id,
        is_active=True
    )
    db.add(admin)
    db.commit()
    
    # Создаем мастера и привязываем к мастерской через M2M
    master = User(
        first_name="Master",
        last_name="Test",
        email="master@test.ru",
        password_hash=MASTER_HASH,
        role_id=master_role.id,
        is_active=True
    )
    db.add(master)
    db.commit()
    db.refresh(master)
    
    # Привязываем мастера к мастерской через M2M таблицу
    db.execute(
        user_workshop_link.insert().values(
            user_id=master.id,
            workshop_id=workshop.id,
            role_in_workshop="master"
        )
    )
    db.commit()
    
    # Создаем клиента и привязываем к мастерской
    client = User(
        first_name="Client",
        last_name="Test",
        email="client@test.ru",
        password_hash=CLIENT_HASH,
        role_id=client_role.id,
        is_active=True
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    
    db.execute(
        user_workshop_link.insert().values(
            user_id=client.id,
            workshop_id=workshop.id,
            role_in_workshop="client"
        )
    )
    db.commit()
    
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    r = client.post("/auth/login", json={"email": "admin@test.ru", "password": "admin123"})
    assert r.status_code == 200
    return r.json()["token"]


@pytest.fixture
def master_token(client):
    r = client.post("/auth/login", json={"email": "master@test.ru", "password": "master123"})
    assert r.status_code == 200
    return r.json()["token"]


@pytest.fixture
def client_token(client):
    r = client.post("/auth/login", json={"email": "client@test.ru", "password": "client123"})
    assert r.status_code == 200
    return r.json()["token"]
