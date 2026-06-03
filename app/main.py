from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.controllers import auth_controller, car_controller, user_controller
from app.core.exceptions import AppException
from app.core.providers import get_car_service, get_user_service
from app.models.car import BodyType, CarCreate
from app.models.user import UserCreate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


def _seed_data() -> None:
    get_user_service().seed(
        [
            UserCreate(name="Иван Петров", email="ivan@example.com", age=34),
            UserCreate(name="Анна Смирнова", email="anna@example.com", age=29),
        ]
    )
    get_car_service().seed(
        [
            CarCreate(brand="Toyota", model="Camry", year=2023, price=3200000,
                      body_type=BodyType.sedan, in_stock=True),
            CarCreate(brand="Kia", model="Sportage", year=2022, price=2750000,
                      body_type=BodyType.suv, in_stock=True),
            CarCreate(brand="BMW", model="320i", year=2024, price=4500000,
                      body_type=BodyType.sedan, in_stock=False),
        ]
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    _seed_data()
    yield


app = FastAPI(
    title="Автосалон",
    description="Стек: Python + FastAPI + Pydantic.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(AppException)
def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(p) for p in err.get("loc", [])),
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Данные не прошли валидацию",
                "details": details,
            }
        },
    )


app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(car_controller.router)


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))
