import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, require_role, get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.repositories.agency_repository import AgencyRepository
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("/members", response_model=List[UserResponse])
async def list_agency_members(
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    agency_repo = AgencyRepository(db)
    user_repo = UserRepository(db)
    memberships = await agency_repo.list_agency_members(membership.agency_id)

    users = []
    for m in memberships:
        u = await user_repo.get_by_id(m.user_id)
        if u and u.is_active:
            users.append(u)
    return users


@router.delete("/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_agency_member(
    user_id: uuid.UUID,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    await user_service.remove_agency_member(membership.agency_id, user_id)
    return None
