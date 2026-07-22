import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.time_entry import TimeEntry
from app.models.project import Project
from app.models.membership import RoleEnum
from app.repositories.base import BaseTenantRepository


class TimeEntryRepository(BaseTenantRepository[TimeEntry]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(TimeEntry, db, agency_id)

    async def list_entries(
        self,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TimeEntry]:
        query = self._base_query().options(selectinload(TimeEntry.user))

        if role == RoleEnum.CLIENT_USER and client_id:
            query = query.join(Project, TimeEntry.project_id == Project.id).where(Project.client_id == client_id)
        elif role == RoleEnum.AGENCY_MEMBER and user_id:
            query = query.where(TimeEntry.user_id == user_id)

        if project_id:
            query = query.where(TimeEntry.project_id == project_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project_total_hours(self, project_id: uuid.UUID) -> float:
        query = select(func.coalesce(func.sum(TimeEntry.hours), 0.0)).where(
            TimeEntry.agency_id == self.agency_id,
            TimeEntry.project_id == project_id
        )
        result = await self.db.execute(query)
        return float(result.scalar_one())

    async def get_total_hours_logged(self, user_id: Optional[uuid.UUID] = None, client_id: Optional[uuid.UUID] = None) -> float:
        query = select(func.coalesce(func.sum(TimeEntry.hours), 0.0)).where(
            TimeEntry.agency_id == self.agency_id
        )
        if user_id:
            query = query.where(TimeEntry.user_id == user_id)
        if client_id:
            query = query.join(Project, TimeEntry.project_id == Project.id).where(Project.client_id == client_id)
        result = await self.db.execute(query)
        return float(result.scalar_one())
