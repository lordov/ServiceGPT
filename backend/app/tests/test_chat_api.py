import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from app.schemas.chat import ChatCreate, ChatOut, MessageOut
from app.tests.conftest import RunUnitOfWork
from app.services.chat_service import ChatService


# Тест эндпоинта /, который возвращает список чатов
@pytest.mark.asyncio
async def test_get_user_chats(override_get_current_user, override_get_chat_service):
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.get("/api/chats/")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        # Проверяем, что ответ — это список с ожидаемыми данными
        assert isinstance(data, list)
        assert len(data) == 1

        # Проверяем соответствие модели ChatOut
        chat = ChatOut(**data[0])  # Если данные неверны, Pydantic вызовет ошибку валидации

        assert chat.id == 1
        assert chat.title == "Test Chat"
        assert chat.owner_id == 1

@pytest.mark.asyncio
async def test_send_first_message(override_get_current_user, override_get_chat_service):
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.post("/api/chats/messages", json={})  # Отправляем пустой json
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 
        response = await client.post("/api/chats/messages", json={"content": "test"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, dict)
        message = MessageOut(**data)
        assert message.sender_id == 1
        assert message.content == "Test message"
        assert message.chat_id == 1


# # Тест для создания чата через API
# @pytest.mark.asyncio
# async def test_create_chat(override_get_current_user, override_get_uow, override_get_chat_service):
#     uow = RunUnitOfWork()
#     chat_data = {"title": "Test Chat", "owner_id": 1}
#     chat_service = ChatService(uow)
#     created_chat = await chat_service.create_chat(ChatCreate(**chat_data))

#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         response = await client.get("/api/chats/")  # Получаем все чаты
#         assert response.status_code == 200
#         data = response.json()

#         chat = ChatOut(**data[0])  # Если данные неверны, Pydantic вызовет ошибку валидации
#         assert chat.id == created_chat.id
#         assert chat.owner_id == 1
#         assert chat.title == "Test Chat"