import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.time_entry import TimeEntry
from app.models.membership import RoleEnum
from app.repositories.time_entry_repository import TimeEntryRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.time_entry import TimeEntryCreate, TimeEntryUpdate


class TimeEntryService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.time_repo = TimeEntryRepository(db, agency_id)
        self.project_repo = ProjectRepository(db, agency_id)

    async def log_time(self, user_id: uuid.UUID, data: TimeEntryCreate, role: RoleEnum) -> TimeEntry:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot log time entries")

        project = await self.project_repo.get_by_id(data.project_id)
        if not project:
            raise NotFoundException("Project not found in agency")

        return await self.time_repo.create(
            project_id=data.project_id,
            task_id=data.task_id,
            user_id=user_id,
            hours=data.hours,
            date=data.date,
            note=data.note
        )

    async def list_time_entries(
        self,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TimeEntry]:
        return await self.time_repo.list_entries(
            role=role,
            client_id=client_id,
            project_id=project_id,
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    async def get_project_total_hours(self, project_id: uuid.UUID) -> float:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        return await self.time_repo.get_project_total_hours(project_id)

    async def update_entry(
        self,
        entry_id: uuid.UUID,
        user_id: uuid.UUID,
        data: TimeEntryUpdate,
        role: RoleEnum
    ) -> TimeEntry:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot modify time entries")

        entry = await self.time_repo.get_by_id(entry_id)
        if not entry:
            raise NotFoundException("Time entry not found")
        if entry.user_id != user_id and role != RoleEnum.AGENCY_ADMIN:
            raise ForbiddenException("You can only edit your own time entries")

        return await self.time_repo.update(
            entry,
            hours=data.hours,
            date=data.date,
            note=data.note
        )

    async def delete_entry(self, entry_id: uuid.UUID, user_id: uuid.UUID, role: RoleEnum) -> None:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot delete time entries")

        entry = await self.time_repo.get_by_id(entry_id)
        if not entry:
            raise NotFoundException("Time entry not found")
        if entry.user_id != user_id and role != RoleEnum.AGENCY_ADMIN:
            raise ForbiddenException("You can only delete your own time entries")

        await self.time_repo.soft_delete(entry)
