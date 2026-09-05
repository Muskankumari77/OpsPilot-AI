"""
Organization and OrganizationMember models.

Multi-tenancy in OpsPilot works like this: every business-data table (sales,
inventory, customers, etc., added from Phase 4 onward) carries an
`organization_id`. A user's access to that data is determined by whether
they have an OrganizationMember row for that organization, and what role
it grants.

Roles are kept to three, matching the lean-build decision:
  - admin:   manage organization, manage users, upload data, configure AI
  - manager: view analytics, generate reports, use Copilot, create actions
  - viewer:  read-only access
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    members = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )


class OrganizationMember(Base):
    """Join table linking a User to an Organization with a Role."""

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.VIEWER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="members")
