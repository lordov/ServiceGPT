from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth import get_current_user
from app.services.chat import create_chat, get_chats_by_user, create_message, get_messages_by_chat
from app.schemas.chat import ChatCreate, ChatOut, MessageBase, MessageCreate, MessageOut
from app.schemas.user import UserOut
from app.services.chat import Chat
from app.services.openai import generate_chatgpt_response


router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=ChatOut)
async def create_new_chat(
    chat_data: ChatCreate,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    chat = await create_chat(db, chat_data, owner_id=current_user.id)
    return chat


@router.get("/", response_model=list[ChatOut])
async def get_user_chats(
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await get_chats_by_user(db, owner_id=current_user.id)


# @router.post("/{chat_id}/messages", response_model=MessageOut)
# async def send_message(
#     chat_id: int,
#     message_data: MessageCreate,
#     current_user: Annotated[UserOut, Depends(get_current_user)],
#     db: AsyncSession = Depends(get_db),
# ):
#     if chat_id != message_data.chat_id:
#         raise HTTPException(status_code=400, detail="Chat ID mismatch")

#     message = await create_message(db, message_data, sender_id=current_user.id)
#     return message


@router.post("/chats/messages", response_model=MessageOut)
async def create_chat_and_send_message(
    message_data: MessageBase,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    # Получаем ответ от нейросети
    gpt_response = await generate_chatgpt_response(
        first_message=[message_data.content])

    sentences = gpt_response.split('. ')
    first_two_sentences = '. '.join(sentences[0]) + '.'
    # Извлекаем первые два предложения для названия чата
    title = " ".join(gpt_response.split(". " or "! " or "? ")[:2]) + "..."

    # Создаем новый чат с названием, полученным от нейросети
    chat = Chat(title=title, owner_id=current_user.id)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    # Сохраняем сообщение от пользователя
    user_message = MessageCreate(chat_id=chat.id, content=message_data.content)
    await create_message(db, user_message, sender_id=current_user.id)

    # Сохраняем ответ от нейросети
    bot_message = MessageCreate(chat_id=chat.id, content=gpt_response)
    saved_bot_message = await create_message(
        db,
        bot_message,
        sender_id=0,
        role="assistant"
    )

    # Возвращаем информацию о созданном чате и сообщении
    return saved_bot_message


@router.post("/chats/{chat_id}/messages", response_model=MessageOut)
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
    gpt_response = await generate_chatgpt_response(chat_messages=chat_messages)

    # Сохраняем сообщение от пользователя
    user_message = MessageCreate(chat_id=chat_id, content=message_data.content)
    await create_message(db, user_message, sender_id=current_user.id)

    # Сохраняем ответ от нейросети
    bot_message = MessageCreate(chat_id=chat_id, content=gpt_response)
    saved_bot_message = await create_message(db, bot_message, sender_id=0, role="assistant")

    return saved_bot_message
