import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.task_file import TaskFile, FileApprovalStatus
from app.models.membership import RoleEnum
from app.repositories.base import BaseTenantRepository


class TaskFileRepository(BaseTenantRepository[TaskFile]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(TaskFile, db, agency_id)

    async def list_for_task(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskFile]:
        query = self._base_query().where(TaskFile.task_id == task_id).options(selectinload(TaskFile.uploader))

        if role == RoleEnum.CLIENT_USER:
            query = query.where(TaskFile.is_internal == False)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_file(self, file_id: uuid.UUID, role: RoleEnum) -> Optional[TaskFile]:
        query = self._base_query().where(TaskFile.id == file_id).options(selectinload(TaskFile.uploader))
        if role == RoleEnum.CLIENT_USER:
            query = query.where(TaskFile.is_internal == False)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_approval(self, file: TaskFile, status: FileApprovalStatus) -> TaskFile:
        file.approval_status = status
        await self.db.flush()
        await self.db.refresh(file)
        return file
