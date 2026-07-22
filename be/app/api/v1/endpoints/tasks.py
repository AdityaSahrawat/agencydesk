import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, require_role, get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.models.task import TaskStatus
from app.schemas.task import (
    TaskAssignUpdate,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate
)
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    return await task_service.create_task(current_user.id, data, membership.role)


@router.get("/", response_model=List[TaskResponse])
@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    project_id: Optional[uuid.UUID] = Query(None),
    assigned_to: Optional[uuid.UUID] = Query(None),
    task_status: Optional[TaskStatus] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    return await task_service.list_tasks(
        role=membership.role,
        client_id=membership.client_id,
        project_id=project_id,
        assigned_to=assigned_to,
        status=task_status,
        search_query=search,
        skip=skip,
        limit=limit
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    return await task_service.get_task(task_id, membership.role, membership.client_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    return await task_service.update_task(task_id, data, membership.role, membership.client_id)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: uuid.UUID,
    data: TaskStatusUpdate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    return await task_service.update_status(task_id, data, membership.role, membership.client_id)


@router.patch("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: uuid.UUID,
    data: TaskAssignUpdate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    return await task_service.assign_user(task_id, data, membership.role, membership.client_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db, membership.agency_id)
    await task_service.delete_task(task_id, membership.role, membership.client_id)
    return None
