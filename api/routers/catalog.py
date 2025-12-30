"""REST: каталог."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api._serialize import dump
from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories")
async def categories(client: Annotated[KworkClient, Depends(get_client)]) -> list:
    """Дерево категорий."""
    return dump(await client.catalog.categories())


@router.get("/kworks")
async def kworks(
    client: Annotated[KworkClient, Depends(get_client)],
    category_id: int | None = None,
    page: int = 1,
) -> dict:
    """Листинг kwork'ов категории."""
    return dump(await client.catalog.kworks(category_id=category_id, page=page))


@router.get("/favorites")
async def favorites(client: Annotated[KworkClient, Depends(get_client)], page: int = 1) -> dict:
    """Избранные kwork'и."""
    return dump(await client.catalog.favorites(page=page))
