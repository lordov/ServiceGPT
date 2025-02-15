from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    fullname: str | None = None
    role: RoleEnum | None = 'user'
    is_active: bool = True


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    fullname: str | None = None


class UserOut(UserBase):
    id: int


class UserInDB(UserOut):
    hashed_password: str
