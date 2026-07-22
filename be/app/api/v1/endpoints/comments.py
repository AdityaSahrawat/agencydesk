import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, get_db
from app.models.user import User
from app.models.membership import AgencyMembership
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment_service import CommentService

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    comment_service = CommentService(db, membership.agency_id)
    return await comment_service.create_comment(current_user.id, data, membership.role, membership.client_id)


@router.get("/task/{task_id}", response_model=List[CommentResponse])
async def list_task_comments(
    task_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    comment_service = CommentService(db, membership.agency_id)
    return await comment_service.list_task_comments(
        task_id=task_id,
        role=membership.role,
        client_id=membership.client_id,
        skip=skip,
        limit=limit
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: uuid.UUID,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    comment_service = CommentService(db, membership.agency_id)
    return await comment_service.update_comment(comment_id, current_user.id, data, membership.role)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    comment_service = CommentService(db, membership.agency_id)
    await comment_service.delete_comment(comment_id, current_user.id, membership.role)
    return None
