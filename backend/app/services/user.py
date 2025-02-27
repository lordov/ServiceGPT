from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.exceptions import UserAlreadyExists

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security.pwdcrypt import password_hasher


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(session: AsyncSession, user_data: UserCreate):
    hashed_password = password_hasher(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        fullname=user_data.fullname,
    )
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise UserAlreadyExists(
            errors=[f"User with id {user_data.email} already exists"]
        )
