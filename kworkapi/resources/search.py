"""Поиск: kwork'и, подсказки, пользователи."""

from __future__ import annotations

from kworkapi.models.common import Page
from kworkapi.models.kwork import KworksResult
from kworkapi.models.user import User
from kworkapi.resources.base import Resource


class SearchResource(Resource):
    async def kworks(
        self,
        query: str,
        *,
        category_id: int | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> KworksResult:
        """Поиск kwork'ов по запросу (`/search`)."""
        data = {
            "query": query,
            "categoryId": category_id,
            "page": page,
            "limit": limit,
        }
        return self._model(await self._call("search", data=data), KworksResult)

    async def suggest(self, query: str, *, page: int = 1) -> dict:
        """Подсказки поисковых запросов (`/searchKworksCatalogQuery`)."""
        data = {"query": query, "page": page}
        return self._payload(await self._call("searchKworksCatalogQuery", data=data))

    async def users(self, query: str, *, page: int = 1) -> Page[User]:
        """Поиск пользователей (`/userSearch`)."""
        return self._page(await self._call("userSearch", data={"query": query, "page": page}), User)
