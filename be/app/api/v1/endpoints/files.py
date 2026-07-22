import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, get_db
from app.models.user import User
from app.models.membership import AgencyMembership
from app.schemas.task_file import FileApprovalUpdate, FileResponse
from app.services.file_service import FileService

router = APIRouter()


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    task_id: uuid.UUID = Form(...),
    is_internal: bool = Form(False),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    file_service = FileService(db, membership.agency_id)
    return await file_service.upload_file(
        uploader_id=current_user.id,
        task_id=task_id,
        file=file,
        is_internal=is_internal,
        role=membership.role,
        client_id=membership.client_id
    )


@router.get("/task/{task_id}", response_model=List[FileResponse])
async def list_task_files(
    task_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    file_service = FileService(db, membership.agency_id)
    return await file_service.list_task_files(
        task_id=task_id,
        role=membership.role,
        client_id=membership.client_id,
        skip=skip,
        limit=limit
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    file_service = FileService(db, membership.agency_id)
    file_meta = await file_service.get_file_metadata(file_id, membership.role)
    if not os.path.exists(file_meta.file_path):
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Physical file not found on server storage")

    return FastAPIFileResponse(
        path=file_meta.file_path,
        filename=file_meta.filename,
        media_type=file_meta.content_type
    )


@router.patch("/{file_id}/approve", response_model=FileResponse)
async def update_file_approval(
    file_id: uuid.UUID,
    data: FileApprovalUpdate,
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    file_service = FileService(db, membership.agency_id)
    return await file_service.update_approval_status(file_id, data.approval_status, membership.role)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    file_service = FileService(db, membership.agency_id)
    await file_service.delete_file(file_id, current_user.id, membership.role)
    return None
