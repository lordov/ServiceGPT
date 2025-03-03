from pydantic import BaseModel
from datetime import datetime
from typing import Union


class ChatBase(BaseModel):
    title: str


class ChatCreate(ChatBase):
    owner_id: int


class ChatOut(ChatBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    content: str


class MessageOut(MessageSchema):
    id: int
    chat_id: int
    sender_id: int

    class Config:
        from_attributes = True
