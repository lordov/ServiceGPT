from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.security.auth import get_current_user
from app.services.chat_services import ChatService
from app.utils.unit_of_work import IUnitOfWork, UnitOfWork
from app.schemas.chat import (
    ChatOut,
    MessageSchema,
    MessageOut
)
from app.schemas.user import UserOut


router = APIRouter(prefix="/chats", tags=["Chats"])


async def get_chat_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> ChatService:
    return ChatService(uow)


@router.get("/", response_model=list[ChatOut])
async def get_user_chats(
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.get_chats_by_user(current_user.id)


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.delete_chat(chat_id, current_user)


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
