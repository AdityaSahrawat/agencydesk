import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.membership import AgencyMembership
    from app.models.client import Client
    from app.models.project import Project


class Agency(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agencies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[List["AgencyMembership"]] = relationship("AgencyMembership", back_populates="agency", cascade="all, delete-orphan")
    clients: Mapped[List["Client"]] = relationship("Client", back_populates="agency", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="agency", cascade="all, delete-orphan")
