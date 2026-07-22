import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.project import Project
from app.models.membership import RoleEnum
from app.repositories.project_repository import ProjectRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.project_repo = ProjectRepository(db, agency_id)
        self.client_repo = ClientRepository(db, agency_id)

    async def create_project(self, creator_id: uuid.UUID, data: ProjectCreate) -> Project:
        client = await self.client_repo.get_by_id(data.client_id)
        if not client:
            raise NotFoundException("Client not found in agency")
        project = await self.project_repo.create(
            client_id=data.client_id,
            name=data.name,
            description=data.description,
            status=data.status,
            created_by=creator_id
        )
        return await self.project_repo.get_by_id_with_relations(project.id)

    async def get_project(
        self,
        project_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> Project:
        project = await self.project_repo.get_project_detail(project_id, role, client_id, user_id)
        if not project:
            raise NotFoundException("Project not found or access denied")
        return project

    async def list_projects(
        self,
        user_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        return await self.project_repo.list_for_user(user_id, role, client_id, skip=skip, limit=limit)

    async def update_project(
        self,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Project:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot modify projects")
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")

        if data.client_id:
            c = await self.client_repo.get_by_id(data.client_id)
            if not c:
                raise NotFoundException("Target client not found")

        await self.project_repo.update(
            project,
            name=data.name,
            description=data.description,
            status=data.status,
            client_id=data.client_id
        )
        return await self.project_repo.get_by_id_with_relations(project_id)

    async def delete_project(self, project_id: uuid.UUID, role: RoleEnum) -> None:
        if role != RoleEnum.AGENCY_ADMIN:
            raise ForbiddenException("Only agency admins can delete projects")
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        await self.project_repo.soft_delete(project)

    async def assign_members(self, project_id: uuid.UUID, user_ids: List[uuid.UUID], role: RoleEnum) -> None:
        if role == RoleEnum.CLIENT_USER:
            raise ForbiddenException("Client users cannot assign project members")
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        await self.project_repo.assign_members(project_id, user_ids)

    async def search_projects(self, query_str: str, role: RoleEnum, client_id: Optional[uuid.UUID] = None) -> List[Project]:
        return await self.project_repo.search(query_str, role, client_id)
