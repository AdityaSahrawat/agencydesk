import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException, NotFoundException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from app.models.membership import RoleEnum
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.agency_repository import AgencyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, Token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.agency_repo = AgencyRepository(db)

    async def register(self, req: RegisterRequest) -> Tuple[User, Token]:
        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise ConflictException("A user with this email address already exists")

        hashed_pw = get_password_hash(req.password)
        user = await self.user_repo.create_user(
            email=req.email,
            hashed_password=hashed_pw,
            full_name=req.full_name
        )

        # If agency name provided, automatically provision initial agency & admin membership
        if req.agency_name:
            slug = req.agency_name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:6]
            agency = await self.agency_repo.create_agency(name=req.agency_name, slug=slug)
            await self.agency_repo.add_membership(
                agency_id=agency.id,
                user_id=user.id,
                role=RoleEnum.AGENCY_ADMIN
            )

        token = await self.create_user_tokens(user.id)
        return user, token

    async def login(self, email: str, password: str) -> Tuple[User, Token]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("User account is deactivated")

        token = await self.create_user_tokens(user.id)
        return user, token

    async def create_user_tokens(self, user_id: uuid.UUID) -> Token:
        access_token = create_access_token(subject=str(user_id))
        refresh_token = create_refresh_token(subject=str(user_id))

        # Pass SHA-256 digest hex string to bcrypt to respect 72-byte max length limit
        rf_digest = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
        rf_hash = get_password_hash(rf_digest)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        rf = RefreshToken(
            user_id=user_id,
            token_hash=rf_hash,
            expires_at=expires_at,
            is_revoked=False
        )
        self.db.add(rf)
        await self.db.flush()

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token_str: str) -> Token:
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            user_id = uuid.UUID(payload.get("sub"))
        except Exception:
            raise UnauthorizedException("Invalid or expired refresh token")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User account is inactive or invalid")

        return await self.create_user_tokens(user.id)
