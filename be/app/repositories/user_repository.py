import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email.ilike(email))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_user(self, email: str, hashed_password: str, full_name: str) -> User:
        user = User(email=email.lower(), hashed_password=hashed_password, full_name=full_name)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user(self, user: User, **kwargs) -> User:
        for k, v in kwargs.items():
            if v is not None and hasattr(user, k):
                setattr(user, k, v)
        await self.db.flush()
        await self.db.refresh(user)
        return user
