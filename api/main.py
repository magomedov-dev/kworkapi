"""Точка входа FastAPI-сервиса.

Запуск:  uvicorn api.main:app --reload
Доки:    http://127.0.0.1:8000/docs

Авторизация: получите токен через POST /auth/login, затем передавайте его в
заголовке `X-Kwork-Token` остальным эндпоинтам.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routers import account, auth, catalog, exchange, kworks, messages, orders, search, users
from kworkapi.exceptions import (
    KworkAPIError,
    KworkAuthError,
    KworkError,
    KworkRateLimitError,
)

app = FastAPI(
    title="KworkAPI",
    description=(
        "Неофициальный REST поверх приватного API kwork.ru. "
        "Авторизуйтесь через /auth/login и передавайте токен в заголовке X-Kwork-Token."
    ),
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(account.router)
app.include_router(catalog.router)
app.include_router(search.router)
app.include_router(exchange.router)
app.include_router(users.router)
app.include_router(kworks.router)
app.include_router(orders.router)
app.include_router(messages.router)


@app.get("/health", tags=["service"])
async def health() -> dict:
    return {"status": "ok"}


# --- маппинг ошибок библиотеки в HTTP -------------------------------------


def _error_body(exc: KworkError) -> dict:
    code = getattr(exc, "code", None)
    return {"error": str(exc), "code": code}


@app.exception_handler(KworkAuthError)
async def _auth_error(request: Request, exc: KworkAuthError) -> JSONResponse:
    return JSONResponse(status_code=401, content=_error_body(exc))


@app.exception_handler(KworkRateLimitError)
async def _rate_error(request: Request, exc: KworkRateLimitError) -> JSONResponse:
    return JSONResponse(status_code=429, content=_error_body(exc))


@app.exception_handler(KworkAPIError)
async def _api_error(request: Request, exc: KworkAPIError) -> JSONResponse:
    # ошибка вышестоящего API kwork
    return JSONResponse(status_code=502, content=_error_body(exc))


@app.exception_handler(KworkError)
async def _generic_error(request: Request, exc: KworkError) -> JSONResponse:
    return JSONResponse(status_code=500, content=_error_body(exc))
