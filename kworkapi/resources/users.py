"""Пользователи: профили, их kwork'и и отзывы."""

from __future__ import annotations

from kworkapi.models.common import Page
from kworkapi.models.kwork import Kwork
from kworkapi.models.user import User
from kworkapi.resources.base import Resource


class UsersResource(Resource):
    async def get(self, user_id: int) -> User:
        """Профиль пользователя по id (`/user`)."""
        return self._model(await self._call("user", data={"id": user_id}), User)

    async def by_username(self, username: str) -> User:
        """Профиль пользователя по username (`/userByUsername`)."""
        return self._model(await self._call("userByUsername", data={"username": username}), User)

    async def kworks(self, user_id: int, *, page: int = 1) -> Page[Kwork]:
        """kwork'и пользователя (`/userKworks`)."""
        data = {"user_id": user_id, "page": page}
        return self._page(await self._call("userKworks", data=data), Kwork)

    async def reviews(self, user_id: int, *, type: str = "", page: int = 1) -> dict:
        """Отзывы о пользователе (`/userReviews`)."""
        data = {"user_id": user_id, "type": type, "page": page}
        return await self._call("userReviews", data=data)
