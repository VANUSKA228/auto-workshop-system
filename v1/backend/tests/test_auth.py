"""Тесты авторизации и регистрации."""


class TestLogin:
    """Тесты входа в систему."""

    def test_login_success_admin(self, client):
        """Успешный вход администратора."""
        r = client.post("/auth/login", json={"email": "admin@test.ru", "password": "admin123"})
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["id"] == 1

    def test_login_success_master(self, client):
        """Успешный вход мастера."""
        r = client.post("/auth/login", json={"email": "master@test.ru", "password": "master123"})
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert data["user"]["role"] == "master"

    def test_login_success_client(self, client):
        """Успешный вход клиента."""
        r = client.post("/auth/login", json={"email": "client@test.ru", "password": "client123"})
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert data["user"]["role"] == "client"

    def test_login_wrong_password(self, client):
        """Неверный пароль."""
        r = client.post("/auth/login", json={"email": "admin@test.ru", "password": "wrong"})
        assert r.status_code == 401
        assert "Неверный email или пароль" in r.json()["detail"]

    def test_login_wrong_email(self, client):
        """Несуществующий email."""
        r = client.post("/auth/login", json={"email": "nonexistent@test.ru", "password": "admin123"})
        assert r.status_code == 401
        assert "Неверный email или пароль" in r.json()["detail"]

    def test_login_invalid_email_format(self, client):
        """Неверный формат email."""
        r = client.post("/auth/login", json={"email": "invalid-email", "password": "admin123"})
        assert r.status_code == 422


class TestProtectedRoutes:
    """Тесты защищенных маршрутов."""

    def test_protected_route_without_token(self, client):
        """Доступ без токена."""
        r = client.get("/workshops/")
        assert r.status_code == 401

    def test_protected_route_with_valid_token(self, client, admin_token):
        """Доступ с валидным токеном."""
        r = client.get("/workshops/", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_protected_route_with_invalid_token(self, client):
        """Доступ с невалидным токеном."""
        r = client.get("/workshops/", headers={"Authorization": "Bearer invalid-token"})
        assert r.status_code == 401


class TestClientRegistration:
    """Тесты регистрации клиента."""

    def test_client_self_register_success(self, client, db):
        """Успешная самостоятельная регистрация клиента."""
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Новый",
                "last_name": "Клиент",
                "email": "newclient@test.ru",
                "password": "client123",
                "workshop_id": 1,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert data["user"]["role"] == "client"
        assert data["user"]["id"] > 1

    def test_client_register_duplicate_email(self, client):
        """Регистрация с занятым email."""
        # Первая регистрация
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Первый",
                "last_name": "Клиент",
                "email": "duplicate@test.ru",
                "password": "client123",
                "workshop_id": 1,
            },
        )
        assert r.status_code == 200

        # Повторная регистрация с тем же email
        r2 = client.post(
            "/auth/register/client",
            json={
                "first_name": "Второй",
                "last_name": "Клиент",
                "email": "duplicate@test.ru",
                "password": "client123",
                "workshop_id": 1,
            },
        )
        assert r2.status_code == 400
        assert "Email уже занят" in r2.json()["detail"]

    def test_client_register_invalid_workshop(self, client):
        """Регистрация с несуществующей мастерской."""
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Тест",
                "last_name": "Клиент",
                "email": "badworkshop@test.ru",
                "password": "client123",
                "workshop_id": 999,
            },
        )
        assert r.status_code == 400
        assert "Мастерская не найдена" in r.json()["detail"]

    def test_client_register_missing_required_fields(self, client):
        """Регистрация без обязательных полей."""
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Тест",
                "last_name": "Клиент",
                "password": "client123",
            },
        )
        assert r.status_code == 422

    def test_client_register_short_password(self, client):
        """Регистрация с коротким паролем — в версии 1 валидация только на frontend."""
        # В версии 1 валидация длины пароля только на frontend (Yup schema)
        # Backend принимает любой пароль
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Тест",
                "last_name": "Клиент",
                "email": "shortpass@test.ru",
                "password": "12345",
                "workshop_id": 1,
            },
        )
        assert r.status_code == 200

    def test_client_register_invalid_email(self, client):
        """Регистрация с невалидным email."""
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Тест",
                "last_name": "Клиент",
                "email": "invalid-email",
                "password": "client123",
                "workshop_id": 1,
            },
        )
        assert r.status_code == 422

    def test_client_register_and_login(self, client, db):
        """Регистрация и последующий вход."""
        # Регистрация
        r = client.post(
            "/auth/register/client",
            json={
                "first_name": "Новый",
                "last_name": "Клиент",
                "email": "newlogin@test.ru",
                "password": "client123",
                "workshop_id": 1,
            },
        )
        assert r.status_code == 200
        token = r.json()["token"]
        assert token is not None

        # Вход с теми же данными
        r2 = client.post("/auth/login", json={"email": "newlogin@test.ru", "password": "client123"})
        assert r2.status_code == 200
        assert r2.json()["token"] is not None
