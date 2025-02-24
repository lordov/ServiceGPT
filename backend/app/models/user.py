from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String
from app.models.base import Base
from app.schemas.user import UserOut


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    fullname: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_read_model(self) -> UserOut:
        return UserOut(
            id=self.id,
            email=self.email,
            fullname=self.fullname,
            role=self.role,
            is_active=self.is_active,
        )
