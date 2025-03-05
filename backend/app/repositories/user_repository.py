from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.repositories.base import SQLAlchemyRepository
from app.models.user import User
from app.core.security.pwdcrypt import password_hasher
from app.schemas.user import UserCreate


from app.core.exceptions.exceptions import UserAlreadyExists


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).filter(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, user_data: UserCreate, hashed_password: str) -> User:

        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            fullname=user_data.fullname,
        )
        try:
            self.session.add(user)
            await self.session.flush()
            return user
        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExists(
                f"User with email {user_data.email} already exists")
