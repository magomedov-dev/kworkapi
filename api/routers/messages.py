"""REST: сообщения и чаты."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api._serialize import dump
from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/dialogs")
async def dialogs(client: Annotated[KworkClient, Depends(get_client)], page: int = 1) -> list:
    """Список диалогов."""
    return dump(await client.messages.dialogs(page=page))


@router.get("/dialogs/{user_id}")
async def history(
    user_id: int, client: Annotated[KworkClient, Depends(get_client)], limit: int = 30
) -> list:
    """История переписки с пользователем."""
    return dump(await client.messages.history(user_id, limit=limit))


class SendRequest(BaseModel):
    user_id: int
    text: str


@router.post("/send")
async def send(body: SendRequest, client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Отправить сообщение."""
    return dump(await client.messages.send(body.user_id, body.text))


@router.post("/dialogs/{user_id}/starred")
async def set_starred(
    user_id: int,
    client: Annotated[KworkClient, Depends(get_client)],
    starred: bool = True,
) -> dict:
    """Добавить/убрать диалог из избранного."""
    return await client.messages.set_starred(user_id, starred)


@router.post("/dialogs/{user_id}/block")
async def block(user_id: int, client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Заблокировать диалог."""
    return await client.messages.block(user_id)
