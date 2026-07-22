import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.comment import Comment
from app.models.membership import RoleEnum
from app.repositories.base import BaseTenantRepository


class CommentRepository(BaseTenantRepository[Comment]):
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        super().__init__(Comment, db, agency_id)

    async def list_for_task(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        query = self._base_query().where(Comment.task_id == task_id).options(selectinload(Comment.author))

        if role == RoleEnum.CLIENT_USER:
            query = query.where(Comment.is_internal == False)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_comment(self, comment_id: uuid.UUID, role: RoleEnum) -> Optional[Comment]:
        query = self._base_query().where(Comment.id == comment_id).options(selectinload(Comment.author))
        if role == RoleEnum.CLIENT_USER:
            query = query.where(Comment.is_internal == False)
        result = await self.db.execute(query)
        return result.scalars().first()
