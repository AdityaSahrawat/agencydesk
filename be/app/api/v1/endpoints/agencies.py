import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, require_role, get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.schemas.agency import AgencyCreate, AgencyResponse, AgencyUpdate, AgencyWithRoleResponse
from app.services.agency_service import AgencyService

router = APIRouter()


@router.post("/", response_model=AgencyResponse, status_code=status.HTTP_201_CREATED)
async def create_agency(
    data: AgencyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    agency_service = AgencyService(db)
    agency, _ = await agency_service.create_agency(current_user.id, data)
    return agency


@router.get("/my-agencies", response_model=List[AgencyWithRoleResponse])
async def list_my_agencies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    agency_service = AgencyService(db)
    pairs = await agency_service.list_user_agencies(current_user.id)
    res = []
    for agency, m in pairs:
        res.append(
            AgencyWithRoleResponse(
                id=agency.id,
                name=agency.name,
                slug=agency.slug,
                is_active=agency.is_active,
                created_at=agency.created_at,
                updated_at=agency.updated_at,
                role=m.role,
                client_id=m.client_id
            )
        )
    return res


@router.get("/current", response_model=AgencyResponse)
async def get_current_tenant_agency(
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    agency_service = AgencyService(db)
    return await agency_service.get_agency(membership.agency_id)


@router.patch("/current", response_model=AgencyResponse)
async def update_current_agency(
    data: AgencyUpdate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    agency_service = AgencyService(db)
    return await agency_service.update_agency(membership.agency_id, data)
