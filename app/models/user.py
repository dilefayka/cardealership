from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):

    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Валидный адрес электронной почты")
    age: Optional[int] = Field(
        default=None, ge=0, le=150, description="Возраст (необязательное поле)"
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name не должно быть пустым")
        return cleaned


class UserCreate(UserBase):
    pass


class UserOut(UserBase):

    id: int = Field(..., description="Уникальный идентификатор")
