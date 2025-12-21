"""REST: каталог и поиск."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories")
async def categories(client: Annotated[KworkClient, Depends(get_client)]) -> list:
    """Дерево категорий."""
    return [c.model_dump() for c in await client.catalog.categories()]


@router.get("/search")
async def search(
    q: str,
    client: Annotated[KworkClient, Depends(get_client)],
    page: int = 1,
) -> dict:
    """Поиск kwork'ов."""
    return (await client.search.kworks(q, page=page)).model_dump()
