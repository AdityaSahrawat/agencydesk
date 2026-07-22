import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ConflictException, NotFoundException, ForbiddenException, AgencyDeskException
from app.core.security import get_password_hash
from app.models.invitation import Invitation, InvitationStatus
from app.models.membership import AgencyMembership, RoleEnum
from app.models.user import User
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.agency_repository import AgencyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.invitation import InvitationCreate, AcceptInvitationRequest


def is_expired(expires_at: datetime) -> bool:
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)
    return expires_at < now


class InvitationService:
    def __init__(self, db: AsyncSession, agency_id: Optional[uuid.UUID] = None):
        self.db = db
        self.agency_id = agency_id
        if agency_id:
            self.invitation_repo = InvitationRepository(db, agency_id)
        self.agency_repo = AgencyRepository(db)
        self.user_repo = UserRepository(db)

    async def create_or_resend_invitation(
        self,
        creator_id: uuid.UUID,
        data: InvitationCreate
    ) -> Invitation:
        if not self.agency_id:
            raise AgencyDeskException("Agency context required")

        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            m = await self.agency_repo.get_membership(self.agency_id, existing_user.id)
            if m:
                raise ConflictException("User is already a member of this agency")

        existing_invite = await self.invitation_repo.get_active_invitation_by_email(data.email)
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc)

        if existing_invite:
            existing_invite.token = token
            existing_invite.expires_at = expires_at + timedelta(days=7)
            existing_invite.role = data.role
            existing_invite.client_id = data.client_id
            await self.db.flush()
            await self.db.refresh(existing_invite)
            return existing_invite

        return await self.invitation_repo.create_invitation(
            email=data.email,
            role=data.role,
            client_id=data.client_id,
            token=token,
            expires_at=expires_at + timedelta(days=7),
            created_by=creator_id
        )

    async def accept_invitation(self, req: AcceptInvitationRequest) -> Tuple[User, AgencyMembership]:
        invitation_repo = InvitationRepository(self.db, uuid.uuid4())
        invitation = await invitation_repo.get_by_token(req.token)

        if not invitation:
            raise NotFoundException("Invitation token not found")

        if invitation.status == InvitationStatus.ACCEPTED:
            user = await self.user_repo.get_by_email(invitation.email)
            if user:
                m = await self.agency_repo.get_membership(invitation.agency_id, user.id)
                if m:
                    return user, m
            raise ConflictException("Invitation has already been accepted")

        if invitation.status != InvitationStatus.PENDING or is_expired(invitation.expires_at):
            invitation.status = InvitationStatus.EXPIRED
            await self.db.flush()
            raise ConflictException("Invitation has expired or is no longer valid")

        user = await self.user_repo.get_by_email(invitation.email)
        if not user:
            if not req.password or not req.full_name:
                raise AgencyDeskException("password and full_name are required for new user registration")
            hashed_pw = get_password_hash(req.password)
            user = await self.user_repo.create_user(
                email=invitation.email,
                hashed_password=hashed_pw,
                full_name=req.full_name
            )

        m = await self.agency_repo.get_membership(invitation.agency_id, user.id)
        if not m:
            m = await self.agency_repo.add_membership(
                agency_id=invitation.agency_id,
                user_id=user.id,
                role=invitation.role,
                client_id=invitation.client_id
            )

        invitation.status = InvitationStatus.ACCEPTED
        await self.db.flush()
        return user, m

    async def list_invitations(self) -> List[Invitation]:
        if not self.agency_id:
            return []
        return await self.invitation_repo.list_all()
