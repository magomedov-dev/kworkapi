"""REST: пользователи."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api._serialize import dump
from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: int, client: Annotated[KworkClient, Depends(get_client)]) -> dict:
    """Профиль пользователя по id."""
    return dump(await client.users.get(user_id))


@router.get("/{user_id}/kworks")
async def user_kworks(
    user_id: int, client: Annotated[KworkClient, Depends(get_client)], page: int = 1
) -> dict:
    """kwork'и пользователя."""
    return dump(await client.users.kworks(user_id, page=page))


@router.get("/{user_id}/reviews")
async def user_reviews(
    user_id: int, client: Annotated[KworkClient, Depends(get_client)], page: int = 1
) -> dict:
    """Отзывы о пользователе."""
    return await client.users.reviews(user_id, page=page)
