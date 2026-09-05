from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.organization import MembershipOut


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class UserMeOut(UserOut):
    """Returned from GET /auth/me — includes every organization the user belongs to."""

    memberships: list[MembershipOut] = []
