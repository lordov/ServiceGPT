from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from backend.app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(75), nullable=False)
