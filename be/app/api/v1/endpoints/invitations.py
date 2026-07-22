from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, require_role, get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.schemas.invitation import AcceptInvitationRequest, InvitationCreate, InvitationResponse
from app.services.invitation_service import InvitationService

router = APIRouter()


@router.post("/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    service = InvitationService(db, membership.agency_id)
    return await service.create_or_resend_invitation(current_user.id, data)


@router.get("/", response_model=List[InvitationResponse])
async def list_invitations(
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    service = InvitationService(db, membership.agency_id)
    return await service.list_invitations()


@router.post("/accept", status_code=status.HTTP_200_OK)
async def accept_invitation(
    data: AcceptInvitationRequest,
    db: AsyncSession = Depends(get_db)
):
    service = InvitationService(db)
    user, membership = await service.accept_invitation(data)
    return {
        "message": "Invitation accepted successfully",
        "user_id": user.id,
        "agency_id": membership.agency_id,
        "role": membership.role
    }
