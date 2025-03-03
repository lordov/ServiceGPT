from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Text
from app.models.base import Base
from app.schemas.chat import ChatOut, MessageOut


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)

    messages = relationship("Message", back_populates="chat")

    def to_read_model(self) -> ChatOut:
        return ChatOut(
            chat_id=self.id,
            owner_id=self.owner_id,
            title=self.title,
        )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete='CASCADE'), nullable=False)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, default=0)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default='user')
    
    def to_read_model(self) -> MessageOut:
        return MessageOut(
            content=self.content,
            sender_id=self.sender_id,
            chat_id=self.chat_id,
            id=self.id
        )

    chat = relationship("Chat", back_populates="messages")
