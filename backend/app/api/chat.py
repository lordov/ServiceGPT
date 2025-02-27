from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.services.chat import create_chat, get_chats_by_user, create_message, get_messages_by_chat
from app.repositories.chat import ChatRepository
from app.schemas.chat import (
    ChatCreate, ChatOut, ChatBase,
    MessageBase, MessageCreate,
    MessageOut
)
from app.schemas.user import UserOut
from app.services.chat import Chat
from app.services.openai import generate_chatgpt_response
from app.services.my_logging import logger
from app.utils.text import get_title


router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=ChatOut)
async def create_new_chat(
    chat_data: ChatBase,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.add_one(chat_data.model_dump())

    if not chat:
        logger.error(f"Failed to create chat for user {current_user.id}")
        raise HTTPException(status_code=500, detail="Failed to create chat")

    logger.info(f"Chat {chat.id} created by user {current_user.id}")
    return chat


@router.get("/", response_model=list[ChatOut])
async def get_user_chats(
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chats = await chat_repo.get_chats_by_user(current_user.id)

    logger.info(
        f"User {current_user.id} fetched their chat list ({len(chats)} chats)")
    return chats


@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat_by_id(
    chat_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_one(chat_id)

    if not chat or chat.owner_id != current_user.id:
        logger.warning(
            f"User {current_user.id} tried to access non-existing chat {chat_id}")
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_one(chat_id)

    if not chat or chat.owner_id != current_user.id:
        logger.warning(
            f"User {current_user.id} tried to delete non-existing chat {chat_id}")
        raise HTTPException(status_code=404, detail="Chat not found")

    deleted = await chat_repo.delete_one(chat_id)

    if not deleted:
        logger.error(f"Failed to delete chat {chat_id}")
        raise HTTPException(status_code=500, detail="Failed to delete chat")

    logger.info(f"User {current_user.id} deleted chat {chat_id}")
    return {"message": "Chat deleted successfully"}


@router.post("/messages", response_model=MessageOut)
async def create_chat_and_send_message(
    message_data: MessageBase,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    # Получаем ответ от нейросети
    gpt_response = await generate_chatgpt_response(
        message=message_data.content)
    chat_repo = ChatRepository(db)
    title = get_title(gpt_response)

    # Создаем новый чат с названием, полученным от нейросети
    chat = ChatCreate(title=title, owner_id=current_user.id).model_dump()
    chat = await chat_repo.add_one(chat)

    # Сохраняем сообщение от пользователя
    user_message = MessageCreate(chat_id=chat.id, content=message_data.content)
    await create_message(db, user_message, sender_id=current_user.id)

    # Сохраняем ответ от нейросети
    bot_message = MessageCreate(chat_id=chat.id, content=gpt_response)
    saved_bot_message = await create_message(
        db,
        bot_message,
        sender_id=1,
        role="assistant"
    )

    # Возвращаем информацию о созданном чате и сообщении
    return saved_bot_message


@router.post("/{chat_id}/messages", response_model=MessageOut)
async def send_message_to_existing_chat(
    chat_id: int,
    message_data: MessageCreate,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    # Получаем историю сообщений для чата
    chat_messages = await get_messages_by_chat(db, chat_id)

    # Проверка, что чат существует
    if not chat_messages:
        raise HTTPException(status_code=404, detail="Чат не найден")

    # Отправляем в OpenAI API
    gpt_response = await generate_chatgpt_response(message_data.content, chat_messages=chat_messages)

    # Сохраняем сообщение от пользователя
    user_message = MessageCreate(chat_id=chat_id, content=message_data.content)
    await create_message(db, user_message, sender_id=current_user.id)

    # Сохраняем ответ от нейросети
    bot_message = MessageCreate(chat_id=chat_id, content=gpt_response)
    saved_bot_message = await create_message(db, bot_message, sender_id=1, role="assistant")

    return saved_bot_message


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
async def get_chat_messages(
    chat_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    # Проверяем, существует ли чат
    chat = await db.get(Chat, chat_id)
    if not chat or chat.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Чат не найден")

    # Получаем список сообщений
    messages = await get_messages_by_chat(db, chat_id)
    return messages
