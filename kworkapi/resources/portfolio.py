"""Портфолио пользователей."""

from __future__ import annotations

from typing import Any

from kworkapi.resources.base import Resource


class PortfolioResource(Resource):
    async def categories(self, user_id: int) -> dict[str, Any]:
        """Категории портфолио пользователя (`/portfolioCategoriesList`)."""
        return self._payload(await self._call("portfolioCategoriesList", data={"user_id": user_id}))

    async def list(self, user_id: int, *, category_id: int | None = None, page: int = 1) -> dict[str, Any]:
        """Работы в портфолио пользователя (`/portfolioList`)."""
        data = {"user_id": user_id, "category_id": category_id, "page": page}
        return await self._call("portfolioList", data=data)
