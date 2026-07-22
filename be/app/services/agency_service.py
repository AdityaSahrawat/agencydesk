import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ConflictException, NotFoundException
from app.models.agency import Agency
from app.models.membership import AgencyMembership, RoleEnum
from app.repositories.agency_repository import AgencyRepository
from app.schemas.agency import AgencyCreate, AgencyUpdate


class AgencyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agency_repo = AgencyRepository(db)

    async def create_agency(self, creator_id: uuid.UUID, data: AgencyCreate) -> Tuple[Agency, AgencyMembership]:
        slug = data.slug or (data.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:6])
        existing = await self.agency_repo.get_by_slug(slug)
        if existing:
            raise ConflictException(f"Agency with slug '{slug}' already exists")

        agency = await self.agency_repo.create_agency(name=data.name, slug=slug)
        membership = await self.agency_repo.add_membership(
            agency_id=agency.id,
            user_id=creator_id,
            role=RoleEnum.AGENCY_ADMIN
        )
        return agency, membership

    async def get_agency(self, agency_id: uuid.UUID) -> Agency:
        agency = await self.agency_repo.get_by_id(agency_id)
        if not agency:
            raise NotFoundException("Agency not found")
        return agency

    async def update_agency(self, agency_id: uuid.UUID, data: AgencyUpdate) -> Agency:
        agency = await self.get_agency(agency_id)
        if data.name:
            agency.name = data.name
        if data.is_active is not None:
            agency.is_active = data.is_active
        await self.db.flush()
        await self.db.refresh(agency)
        return agency

    async def list_user_agencies(self, user_id: uuid.UUID) -> List[Tuple[Agency, AgencyMembership]]:
        memberships = await self.agency_repo.get_user_memberships(user_id)
        result = []
        for m in memberships:
            agency = await self.agency_repo.get_by_id(m.agency_id)
            if agency and agency.is_active:
                result.append((agency, m))
        return result
