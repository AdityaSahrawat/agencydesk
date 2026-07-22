import enum
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agency import Agency
    from app.models.user import User
    from app.models.client import Client


class RoleEnum(str, enum.Enum):
    AGENCY_ADMIN = "agency_admin"
    AGENCY_MEMBER = "agency_member"
    CLIENT_USER = "client_user"


class AgencyMembership(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agency_memberships"
    __table_args__ = (
        UniqueConstraint("agency_id", "user_id", name="uq_agency_user_membership"),
    )

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, native_enum=False), nullable=False)
    client_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    agency: Mapped["Agency"] = relationship("Agency", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    client: Mapped[Optional["Client"]] = relationship("Client", back_populates="memberships")
