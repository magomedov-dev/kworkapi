"""Каталог: дерево категорий, рубрики, листинг и подборки kwork'ов."""

from __future__ import annotations

from typing import Any

from kworkapi.models.catalog import Category
from kworkapi.models.common import Page
from kworkapi.models.kwork import Kwork, KworksResult
from kworkapi.resources.base import Resource


class CatalogResource(Resource):
    async def categories(self, *, type: int = 1) -> list[Category]:
        """Дерево категорий (`/categories`): рубрика → категория → подкатегория."""
        return self._list(await self._call("categories", data={"type": type}), Category)

    async def rubrics(self) -> dict[str, Any]:
        """Рубрики каталога (`/catalogRubrics`)."""
        return self._payload(await self._call("catalogRubrics"))

    async def main(self) -> dict[str, Any]:
        """Главная каталога (`/catalogMainv2`)."""
        return self._payload(await self._call("catalogMainv2"))

    async def kworks(
        self,
        *,
        category_id: int | None = None,
        classifier_id: int | None = None,
        page: int = 1,
        limit: int | None = None,
    ) -> KworksResult:
        """Листинг kwork'ов категории (`/kworks`)."""
        data = {
            "categoryId": category_id,
            "classifierId": classifier_id,
            "page": page,
            "limit": limit,
        }
        return self._model(await self._call("kworks", data=data), KworksResult)

    async def favorites(self, *, page: int = 1) -> Page[Kwork]:
        """Избранные kwork'и (`/favoriteKworks`)."""
        return self._page(await self._call("favoriteKworks", data={"page": page}), Kwork)

    async def hidden(self, *, page: int = 1) -> Page[Kwork]:
        """Скрытые kwork'и (`/getHiddenKworks`)."""
        return self._page(await self._call("getHiddenKworks", data={"page": page}), Kwork)

    async def viewed(self, *, page: int = 1) -> Page[Kwork]:
        """Просмотренные kwork'и (`/viewedCatalogKworks`)."""
        return self._page(await self._call("viewedCatalogKworks", data={"page": page}), Kwork)

    async def filters(self, *, category_id: int | None = None, query: str | None = None) -> dict[str, Any]:
        """Доступные фильтры категории/поиска (`/catalogFilters`)."""
        data = {"categoryId": category_id, "query": query}
        return self._payload(await self._call("catalogFilters", data=data))
