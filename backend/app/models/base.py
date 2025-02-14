from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from datetime import datetime


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(
        DateTime(), default=datetime.now, nullable=True
    )
    updated: Mapped[DateTime] = mapped_column(
        DateTime(), default=datetime.now, onupdate=datetime.now, nullable=True
    )
