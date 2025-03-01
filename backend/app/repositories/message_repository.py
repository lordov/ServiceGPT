from sqlalchemy import select, desc
from app.repositories.base import SQLAlchemyRepository
from app.models.chat import Message


class MessageRepository(SQLAlchemyRepository):
    model = Message

    async def get_by_chat(self, chat_id: int, limit: int = 20) -> list[Message]:
        stmt = (
            select(self.model)
            .filter(self.model.chat_id == chat_id)
            .order_by(desc(self.model.id))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
