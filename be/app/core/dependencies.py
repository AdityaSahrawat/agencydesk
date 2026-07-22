import logging
import uuid
from typing import List, Optional
from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.config import settings
from app.core.exceptions import ForbiddenException, UnauthorizedException, NotFoundException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.models.membership import AgencyMembership, RoleEnum
from app.repositories.user_repository import UserRepository
from app.repositories.agency_repository import AgencyRepository

logger = logging.getLogger("agencydesk.auth")
logging.basicConfig(level=logging.INFO)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    auth_header = request.headers.get("Authorization")
    path = request.url.path
    logger.info(f"🔑 Auth Check -> Path: {path} | Auth Header Present: {bool(auth_header)} | Token: {token[:15] if token else 'NONE'}")

    if not token:
        logger.warning(f"❌ Auth Failed: Token missing for path {path}")
        raise UnauthorizedException("Authentication token required")

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            logger.warning(f"❌ Auth Failed: Invalid token type for path {path}")
            raise UnauthorizedException("Invalid token type")

        user_id_str: str = payload.get("sub")
        if not user_id_str:
            logger.warning(f"❌ Auth Failed: Invalid token subject for path {path}")
            raise UnauthorizedException("Invalid token subject")

        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError) as e:
        logger.warning(f"❌ Auth Failed: JWT decode error ({str(e)}) for path {path}")
        raise UnauthorizedException("Invalid or expired authentication token")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        logger.warning(f"❌ Auth Failed: User inactive or not found ({user_id}) for path {path}")
        raise UnauthorizedException("User account is inactive or non-existent")

    return user


async def get_tenant_membership(
    x_agency_id: Optional[str] = Header(None, alias="X-Agency-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AgencyMembership:
    logger.info(f"🏢 Tenant Check -> User: {current_user.email} | X-Agency-ID Header: {x_agency_id}")
    agency_repo = AgencyRepository(db)
    memberships = await agency_repo.get_user_memberships(current_user.id)

    if not memberships:
        logger.warning(f"❌ Tenant Failed: No memberships for user {current_user.email}")
        raise ForbiddenException("User is not associated with any active agency")

    selected_agency_id: Optional[uuid.UUID] = None

    if x_agency_id:
        try:
            selected_agency_id = uuid.UUID(x_agency_id)
        except ValueError:
            logger.warning(f"❌ Tenant Failed: Invalid UUID format for X-Agency-ID ({x_agency_id})")
            raise ForbiddenException("Invalid X-Agency-ID header format")
    elif len(memberships) == 1:
        selected_agency_id = memberships[0].agency_id
    else:
        # User has multiple agencies; default to first membership
        selected_agency_id = memberships[0].agency_id

    # Find matching membership for the selected agency
    matching = next((m for m in memberships if m.agency_id == selected_agency_id), None)
    if not matching:
        logger.warning(f"❌ Tenant Failed: User {current_user.email} has no membership in agency {selected_agency_id}")
        raise ForbiddenException("Access denied: You do not have an active membership in this agency")

    return matching


def require_role(allowed_roles: List[RoleEnum]):
    async def role_checker(membership: AgencyMembership = Depends(get_tenant_membership)) -> AgencyMembership:
        if membership.role not in allowed_roles:
            logger.warning(f"❌ Role Failed: Role '{membership.role.value}' not in allowed roles {[r.value for r in allowed_roles]}")
            raise ForbiddenException(f"Role '{membership.role.value}' is not authorized to perform this operation")
        return membership
    return role_checker
