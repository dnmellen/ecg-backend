from collections.abc import Sequence
from uuid import UUID
from typing import Generic, TypeVar
from sqlalchemy import select

from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


class EntityDAL(Generic[T]):
    """Data Access Layer for SQLAlchemy entities"""

    model = None

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session: AsyncSession = db_session

    async def create(self, entity: T) -> T:
        self.db_session.add(entity)
        await self.db_session.commit()
        await self.db_session.refresh(entity)
        return entity

    async def create_bulk(self, entities: Sequence[T]) -> bool:
        self.db_session.add_all(entities)
        await self.db_session.commit()
        return True

    async def list(self, where_expr: BinaryExpression | None = None) -> list[T]:
        if where_expr is None:
            results = await self.db_session.execute(select(self.model))
        else:
            results = await self.db_session.execute(
                select(self.model).where(where_expr)
            )
        items = results.all()
        return items

    async def get(self, id: UUID) -> T:
        item = (
            await self.db_session.scalars(select(self.model).where(self.model.id == id))
        ).first()
        return item

    async def get_by_field(self, field, value) -> T:
        item = (
            await self.db_session.scalars(
                select(self.model).where(getattr(self.model, field) == value)
            )
        ).first()
        return item

    async def update(self, entity: T) -> T:
        self.db_session.add(entity)
        await self.db_session.commit()
        await self.db_session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> T:
        await self.db_session.delete(entity)
        await self.db_session.commit()
        return entity
