from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token
)
from app.services.auth_service import AuthService
from app.services.agency_service import AgencyService
from app.schemas.user import UserWithMembershipsResponse, UserMembershipInfo

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    _, token = await auth_service.register(req)
    return token


@router.post("/login", response_model=Token)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    _, token = await auth_service.login(req.email, req.password)
    return token


@router.post("/refresh", response_model=Token)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(req.refresh_token)


@router.get("/me", response_model=UserWithMembershipsResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    agency_service = AgencyService(db)
    agencies_with_memberships = await agency_service.list_user_agencies(current_user.id)

    membership_infos = []
    for agency, m in agencies_with_memberships:
        membership_infos.append(
            UserMembershipInfo(
                agency_id=agency.id,
                agency_name=agency.name,
                role=m.role,
                client_id=m.client_id
            )
        )

    return UserWithMembershipsResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        memberships=membership_infos
    )
