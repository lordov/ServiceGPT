import pytest
import pytest_asyncio
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from app.core.config.settings import settings
from app.core.security.auth import get_current_user
from app.api.chat import get_chat_service
from app.main import app
from app.models.base import Base
from app.schemas.user import UserOut
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository


test_engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


class TestIUnitOfWork(ABC):
    chat: ChatRepository
    message: MessageRepository
    user: UserRepository
    
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class RunUnitOfWork(TestIUnitOfWork):
    def __init__(self):
        self.session_factory = TestSessionLocal

    async def __aenter__(self):
        self.session = self.session_factory()

        self.chat = ChatRepository(self.session)
        self.message = MessageRepository(self.session)
        self.user = UserRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


# Фикстура для создания тестовой БД
@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаём таблицы

    
    async with TestSessionLocal() as session:
        yield session

    # async with test_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)  # Удаляем таблицы после теста

# Фикстура для подмены UnitOfWork на тестовую сессию
@pytest.fixture
def override_get_uow(test_db):
    async def _override():
        uow = RunUnitOfWork()
        uow.session = test_db  # Используем тестовую сессию
        return uow

    # Подменяем зависимость UnitOfWork для FastAPI
    app.dependency_overrides[RunUnitOfWork] = _override
    yield
    # Убираем подмену зависимости после выполнения теста
    app.dependency_overrides.pop(RunUnitOfWork, None)

# Фикстура для подмены зависимости авторизации
@pytest.fixture
def override_get_current_user():
    async def fake_get_current_user():
        # Здесь возвращаем фиктивного пользователя; подстроите поля под вашу модель
        return UserOut(id=1, email="test@example.com", full_name="Test User")
    app.dependency_overrides[get_current_user] = fake_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


# Фикстура для подмены зависимости ChatService
@pytest.fixture
def override_get_chat_service():
    async def fake_get_chat_service():
        class FakeChatService:
            async def get_chats_by_user(self, user_id: int):
                return [
                    {"id": 1, "title": "Test Chat", "owner_id": 1}
                ]
            async def create_chat_and_send_message(self, message_data: dict, user_id: int):
                return {"id": 1, "content": "Test message", "sender_id": 1, "chat_id": 1}
        return FakeChatService()

    app.dependency_overrides[get_chat_service] = fake_get_chat_service
    yield
    app.dependency_overrides.pop(get_chat_service, None)
