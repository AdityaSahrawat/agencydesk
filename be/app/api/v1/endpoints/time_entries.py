import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, require_role, get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.schemas.time_entry import (
    ProjectTotalHoursResponse,
    TimeEntryCreate,
    TimeEntryResponse,
    TimeEntryUpdate
)
from app.services.time_entry_service import TimeEntryService

router = APIRouter()


@router.post("/", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def log_time_entry(
    data: TimeEntryCreate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    service = TimeEntryService(db, membership.agency_id)
    return await service.log_time(current_user.id, data, membership.role)


@router.get("/", response_model=List[TimeEntryResponse])
async def list_time_entries(
    project_id: Optional[uuid.UUID] = Query(None),
    user_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    service = TimeEntryService(db, membership.agency_id)
    return await service.list_time_entries(
        role=membership.role,
        client_id=membership.client_id,
        project_id=project_id,
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get("/project/{project_id}/total-hours", response_model=ProjectTotalHoursResponse)
async def get_project_total_hours(
    project_id: uuid.UUID,
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    service = TimeEntryService(db, membership.agency_id)
    total_hours = await service.get_project_total_hours(project_id)
    return ProjectTotalHoursResponse(project_id=project_id, total_hours=total_hours)


@router.patch("/{entry_id}", response_model=TimeEntryResponse)
async def update_time_entry(
    entry_id: uuid.UUID,
    data: TimeEntryUpdate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    service = TimeEntryService(db, membership.agency_id)
    return await service.update_entry(entry_id, current_user.id, data, membership.role)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    service = TimeEntryService(db, membership.agency_id)
    await service.delete_entry(entry_id, current_user.id, membership.role)
    return None
