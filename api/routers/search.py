"""REST: поиск."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api._serialize import dump
from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/kworks")
async def kworks(
    q: str,
    client: Annotated[KworkClient, Depends(get_client)],
    category_id: int | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Поиск kwork'ов."""
    return dump(await client.search.kworks(q, category_id=category_id, page=page, limit=limit))


@router.get("/users")
async def users(q: str, client: Annotated[KworkClient, Depends(get_client)], page: int = 1) -> dict:
    """Поиск пользователей."""
    return dump(await client.search.users(q, page=page))
