"""
Auth request/response schemas.

RegisterRequest creates a user AND their first organization in one step —
matching how most SaaS onboarding actually works ("sign up, name your
workspace"). Joining an existing organization is invite-based and comes
later; not needed for the lean build.
"""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
