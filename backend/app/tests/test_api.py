import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_get_user_chats():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/api/chats/")
        assert response.status_code == 401
        data = response.json()
        assert data == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_send_first_message():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post("/api/chats/messages", json={"content": "test"})
        assert response.status_code == 401
        data = response.json()
        assert data == {"detail": "Not authenticated"}
