from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status

from app.core.providers import get_user_service
from app.core.security import require_role
from app.models.user import UserCreate, UserOut
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserOut])
def list_users(service: UserService = Depends(get_user_service)) -> List[UserOut]:
    return service.list_all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int, service: UserService = Depends(get_user_service)
) -> UserOut:
    return service.get_by_id(user_id)


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def create_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserOut:
    return service.create(payload)
