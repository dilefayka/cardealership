from __future__ import annotations

from itertools import count
from typing import List, Optional

from app.core.exceptions import EntityNotFoundError
from app.decorators.audit import audit
from app.models.car import CarCreate, CarOut


class CarService:

    def __init__(self) -> None:
        self._items: List[CarOut] = []
        self._id_seq = count(start=1)

    @audit("car.list")
    def list_all(
        self, brand: Optional[str] = None, max_price: Optional[float] = None
    ) -> List[CarOut]:
        result = list(self._items)
        if brand:
            needle = brand.strip().lower()
            result = [c for c in result if c.brand.lower() == needle]
        if max_price is not None:
            result = [c for c in result if c.price <= max_price]
        return result

    @audit("car.get")
    def get_by_id(self, car_id: int) -> CarOut:
        for item in self._items:
            if item.id == car_id:
                return item
        raise EntityNotFoundError(f"Автомобиль с id={car_id} не найден")

    @audit("car.create")
    def create(self, payload: CarCreate) -> CarOut:
        car = CarOut(id=next(self._id_seq), **payload.model_dump())
        self._items.append(car)
        return car

    @audit("car.delete")
    def delete(self, car_id: int) -> None:
        for index, item in enumerate(self._items):
            if item.id == car_id:
                del self._items[index]
                return
        raise EntityNotFoundError(f"Автомобиль с id={car_id} не найден")

    def seed(self, payloads: List[CarCreate]) -> None:
        for payload in payloads:
            self.create(payload)
