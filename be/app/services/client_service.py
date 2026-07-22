import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.client import Client
from app.models.membership import RoleEnum
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.client_repo = ClientRepository(db, agency_id)

    async def create_client(self, data: ClientCreate) -> Client:
        return await self.client_repo.create(
            name=data.name,
            company_name=data.company_name,
            email=data.email,
            phone=data.phone
        )

    async def get_client(self, client_id: uuid.UUID, role: RoleEnum, user_client_id: Optional[uuid.UUID] = None) -> Client:
        if role == RoleEnum.CLIENT_USER and user_client_id != client_id:
            raise ForbiddenException("Access denied: You can only view your own client company details")
        client = await self.client_repo.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client not found")
        return client

    async def list_clients(
        self,
        role: RoleEnum,
        user_client_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        if role == RoleEnum.CLIENT_USER:
            if not user_client_id:
                return []
            c = await self.client_repo.get_by_id(user_client_id)
            return [c] if c else []
        return await self.client_repo.list_all(skip=skip, limit=limit)

    async def update_client(self, client_id: uuid.UUID, data: ClientUpdate) -> Client:
        client = await self.client_repo.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client not found")
        return await self.client_repo.update(
            client,
            name=data.name,
            company_name=data.company_name,
            email=data.email,
            phone=data.phone
        )

    async def delete_client(self, client_id: uuid.UUID) -> None:
        client = await self.client_repo.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client not found")
        await self.client_repo.soft_delete(client)

    async def search_clients(self, query_str: str) -> List[Client]:
        return await self.client_repo.search(query_str)
