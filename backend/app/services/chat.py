from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, ChatOut, MessageCreate


async def create_chat(db: AsyncSession, chat_id: int, response: str, owner_id: int):
    # Сохраняем сообщение и ответ от OpenAI
    new_chat = Chat(
        id=chat_id,
        owner_id=owner_id,
        message=response,
    )
    db.add(new_chat)
    await db.commit()
    return ChatOut(
        chat_id=chat_id,
        message=response,
        response=response,
        owner_id=owner_id,
    )


async def get_chats_by_user(session: AsyncSession, owner_id: int) -> list[Chat]:
    result = await session.execute(select(Chat).filter(Chat.owner_id == owner_id))
    return result.scalars().all()


async def create_message(session: AsyncSession, message_data: MessageCreate, sender_id: int):
    message = Message(
        chat_id=message_data.chat_id,
        sender_id=sender_id,
        content=message_data.content
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def get_messages_by_chat(session: AsyncSession, chat_id: int) -> list[Message]:
    result = await session.execute(select(Message).filter(Message.chat_id == chat_id))
    return result.scalars().all()
