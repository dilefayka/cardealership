from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BodyType(str, Enum):

    sedan = "sedan"
    hatchback = "hatchback"
    suv = "suv"
    coupe = "coupe"
    wagon = "wagon"


class CarBase(BaseModel):

    brand: str = Field(..., min_length=1, max_length=50, description="Марка")
    model: str = Field(..., min_length=1, max_length=50, description="Модель")
    year: int = Field(..., ge=1950, le=2030, description="Год выпуска")
    price: float = Field(..., gt=0, description="Цена в рублях")
    body_type: BodyType = Field(default=BodyType.sedan, description="Тип кузова")
    in_stock: bool = Field(default=True, description="Наличие на складе")

    @field_validator("brand", "model")
    @classmethod
    def strip_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("поле не должно быть пустым")
        return cleaned


class CarCreate(CarBase):
    pass


class CarOut(CarBase):

    id: int = Field(..., description="Уникальный идентификатор")
