from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from app.models.user import User

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session_maker() as session:
        yield session

async def get_user(email: str, session: AsyncSession):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    try:
        db_dict = result.scalars().all()[0].to_read_model()
    except IndexError:
        return False
    return db_dict