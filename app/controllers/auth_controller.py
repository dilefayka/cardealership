from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.security import authenticate

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["admin123"])


class LoginResponse(BaseModel):
    token: str
    role: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    token, role = authenticate(payload.username, payload.password)
    return LoginResponse(token=token, role=role)
