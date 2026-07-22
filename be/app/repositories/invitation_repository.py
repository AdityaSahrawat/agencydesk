import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.invitation import Invitation, InvitationStatus
from app.models.membership import RoleEnum
from app.repositories.base import BaseTenantRepository


class InvitationRepository(BaseTenantRepository[Invitation]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(Invitation, db, agency_id)

    async def get_by_token(self, token: str) -> Optional[Invitation]:
        # Token lookup is cross-tenant resolution since the recipient clicks token link
        query = select(Invitation).where(Invitation.token == token)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_active_invitation_by_email(self, email: str) -> Optional[Invitation]:
        query = self._base_query().where(
            Invitation.email == email.lower(),
            Invitation.status == InvitationStatus.PENDING,
            Invitation.expires_at > datetime.now(timezone.utc)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_invitation(
        self,
        email: str,
        role: RoleEnum,
        token: str,
        expires_at: datetime,
        client_id: Optional[uuid.UUID] = None,
        created_by: Optional[uuid.UUID] = None
    ) -> Invitation:
        invitation = Invitation(
            agency_id=self.agency_id,
            email=email.lower(),
            role=role,
            client_id=client_id,
            token=token,
            status=InvitationStatus.PENDING,
            expires_at=expires_at,
            created_by=created_by
        )
        self.db.add(invitation)
        await self.db.flush()
        await self.db.refresh(invitation)
        return invitation
