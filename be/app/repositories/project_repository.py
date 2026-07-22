import uuid
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.project import Project, ProjectStatus
from app.models.project_member import ProjectMember
from app.models.membership import RoleEnum
from app.repositories.base import BaseTenantRepository


class ProjectRepository(BaseTenantRepository[Project]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(Project, db, agency_id)

    async def get_by_id_with_relations(self, project_id: uuid.UUID) -> Optional[Project]:
        query = self._base_query().where(Project.id == project_id).options(selectinload(Project.client))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        query = self._base_query().options(selectinload(Project.client))

        if role == RoleEnum.CLIENT_USER:
            if not client_id:
                return []
            query = query.where(Project.client_id == client_id)
        elif role == RoleEnum.AGENCY_MEMBER:
            member_subquery = select(ProjectMember.project_id).where(
                ProjectMember.user_id == user_id,
                ProjectMember.agency_id == self.agency_id
            )
            query = query.where(
                or_(
                    Project.id.in_(member_subquery),
                    Project.created_by == user_id
                )
            )

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project_detail(
        self,
        project_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[Project]:
        query = self._base_query().where(Project.id == project_id).options(
            selectinload(Project.client),
            selectinload(Project.members).selectinload(ProjectMember.user)
        )

        if role == RoleEnum.CLIENT_USER:
            if not client_id:
                return None
            query = query.where(Project.client_id == client_id)
        elif role == RoleEnum.AGENCY_MEMBER and user_id:
            member_subquery = select(ProjectMember.project_id).where(
                ProjectMember.user_id == user_id,
                ProjectMember.agency_id == self.agency_id
            )
            query = query.where(
                or_(
                    Project.id.in_(member_subquery),
                    Project.created_by == user_id
                )
            )

        result = await self.db.execute(query)
        return result.scalars().first()

    async def assign_members(self, project_id: uuid.UUID, user_ids: List[uuid.UUID]) -> None:
        existing = await self.db.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        for row in existing.scalars().all():
            await self.db.delete(row)

        for u_id in set(user_ids):
            pm = ProjectMember(agency_id=self.agency_id, project_id=project_id, user_id=u_id)
            self.db.add(pm)
        await self.db.flush()

    async def search(self, query_str: str, role: RoleEnum, client_id: Optional[uuid.UUID] = None) -> List[Project]:
        query = self._base_query().options(selectinload(Project.client)).where(
            or_(
                Project.name.ilike(f"%{query_str}%"),
                Project.description.ilike(f"%{query_str}%")
            )
        )
        if role == RoleEnum.CLIENT_USER and client_id:
            query = query.where(Project.client_id == client_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
