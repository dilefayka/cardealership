from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.providers import get_car_service
from app.core.security import require_role
from app.models.car import CarCreate, CarOut
from app.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("", response_model=List[CarOut])
def list_cars(
    brand: Optional[str] = Query(default=None, description="Фильтр по марке"),
    max_price: Optional[float] = Query(default=None, gt=0, description="Макс. цена"),
    service: CarService = Depends(get_car_service),
) -> List[CarOut]:
    return service.list_all(brand=brand, max_price=max_price)


@router.get("/{car_id}", response_model=CarOut)
def get_car(car_id: int, service: CarService = Depends(get_car_service)) -> CarOut:
    return service.get_by_id(car_id)


@router.post(
    "",
    response_model=CarOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def create_car(
    payload: CarCreate, service: CarService = Depends(get_car_service)
) -> CarOut:
    return service.create(payload)


@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_car(car_id: int, service: CarService = Depends(get_car_service)) -> Response:
    service.delete(car_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
