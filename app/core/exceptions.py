from __future__ import annotations


class AppException(Exception):

    status_code: int = 400
    code: str = "app_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(AppException):

    status_code = 404
    code = "not_found"


class DuplicateEmailError(AppException):

    status_code = 409
    code = "duplicate_email"


class AuthenticationError(AppException):

    status_code = 401
    code = "unauthorized"


class AuthorizationError(AppException):

    status_code = 403
    code = "forbidden"
