import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.task import Task, TaskStatus
from app.models.membership import RoleEnum
from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskAssignUpdate


class TaskService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.task_repo = TaskRepository(db, agency_id)
        self.project_repo = ProjectRepository(db, agency_id)

    async def create_task(self, creator_id: uuid.UUID, data: TaskCreate, role: RoleEnum) -> Task:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users are not permitted to create tasks")

        project = await self.project_repo.get_by_id(data.project_id)
        if not project:
            raise NotFoundException("Project not found in agency")

        task = await self.task_repo.create(
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            assigned_to=data.assigned_to,
            is_internal=data.is_internal,
            created_by=creator_id
        )
        return task

    async def get_task(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Task:
        task = await self.task_repo.get_task_by_id(task_id, role, client_id)
        if not task:
            raise NotFoundException("Task not found or internal access forbidden")
        return task

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
        return await self.task_repo.list_tasks(
            role=role,
            client_id=client_id,
            project_id=project_id,
            assigned_to=assigned_to,
            status=status,
            search_query=search_query,
            skip=skip,
            limit=limit
        )

    async def update_task(
        self,
        task_id: uuid.UUID,
        data: TaskUpdate,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Task:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot update tasks")

        task = await self.get_task(task_id, role, client_id)
        return await self.task_repo.update(
            task,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            assigned_to=data.assigned_to,
            is_internal=data.is_internal
        )

    async def update_status(
        self,
        task_id: uuid.UUID,
        data: TaskStatusUpdate,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Task:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot change task status")

        task = await self.get_task(task_id, role, client_id)
        return await self.task_repo.update(task, status=data.status)

    async def assign_user(
        self,
        task_id: uuid.UUID,
        data: TaskAssignUpdate,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Task:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot assign users to tasks")

        task = await self.get_task(task_id, role, client_id)
        return await self.task_repo.update(task, assigned_to=data.assigned_to)

    async def delete_task(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> None:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot delete tasks")

        task = await self.get_task(task_id, role, client_id)
        await self.task_repo.soft_delete(task)
