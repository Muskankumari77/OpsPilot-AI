from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.organization import Role


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class MembershipOut(BaseModel):
    """An organization the current user belongs to, plus their role in it."""

    model_config = ConfigDict(from_attributes=True)

    organization: OrganizationOut
    role: Role
