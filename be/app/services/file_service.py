import os
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.task_file import TaskFile, FileApprovalStatus
from app.models.membership import RoleEnum
from app.repositories.file_repository import TaskFileRepository
from app.repositories.task_repository import TaskRepository


class FileService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.file_repo = TaskFileRepository(db, agency_id)
        self.task_repo = TaskRepository(db, agency_id)

    async def upload_file(
        self,
        uploader_id: uuid.UUID,
        task_id: uuid.UUID,
        file: UploadFile,
        is_internal: bool,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> TaskFile:
        task = await self.task_repo.get_task_by_id(task_id, role, client_id)
        if not task:
            raise NotFoundException("Task not found or access forbidden")

        if role == RoleEnum.CLIENT_USER:
            is_internal = False  # Client uploaded files cannot be internal

        file_id = uuid.uuid4()
        task_dir = os.path.join(settings.UPLOAD_DIR, str(self.agency_id), str(task_id))
        os.makedirs(task_dir, exist_ok=True)

        safe_filename = file.filename or "uploaded_file"
        disk_path = os.path.join(task_dir, f"{file_id}_{safe_filename}")

        contents = await file.read()
        file_size = len(contents)
        with open(disk_path, "wb") as f:
            f.write(contents)

        return await self.file_repo.create(
            id=file_id,
            task_id=task_id,
            uploaded_by=uploader_id,
            filename=safe_filename,
            file_path=disk_path,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            is_internal=is_internal,
            approval_status=FileApprovalStatus.PENDING
        )

    async def list_task_files(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskFile]:
        task = await self.task_repo.get_task_by_id(task_id, role, client_id)
        if not task:
            raise NotFoundException("Task not found or access forbidden")
        return await self.file_repo.list_for_task(task_id, role, skip=skip, limit=limit)

    async def get_file_metadata(self, file_id: uuid.UUID, role: RoleEnum) -> TaskFile:
        task_file = await self.file_repo.get_file(file_id, role)
        if not task_file:
            raise NotFoundException("File not found or access forbidden")
        return task_file

    async def update_approval_status(
        self,
        file_id: uuid.UUID,
        status: FileApprovalStatus,
        role: RoleEnum
    ) -> TaskFile:
        task_file = await self.file_repo.get_file(file_id, role)
        if not task_file:
            raise NotFoundException("File not found")
        return await self.file_repo.update_approval(task_file, status)

    async def delete_file(self, file_id: uuid.UUID, user_id: uuid.UUID, role: RoleEnum) -> None:
        task_file = await self.file_repo.get_file(file_id, role)
        if not task_file:
            raise NotFoundException("File not found")
        if task_file.uploaded_by != user_id and role != RoleEnum.AGENCY_ADMIN:
            raise ForbiddenException("You do not have permission to delete this file")

        await self.file_repo.soft_delete(task_file)
        if os.path.exists(task_file.file_path):
            try:
                os.remove(task_file.file_path)
            except OSError:
                pass
