from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Dict

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationError, AuthorizationError


@dataclass(frozen=True)
class Account:

    username: str
    password: str
    role: str


_ACCOUNTS: Dict[str, Account] = {
    "admin": Account(username="admin", password="admin123", role="admin"),
    "guest": Account(username="guest", password="guest123", role="guest"),
}


_TOKENS: Dict[str, str] = {}


_bearer = HTTPBearer(auto_error=False)


def authenticate(username: str, password: str) -> tuple[str, str]:
    account = _ACCOUNTS.get(username)
    if account is None or not secrets.compare_digest(account.password, password):
        raise AuthenticationError("Неверный логин или пароль")
    token = secrets.token_urlsafe(24)
    _TOKENS[token] = account.role
    return token, account.role


def get_current_role(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    if credentials is None:
        raise AuthenticationError("Требуется авторизация (Bearer-токен)")
    role = _TOKENS.get(credentials.credentials)
    if role is None:
        raise AuthenticationError("Недействительный токен")
    return role


def require_role(*allowed_roles: str):

    def dependency(role: str = Depends(get_current_role)) -> str:
        if role not in allowed_roles:
            raise AuthorizationError(
                f"Недостаточно прав: требуется одна из ролей {allowed_roles}"
            )
        return role
    return dependency
