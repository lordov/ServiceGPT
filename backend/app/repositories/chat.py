from app.repositories.base import BaseRepository
from app.models.chat import Chat, Message
from app.services.my_logging import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete


class ChatRepository(BaseRepository):
    model = Chat

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_chats_by_user(self, owner_id: int):
        result = await self.session.execute(select(Chat).filter(Chat.owner_id == owner_id))
        return result.scalars().all()
    
    async def delete_one(self, chat_id: int):
        try:
            # Удаляем сначала все сообщения, связанные с этим чатом
            await self.session.execute(delete(Message).where(Message.chat_id == chat_id))
            
            # Затем удаляем сам чат
            deleted = await super().delete_one(chat_id)

            if deleted:
                logger.info(f"Deleted chat {chat_id} and its messages")
            else:
                logger.warning(f"Failed to delete chat {chat_id}")

            return deleted
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {str(e)}")
            return False
