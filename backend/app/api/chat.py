from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from backend.app.core.security.auth import get_current_user
# from app.services.chat import create_chat, get_chats_by_user, create_message, get_messages_by_chat
from app.services.chat_services import ChatService
from app.utils.unit_of_work import IUnitOfWork, UnitOfWork
from backend.app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatCreate, ChatOut, ChatBase,
    MessageSchema,
    MessageOut
)
from app.schemas.user import UserOut
from app.services.openai import generate_chatgpt_response
from app.services.my_logging import logger
from app.utils.text import get_title


router = APIRouter(prefix="/chats", tags=["Chats"])


async def get_chat_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> ChatService:
    return ChatService(uow)


@router.post("/", response_model=ChatOut)
async def create_new_chat(
    chat_data: ChatBase,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)
):
    data = ChatCreate(**chat_data.model_dump(), owner_id=current_user.id)
    return await chat_service.create_chat(data)


@router.get("/", response_model=list[ChatOut])
async def get_user_chats(
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.get_chats_by_user(current_user.id)


# @router.get("/{chat_id}", response_model=ChatOut)
# async def get_chat_by_id(
#     chat_id: int,
#     current_user: Annotated[UserOut, Depends(get_current_user)],
#     chat_service: ChatService = Depends(get_chat_service)
# ):
#     chat_repo = ChatRepository(db)
#     chat = await chat_repo.get_one(chat_id)

#     if not chat or chat.owner_id != current_user.id:
#         logger.warning(
#             f"User {current_user.id} tried to access non-existing chat {chat_id}")
#         raise HTTPException(status_code=404, detail="Chat not found")

#     return chat


# @router.delete("/{chat_id}")
# async def delete_chat(
#     chat_id: int,
#     current_user: Annotated[UserOut, Depends(get_current_user)],
#     db: AsyncSession = Depends(get_db),
# ):
#     chat_repo = ChatRepository(db)
#     chat = await chat_repo.get_one(chat_id)

#     if not chat or chat.owner_id != current_user.id:
#         logger.warning(
#             f"User {current_user.id} tried to delete non-existing chat {chat_id}")
#         raise HTTPException(status_code=404, detail="Chat not found")

#     deleted = await chat_repo.delete_one(chat_id)

#     if not deleted:
#         logger.error(f"Failed to delete chat {chat_id}")
#         raise HTTPException(status_code=500, detail="Failed to delete chat")

#     logger.info(f"User {current_user.id} deleted chat {chat_id}")
#     return {"message": "Chat deleted successfully"}


@router.post("/messages", response_model=MessageOut)
async def send_first_message(
    message_data: MessageSchema,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.create_chat_and_send_message(
        message_data, current_user)

@router.post("/{chat_id}/messages", response_model=MessageOut)
async def send_message_to_existing_chat(
    chat_id: int,
    message_data: MessageSchema,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)

):
    return await chat_service.send_message_to_chat(
        chat_id, message_data, current_user)


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
async def get_chat_messages(
    chat_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.get_chat_messages(chat_id, current_user)
