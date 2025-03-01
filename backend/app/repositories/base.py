from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import Table
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import (
    IntegrityError, NoResultFound, 
    MultipleResultsFound, DBAPIError
    )
from app.services.my_logging import logger
from backend.app.core.exceptions.exceptions import NoRowsFoundError, DBError


class AbstractRepository(ABC):

    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model: Table = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        # Шаг 1: Вставка данных
        stmt_insert = insert(self.model).values(**data)
        try:
            await self.session.execute(stmt_insert)

            # Шаг 2: Получение только что созданной записи
            last_id_stmt = select(self.model.id).order_by(
                self.model.id.desc()).limit(1)
            result = await self.session.execute(last_id_stmt)
            last_id = result.scalar_one()

            # Шаг 3: Выборка полной записи по ID
            select_stmt = select(self.model).where(self.model.id == last_id)
            full_result = await self.session.execute(select_stmt)
            created_instance = full_result.scalar_one()

            logger.info(f"Created {self.model.__name__} with data: {data}")
            return created_instance

        except IntegrityError as e:
            logger.error(f"IntegrityError in {self.model.__name__}: {str(e)}")
            raise
        except DBAPIError as e:
            logger.error(
                f"Unexpected error in {self.model.__name__}: {str(e)}")
            raise

    async def get_one(self, id: int):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        try:
            return result.scalar_one()
        except NoResultFound:
            logger.warning(f"{self.model.__name__} with ID {id} not found")
            return None
        except MultipleResultsFound:
            logger.error(
                f"Multiple results found for {self.model.__name__} with ID {id}")
            return None

    async def get_all(self, owner_id: Optional[int] = None):
        query = select(self.model)
        if owner_id is not None:
            query = select(self.model).where(self.model.owner_id == owner_id)
        try:
            result = await self.session.execute(query)
            rows = result.scalars().all()  # Получаем список результатов
            if not rows:  # Если список пустой, выбрасываем исключение
                raise NoRowsFoundError(f'For model {self.model.__name__} not found')
            return rows
        except DBAPIError as e:
            raise DBError(str(e))

    async def edit_one(self, id: int, data: dict):
        if not data:
            logger.warning(
                f"Attempt to update {self.model.__name__} with empty data")
            return None
        stmt = update(self.model).where(self.model.id ==
                                        id).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_one(self, id: int):
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
