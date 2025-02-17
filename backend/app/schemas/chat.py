from pydantic import BaseModel
from datetime import datetime


class ChatBase(BaseModel):
    title: str


class ChatCreate(ChatBase):
    pass


class ChatOut(ChatBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    chat_id: int


class MessageOut(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
