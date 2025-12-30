"""Зависимости FastAPI: построение клиента kworkapi из токена запроса.

Сервис стателесс: на каждый запрос создаётся свой KworkClient (свой httpx-пул),
который закрывается по завершении. `uad` сервиса стабилен в пределах процесса —
авторизованным вызовам этого достаточно (вход — отдельный кейс).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Header, HTTPException

from kworkapi import KworkClient
from kworkapi._device import generate_uad
from kworkapi.auth import Session

# Стабильный идентификатор установки на время жизни процесса сервиса.
SERVICE_UAD = generate_uad()


async def get_client(
    x_kwork_token: Annotated[str | None, Header(alias="X-Kwork-Token")] = None,
) -> AsyncIterator[KworkClient]:
    """Клиент для авторизованных эндпоинтов: токен из заголовка X-Kwork-Token."""
    if not x_kwork_token:
        raise HTTPException(status_code=401, detail="Нужен заголовок X-Kwork-Token")
    client = KworkClient(session=Session(token=x_kwork_token, uad=SERVICE_UAD))
    try:
        yield client
    finally:
        await client.aclose()


async def get_anon_client() -> AsyncIterator[KworkClient]:
    """Клиент без токена — для логина."""
    client = KworkClient(uad=SERVICE_UAD)
    try:
        yield client
    finally:
        await client.aclose()
