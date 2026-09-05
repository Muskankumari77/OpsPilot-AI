"""
Auth routes: register, login, and "who am I" (with organization memberships).

Thin by design — validation happens via the Pydantic schemas, business
logic lives in services/auth_service.py.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserMeOut
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    _, token = auth_service.register_user(db, payload)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    _, token = auth_service.authenticate_user(db, payload)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserMeOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
