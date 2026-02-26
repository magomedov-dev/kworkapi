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

    # --- действия ------------------------------------------------------

    async def create_offer(
        self,
        want_id: int,
        description: str,
        *,
        price: int,
        duration: int,
        offer_type: str = "custom",
    ) -> dict:
        """Откликнуться на проект (`/api/offer/createoffer`, multipart).

        :param want_id: id проекта.
        :param description: текст отклика.
        :param price: цена в рублях.
        :param duration: срок в днях.
        """
        data = {
            "wantId": want_id,
            "offerType": offer_type,
            "description": description,
            "kwork_price": price,
            "kwork_duration": duration,
        }
        return await self._call("api/offer/createoffer", data=data, multipart=True)

    async def edit_offer(
        self,
        want_id: int,
        description: str,
        *,
        price: int,
        duration: int,
        offer_type: str = "custom",
    ) -> dict:
        """Изменить отклик (`/api/offer/editoffer`, multipart)."""
        data = {
            "wantId": want_id,
            "offerType": offer_type,
            "description": description,
            "kwork_price": price,
            "kwork_duration": duration,
        }
        return await self._call("api/offer/editoffer", data=data, multipart=True)

    async def delete_offer(self, offer_id: int) -> dict:
        """Удалить отклик (`/api/offer/deleteoffer`)."""
        return await self._call("api/offer/deleteoffer", data={"id": offer_id})

    async def get_offer(self, offer_id: int) -> Offer:
        """Детали отклика (`/offer`)."""
        return self._model(await self._call("offer", data={"id": offer_id}), Offer)

    async def projects_count(
        self,
        *,
        categories: str = "all",
        attributes: str = "",
        price_from: int | None = None,
        price_to: int | None = None,
        hiring_from: int | None = None,
        offers: str = "",
    ) -> dict:
        """Число доступных проектов по фильтрам (`/getWantsCount`)."""
        data = {
            "categories": categories,
            "attributes": attributes,
            "price_from": price_from,
            "price_to": price_to,
            "hiring_from": hiring_from,
            "offers": offers,
        }
        return self._payload(await self._call("getWantsCount", data=data))

    async def set_favorite_categories(self, categories: str, *, attributes: str = "") -> dict:
        """Сохранить избранные категории биржи (`/setFavorite`)."""
        return await self._call("setFavorite", data={"categories": categories, "attributes": attributes})
