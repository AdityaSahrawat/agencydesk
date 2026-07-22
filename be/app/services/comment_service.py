import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.comment import Comment
from app.models.membership import RoleEnum
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.comment_repo = CommentRepository(db, agency_id)
        self.task_repo = TaskRepository(db, agency_id)

    async def create_comment(
        self,
        author_id: uuid.UUID,
        data: CommentCreate,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> Comment:
        task = await self.task_repo.get_task_by_id(data.task_id, role, client_id)
        if not task:
            raise NotFoundException("Task not found or access forbidden")

        is_internal = data.is_internal
        if role == RoleEnum.CLIENT_USER:
            is_internal = False  # Client users can never post internal comments!

        return await self.comment_repo.create(
            task_id=data.task_id,
            user_id=author_id,
            content=data.content,
            is_internal=is_internal
        )

    async def list_task_comments(
        self,
        task_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        task = await self.task_repo.get_task_by_id(task_id, role, client_id)
        if not task:
            raise NotFoundException("Task not found or access forbidden")
        return await self.comment_repo.list_for_task(task_id, role, skip=skip, limit=limit)

    async def update_comment(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CommentUpdate,
        role: RoleEnum
    ) -> Comment:
        comment = await self.comment_repo.get_comment(comment_id, role)
        if not comment:
            raise NotFoundException("Comment not found")
        if comment.user_id != user_id and role != RoleEnum.AGENCY_ADMIN:
            raise ForbiddenException("You can only edit your own comments")

        is_internal = comment.is_internal
        if data.is_internal is not None and role != RoleEnum.CLIENT_USER:
            is_internal = data.is_internal

        return await self.comment_repo.update(
            comment,
            content=data.content,
            is_internal=is_internal
        )

    async def delete_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID, role: RoleEnum) -> None:
        comment = await self.comment_repo.get_comment(comment_id, role)
        if not comment:
            raise NotFoundException("Comment not found")
        if comment.user_id != user_id and role != RoleEnum.AGENCY_ADMIN:
            raise ForbiddenException("You can only delete your own comments")

        await self.comment_repo.soft_delete(comment)
