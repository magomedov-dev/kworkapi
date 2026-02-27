"""Пользователи: профили, их kwork'и и отзывы."""

from __future__ import annotations

from typing import Any

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

    async def reviews(self, user_id: int, *, type: str = "", page: int = 1) -> dict[str, Any]:
        """Отзывы о пользователе (`/userReviews`)."""
        data = {"user_id": user_id, "type": type, "page": page}
        return await self._call("userReviews", data=data)

    async def kworks_categories(self, user_id: int) -> dict[str, Any]:
        """Категории kwork'ов пользователя (`/kworksCategoriesList`)."""
        return self._payload(await self._call("kworksCategoriesList", data={"user_id": user_id}))

    async def kworks_statuses(self) -> dict[str, Any]:
        """Список возможных статусов kwork (`/kworksStatusList`)."""
        return self._payload(await self._call("kworksStatusList"))

    async def blocked_dialogs(self, *, page: int = 1) -> dict[str, Any]:
        """Список заблокированных диалогов (`/blockedDialogs`)."""
        return await self._call("blockedDialogs", data={"page": page})
