from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.chat import Chat, Message
from app.schemas.chat import ChatOut, MessageCreate, MessageOut, ChatCreate
from app.utils.unit_of_work import IUnitOfWork
from app.services.my_logging import logger


class ChatService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def create_chat(
            self,
            data: ChatCreate
    ) -> ChatOut:
        async with self.uow:
            chat: Chat = await self.uow.chat.add_one(data.model_dump())
            chat_to_return = ChatOut.model_validate(chat)
            await self.uow.commit()
            logger.info(f"Chat {chat.id} created by user {data.owner_id}")
            return chat_to_return

    async def get_chats_by_user(self, owner_id: int) -> list[Chat]:
        async with self.uow:
            try:
                chats = await self.uow.chat.get_all(owner_id == owner_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        logger.info(
            f"User {owner_id} fetched their chat list ({len(chats)} chats)")
        return [ChatOut.model_validate(chats)]


    async def create_message(
            session: AsyncSession,
            message_data: MessageCreate,
            sender_id: int,
            role: str | None = None
    ):
        message = Message(
            chat_id=message_data.chat_id,
            sender_id=sender_id,
            content=message_data.content,
            role=role
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return MessageOut(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            content=message.content
        )

    async def get_messages_by_chat(db: AsyncSession, chat_id: int, limit: int = 20) -> list[Message]:
        result = await db.execute(
            select(Message).filter(Message.chat_id == chat_id).order_by(
                desc(Message.chat_id)).limit(limit)
        )
        return result.scalars().all()
