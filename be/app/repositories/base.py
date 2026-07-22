import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseTenantRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession, agency_id: uuid.UUID):
        self.model = model
        self.db = db
        self.agency_id = agency_id

    def _base_query(self):
        query = select(self.model).where(getattr(self.model, "agency_id") == self.agency_id)
        if hasattr(self.model, "is_deleted"):
            query = query.where(getattr(self.model, "is_deleted") == False)
        return query

    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        query = self._base_query().where(getattr(self.model, "id") == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        query = self._base_query()
        if filters:
            for field, val in filters.items():
                if val is not None and hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == val)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> T:
        kwargs["agency_id"] = self.agency_id
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def soft_delete(self, instance: T) -> None:
        if hasattr(instance, "is_deleted"):
            setattr(instance, "is_deleted", True)
            await self.db.flush()
        else:
            await self.db.delete(instance)
            await self.db.flush()
