"""REST: биржа проектов."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/exchange", tags=["exchange"])


@router.get("/projects")
async def projects(
    client: Annotated[KworkClient, Depends(get_client)],
    categories: str = "all",
    page: int = 1,
) -> dict:
    """Лента проектов на бирже."""
    return await client.exchange.projects(categories=categories, page=page)


@router.get("/offers")
async def my_offers(client: Annotated[KworkClient, Depends(get_client)]) -> list:
    """Мои отклики."""
    offers = await client.exchange.my_offers()
    return [o.model_dump() for o in offers]
