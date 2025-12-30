"""REST: аккаунт."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api._serialize import dump
from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/me")
async def me(client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Профиль и состояние текущего пользователя."""
    return dump(await client.account.me())


@router.get("/notifications")
async def notifications(
    client: Annotated[KworkClient, Depends(get_client)], page: int = 1
) -> dict:
    """Лента уведомлений."""
    return await client.account.notifications(page=page)


@router.get("/payment-methods")
async def payment_methods(client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Способы оплаты и комиссии."""
    return await client.account.payment_methods()


class UpdateSettingsRequest(BaseModel):
    username: str
    fullname: str = ""
    email: str = ""
    timezone_id: int | None = None
    country_id: int | None = None
    city_id: int | None = None
    details: str = ""
    profession: str = ""


@router.post("/settings")
async def update_settings(
    body: UpdateSettingsRequest,
    client: Annotated[KworkClient, Depends(get_client)],
) -> dict:
    """Сохранить настройки профиля."""
    return await client.account.update_settings(**body.model_dump())


@router.post("/taking-orders")
async def set_taking_orders(
    status: str, client: Annotated[KworkClient, Depends(get_client)]
) -> dict:
    """Включить/выключить приём заказов."""
    return await client.account.set_taking_orders(status)
