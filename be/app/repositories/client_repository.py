import uuid
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client
from app.repositories.base import BaseTenantRepository


class ClientRepository(BaseTenantRepository[Client]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(Client, db, agency_id)

    async def search(self, query_str: str) -> List[Client]:
        query = self._base_query().where(
            or_(
                Client.name.ilike(f"%{query_str}%"),
                Client.company_name.ilike(f"%{query_str}%"),
                Client.email.ilike(f"%{query_str}%")
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
