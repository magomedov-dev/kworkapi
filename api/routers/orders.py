"""REST: заказы."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/worker")
async def worker_orders(
    client: Annotated[KworkClient, Depends(get_client)], filter: str = "all"
) -> list:
    """Заказы как исполнителя."""
    return await client.orders.worker(filter=filter)


@router.get("/payer")
async def payer_orders(
    client: Annotated[KworkClient, Depends(get_client)], filter: str = "all"
) -> list:
    """Заказы как покупателя."""
    return await client.orders.payer(filter=filter)
