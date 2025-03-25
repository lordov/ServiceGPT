from pydantic import BaseModel, ConfigDict


class ChatBase(BaseModel):
    title: str


class ChatCreate(ChatBase):
    owner_id: int


class ChatOut(ChatBase):
    id: int
    owner_id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class MessageSchema(BaseModel):
    content: str


class MessageOut(MessageSchema):
    id: int
    chat_id: int
    sender_id: int

    model_config = ConfigDict(
        from_attributes=True
    )
