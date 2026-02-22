from fastapi import status
from httpx import AsyncClient


class TestAPI:
    """Тесты для API приложения."""

    async def test_root_endpoint(self, client: AsyncClient):
        """Тестирование корневого эндпоинта."""
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Приложение работает!"}

    async def test_create_short_link(self, client: AsyncClient):
        """Тестирование создания короткой ссылки."""
        payload = {"url": "https://www.example.com/test/"}
        response = await client.post(
            "/links/",
            json=payload
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "short_url" in data
        assert data["original_url"] == payload["url"]

    async def test_create_short_link_invalid_url(self, client: AsyncClient):
        """Тестирование создания короткой ссылки с невалидным URL."""
        payload = {"url": "invalid-url"}
        response = await client.post(
            "/links/",
            json=payload
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_redirect_to_original_url(self, client: AsyncClient):
        """Тестирование редиректа по короткой ссылке."""
        # Создаем ссылку
        payload = {"url": "https://www.example.com/redirect-test/"}
        create_response = await client.post(
            "/links/",
            json=payload
        )
        short_url = create_response.json()["short_url"]
        short_code = short_url.rsplit("/", 1)[-1]
        #  Тестируем редирект
        response = await client.get(
            f"/links/{short_code}",
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == payload["url"]

    async def test_redirect_nonexistent_short_link(self, client: AsyncClient):
        """Тестирование редиректа по несуществующей короткой ссылке."""
        response = await client.get(
            "/links/nonexistent",
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Ссылка не найдена."}
