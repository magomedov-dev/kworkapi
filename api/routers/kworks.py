"""REST: управление своими kwork'ами."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/kworks", tags=["kworks"])


@router.post("/{kwork_id}/favorite")
async def mark_favorite(
    kwork_id: int,
    client: Annotated[KworkClient, Depends(get_client)],
    favorite: bool = True,
) -> dict:
    """Добавить/убрать kwork из избранного."""
    return await client.kworks.mark_favorite(kwork_id, favorite)


@router.post("/{kwork_id}/hidden")
async def mark_hidden(
    kwork_id: int,
    client: Annotated[KworkClient, Depends(get_client)],
    hidden: bool = True,
) -> dict:
    """Скрыть/вернуть kwork."""
    return await client.kworks.mark_hidden(kwork_id, hidden)


@router.post("/{kwork_id}/pause")
async def pause(kwork_id: int, client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Поставить свой kwork на паузу."""
    return await client.kworks.pause(kwork_id)


@router.post("/{kwork_id}/start")
async def start(kwork_id: int, client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Запустить свой kwork."""
    return await client.kworks.start(kwork_id)
