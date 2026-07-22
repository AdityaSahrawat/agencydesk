import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.membership import RoleEnum

if TYPE_CHECKING:
    from app.models.agency import Agency
    from app.models.client import Client
    from app.models.user import User


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invitation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invitations"

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, native_enum=False), nullable=False)
    client_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus, native_enum=False),
        default=InvitationStatus.PENDING,
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    agency: Mapped["Agency"] = relationship("Agency")
    client: Mapped[Optional["Client"]] = relationship("Client")
    creator: Mapped[Optional["User"]] = relationship("User")
