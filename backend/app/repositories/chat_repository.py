from app.repositories.base import SQLAlchemyRepository
from app.models.chat import Chat

class ChatRepository(SQLAlchemyRepository):
    model = Chat
