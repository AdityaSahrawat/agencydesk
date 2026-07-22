import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agency import Agency
    from app.models.membership import AgencyMembership
    from app.models.project import Project


class Client(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "clients"

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    agency: Mapped["Agency"] = relationship("Agency", back_populates="clients")
    memberships: Mapped[List["AgencyMembership"]] = relationship("AgencyMembership", back_populates="client")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="client", cascade="all, delete-orphan")
