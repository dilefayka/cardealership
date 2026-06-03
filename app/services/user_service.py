from __future__ import annotations

from itertools import count
from typing import List

from app.core.exceptions import DuplicateEmailError, EntityNotFoundError
from app.decorators.audit import audit
from app.models.user import UserCreate, UserOut


class UserService:

    def __init__(self) -> None:
        self._items: List[UserOut] = []
        self._id_seq = count(start=1)

    @audit("user.list")
    def list_all(self) -> List[UserOut]:
        return list(self._items)

    @audit("user.get")
    def get_by_id(self, user_id: int) -> UserOut:
        for item in self._items:
            if item.id == user_id:
                return item
        raise EntityNotFoundError(f"Пользователь с id={user_id} не найден")

    @audit("user.create")
    def create(self, payload: UserCreate) -> UserOut:
        normalized = payload.email.lower()
        for item in self._items:
            if item.email.lower() == normalized:
                raise DuplicateEmailError(
                    f"Пользователь с email {payload.email} уже существует"
                )
        user = UserOut(id=next(self._id_seq), **payload.model_dump())
        self._items.append(user)
        return user

    def seed(self, payloads: List[UserCreate]) -> None:
        for payload in payloads:
            try:
                self.create(payload)
            except DuplicateEmailError:
                continue
