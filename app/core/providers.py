from __future__ import annotations

from app.services.car_service import CarService
from app.services.user_service import UserService


_user_service = UserService()
_car_service = CarService()


def get_user_service() -> UserService:
    return _user_service


def get_car_service() -> CarService:
    return _car_service
