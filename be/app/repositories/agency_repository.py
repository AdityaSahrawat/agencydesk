import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agency import Agency
from app.models.membership import AgencyMembership, RoleEnum


class AgencyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agency(self, name: str, slug: str) -> Agency:
        agency = Agency(name=name, slug=slug)
        self.db.add(agency)
        await self.db.flush()
        await self.db.refresh(agency)
        return agency

    async def get_by_id(self, agency_id: uuid.UUID) -> Optional[Agency]:
        query = select(Agency).where(Agency.id == agency_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_slug(self, slug: str) -> Optional[Agency]:
        query = select(Agency).where(Agency.slug == slug)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def add_membership(
        self,
        agency_id: uuid.UUID,
        user_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> AgencyMembership:
        membership = AgencyMembership(
            agency_id=agency_id,
            user_id=user_id,
            role=role,
            client_id=client_id
        )
        self.db.add(membership)
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def get_membership(self, agency_id: uuid.UUID, user_id: uuid.UUID) -> Optional[AgencyMembership]:
        query = select(AgencyMembership).where(
            AgencyMembership.agency_id == agency_id,
            AgencyMembership.user_id == user_id,
            AgencyMembership.is_active == True
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_memberships(self, user_id: uuid.UUID) -> List[AgencyMembership]:
        query = select(AgencyMembership).where(
            AgencyMembership.user_id == user_id,
            AgencyMembership.is_active == True
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_agency_members(self, agency_id: uuid.UUID) -> List[AgencyMembership]:
        query = select(AgencyMembership).where(
            AgencyMembership.agency_id == agency_id,
            AgencyMembership.is_active == True
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
