import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_membership, require_role, get_db
from app.models.membership import AgencyMembership, RoleEnum
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    client_service = ClientService(db, membership.agency_id)
    return await client_service.create_client(data)


@router.get("/", response_model=List[ClientResponse])
@router.get("", response_model=List[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    client_service = ClientService(db, membership.agency_id)
    return await client_service.list_clients(
        role=membership.role,
        user_client_id=membership.client_id,
        skip=skip,
        limit=limit
    )


@router.get("/search", response_model=List[ClientResponse])
async def search_clients(
    q: str = Query(..., min_length=1),
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN, RoleEnum.AGENCY_MEMBER])),
    db: AsyncSession = Depends(get_db)
):
    client_service = ClientService(db, membership.agency_id)
    return await client_service.search_clients(q)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: uuid.UUID,
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    client_service = ClientService(db, membership.agency_id)
    return await client_service.get_client(client_id, membership.role, membership.client_id)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    data: ClientUpdate,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    client_service = ClientService(db, membership.agency_id)
    return await client_service.update_client(client_id, data)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    membership: AgencyMembership = Depends(require_role([RoleEnum.AGENCY_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    client_service = ClientService(db, membership.agency_id)
    await client_service.delete_client(client_id)
    return None
