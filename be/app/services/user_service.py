import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.user import User
from app.models.membership import AgencyMembership
from app.repositories.user_repository import UserRepository
from app.repositories.agency_repository import AgencyRepository
from app.repositories.task_repository import TaskRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.agency_repo = AgencyRepository(db)

    async def remove_agency_member(self, agency_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Edge Case: Member removed policy - deactivate membership and unassign active tasks."""
        membership = await self.agency_repo.get_membership(agency_id, user_id)
        if not membership:
            raise NotFoundException("Member not found in agency")

        membership.is_active = False
        await self.db.flush()

        # Unassign active tasks
        task_repo = TaskRepository(self.db, agency_id)
        await task_repo.unassign_user_tasks(user_id)

    async def get_user_profile(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user
