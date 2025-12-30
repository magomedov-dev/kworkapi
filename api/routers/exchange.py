"""REST: биржа проектов."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api._serialize import dump
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


@router.get("/info")
async def info(client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Сводка по бирже."""
    return dump(await client.exchange.info())


@router.get("/offers")
async def my_offers(client: Annotated[KworkClient, Depends(get_client)], page: int = 1) -> list:
    """Мои отклики."""
    return dump(await client.exchange.my_offers(page=page))


class OfferRequest(BaseModel):
    want_id: int
    description: str
    price: int
    duration: int


@router.post("/offers")
async def create_offer(
    body: OfferRequest, client: Annotated[KworkClient, Depends(get_client)]
) -> dict:
    """Откликнуться на проект."""
    return await client.exchange.create_offer(
        body.want_id, body.description, price=body.price, duration=body.duration
    )


@router.delete("/offers/{offer_id}")
async def delete_offer(
    offer_id: int, client: Annotated[KworkClient, Depends(get_client)]
) -> dict:
    """Удалить отклик."""
    return await client.exchange.delete_offer(offer_id)
