"""Биржа проектов: лента заказов, категории, отклики исполнителя."""

from __future__ import annotations

from kworkapi.models.catalog import Category
from kworkapi.models.exchange import ExchangeInfo, Offer
from kworkapi.resources.base import Resource


class ExchangeResource(Resource):
    async def projects(
        self,
        *,
        categories: str = "all",
        price_from: int | None = None,
        price_to: int | None = None,
        page: int = 1,
    ) -> dict:
        """Лента проектов на бирже (`/projects`).

        Возвращает сырой ответ: структура зависит от наличия проектов
        (`connects` + `paging`, при наличии — список проектов).
        """
        data = {
            "categories": categories,
            "price_from": price_from,
            "price_to": price_to,
            "page": page,
        }
        return await self._call("projects", data=data)

    async def info(self) -> ExchangeInfo:
        """Сводка по бирже (`/exchangeInfo`)."""
        return self._model(await self._call("exchangeInfo"), ExchangeInfo)

    async def categories(self, *, type: int = 1) -> list[Category]:
        """Категории проектов биржи (`/categories`)."""
        return self._list(await self._call("categories", data={"type": type}), Category)

    async def favorite_categories(self) -> dict:
        """Избранные категории биржи (`/favoriteCategories`)."""
        return self._payload(await self._call("favoriteCategories"))

    async def wants_count(self) -> dict:
        """Счётчик и фильтры доступных проектов (`/getWantsCount`)."""
        return self._payload(await self._call("getWantsCount"))

    async def my_offers(self, *, page: int = 1) -> list[Offer]:
        """Мои отклики на проекты (`/offers`)."""
        return self._list(await self._call("offers", data={"page": page}), Offer)

    async def my_wants(self, *, page: int = 1, status_id: int = -1) -> dict:
        """Мои размещённые проекты (`/myWants`)."""
        data = {"page": page, "want_status_id": status_id}
        return await self._call("myWants", data=data)
