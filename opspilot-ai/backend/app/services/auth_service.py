"""
Auth service — registration and login logic.

Kept out of the route handlers so api/v1/auth.py stays a thin HTTP layer:
parse request, call service, return response.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.organization import Organization, OrganizationMember, Role
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> tuple[User, str]:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise ValidationError("An account with this email already exists.")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()  # assigns user.id without committing yet

    organization = Organization(name=payload.organization_name)
    db.add(organization)
    db.flush()

    membership = OrganizationMember(
        user_id=user.id,
        organization_id=organization.id,
        role=Role.ADMIN,  # creator of an organization is always its admin
    )
    db.add(membership)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return user, token


def authenticate_user(db: Session, payload: LoginRequest) -> tuple[User, str]:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password.")
    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated.")

    token = create_access_token({"sub": str(user.id)})
    return user, token
