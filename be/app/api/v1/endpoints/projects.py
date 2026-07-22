import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, require_role, get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectMemberAssign,
    ProjectResponse,
    ProjectUpdate
)
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    return await project_service.create_project(current_user.id, data)


@router.get("/", response_model=List[ProjectResponse])
@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    return await project_service.list_projects(
        user_id=current_user.id,
        role=membership.role,
        client_id=membership.client_id,
        skip=skip,
        limit=limit
    )


@router.get("/search", response_model=List[ProjectResponse])
async def search_projects(
    q: str = Query(..., min_length=1),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    return await project_service.search_projects(q, membership.role, membership.client_id)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    p = await project_service.get_project(
        project_id=project_id,
        role=membership.role,
        client_id=membership.client_id,
        user_id=current_user.id
    )
    members_users = [pm.user for pm in p.members if pm.user]
    return ProjectDetailResponse(
        id=p.id,
        agency_id=p.agency_id,
        client_id=p.client_id,
        name=p.name,
        description=p.description,
        status=p.status,
        created_by=p.created_by,
        created_at=p.created_at,
        updated_at=p.updated_at,
        client=p.client,
        members=members_users
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    return await project_service.update_project(project_id, data, membership.role, membership.client_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    await project_service.delete_project(project_id, membership.role)
    return None


@router.post("/{project_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def assign_project_members(
    project_id: uuid.UUID,
    data: ProjectMemberAssign,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db, membership.agency_id)
    await project_service.assign_members(project_id, data.user_ids, membership.role)
    return None
