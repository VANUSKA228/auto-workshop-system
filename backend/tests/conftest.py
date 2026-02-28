"""Фикстуры pytest для тестов API."""

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Role, User

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pre-computed hash для "admin123" (bcrypt)
ADMIN_HASH = bcrypt.hashpw(b"admin123", bcrypt.gensalt(rounds=12)).decode()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed: роли
    for name in ("client", "master", "admin"):
        db.add(Role(name=name))
    db.commit()
    # Admin user
    admin = User(
        first_name="Admin",
        last_name="Test",
        email="admin@test.ru",
        password_hash=ADMIN_HASH,
        role_id=3,
    )
    db.add(admin)
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
