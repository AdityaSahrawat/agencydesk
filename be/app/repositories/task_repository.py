import uuid
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.task import Task, TaskStatus
from app.models.project import Project
from app.models.membership import RoleEnum
from app.repositories.base import BaseTenantRepository


class TaskRepository(BaseTenantRepository[Task]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(Task, db, agency_id)

    async def list_tasks(
        self,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        assigned_to: Optional[uuid.UUID] = None,
        status: Optional[TaskStatus] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        query = self._base_query().options(selectinload(Task.assignee))

        if role == RoleEnum.CLIENT_USER:
            # Strictly filter internal content for client users!
            query = query.where(Task.is_internal == False)
            if client_id:
                query = query.join(Project, Task.project_id == Project.id).where(Project.client_id == client_id)

        if project_id:
            query = query.where(Task.project_id == project_id)
        if assigned_to:
            query = query.where(Task.assigned_to == assigned_to)
        if status:
            query = query.where(Task.status == status)
        if search_query:
            query = query.where(
                or_(
                    Task.title.ilike(f"%{search_query}%"),
                    Task.description.ilike(f"%{search_query}%")
                )
            )

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_task_by_id(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Optional[Task]:
        query = self._base_query().where(Task.id == task_id).options(selectinload(Task.assignee))

        if role == RoleEnum.CLIENT_USER:
            query = query.where(Task.is_internal == False)
            if client_id:
                query = query.join(Project, Task.project_id == Project.id).where(Project.client_id == client_id)

        result = await self.db.execute(query)
        return result.scalars().first()

    async def unassign_user_tasks(self, user_id: uuid.UUID) -> None:
        """Edge case handling: When member is removed from agency, unassign active tasks."""
        query = self._base_query().where(
            Task.assigned_to == user_id,
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW])
        )
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        for t in tasks:
            t.assigned_to = None
        await self.db.flush()
