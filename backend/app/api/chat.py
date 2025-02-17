from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.services.chat import create_chat, get_chats_by_user, create_message, get_messages_by_chat
from app.schemas.chat import ChatCreate, ChatOut, MessageCreate, MessageOut
from app.services.user import get_user_by_email


router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=ChatOut)
async def create_new_chat(
    chat_data: ChatCreate,
    current_user: Annotated[ChatOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),  
):
    chat = await create_chat(db, chat_data, owner_id=current_user.id)
    return chat


@router.get("/", response_model=list[ChatOut])
async def get_user_chats(
    current_user: Annotated[ChatOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await get_chats_by_user(db, owner_id=current_user.id)


@router.post("/{chat_id}/messages", response_model=MessageOut)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: Annotated[ChatOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    if chat_id != message_data.chat_id:
        raise HTTPException(status_code=400, detail="Chat ID mismatch")

    message = await create_message(db, message_data, sender_id=current_user.id)
    return message


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
async def get_chat_messages(
    chat_id: int,
    current_user: Annotated[ChatOut, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await get_messages_by_chat(db, chat_id)
