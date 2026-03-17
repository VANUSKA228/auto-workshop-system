"""Тесты мастерских."""


class TestWorkshopsPublic:
    """Тесты публичного списка мастерских."""

    def test_list_workshops_public_without_auth(self, client):
        """Получение списка мастерских без авторизации."""
        r = client.get("/workshops/public")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_workshops_public_with_auth(self, client, admin_token):
        """Получение списка мастерских с авторизацией."""
        r = client.get("/workshops/public", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)


class TestWorkshopsAuthenticated:
    """Тесты авторизованного доступа к мастерским."""

    def test_list_workshops_admin(self, client, admin_token):
        """Админ видит все мастерские."""
        r = client.get("/workshops/", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_list_workshops_master(self, client, master_token):
        """Мастер видит свои мастерские."""
        r = client.get("/workshops/", headers={"Authorization": f"Bearer {master_token}"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_list_workshops_without_auth(self, client):
        """Без авторизации доступ запрещен."""
        r = client.get("/workshops/")
        assert r.status_code == 401

    def test_get_workshop_by_id_admin(self, client, admin_token):
        """Админ получает информацию о мастерской."""
        r = client.get("/workshops/1", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == 1
        assert "name" in data

    def test_get_nonexistent_workshop(self, client, admin_token):
        """Получение несуществующей мастерской."""
        r = client.get("/workshops/999", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 404
