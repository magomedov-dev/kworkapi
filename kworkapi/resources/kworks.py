"""Управление своими kwork'ами (исполнитель) и пометками каталога.

Имена методов подтверждены кодом UserService.
"""

from __future__ import annotations

from kworkapi.resources.base import Resource


class KworksResource(Resource):
    # --- чтение деталей -------------------------------------------------

    async def details(self, kwork_id: int) -> dict:
        """Детали kwork (`/getKworkDetails`)."""
        return self._payload(await self._call("getKworkDetails", data={"id": kwork_id}))

    async def reviews(self, kwork_id: int, *, type: str = "", page: int = 1) -> dict:
        """Отзывы о kwork (`/getKworkReviews`)."""
        data = {"kwork_id": kwork_id, "type": type, "page": page}
        return await self._call("getKworkReviews", data=data)

    async def portfolios(self, kwork_id: int, *, page: int = 1) -> dict:
        """Портфолио по kwork (`/getKworkPortfolios`)."""
        return self._payload(
            await self._call("getKworkPortfolios", data={"id": kwork_id, "page": page})
        )

    async def details_extra(self, kwork_id: int) -> dict:
        """Доп. детали kwork (`/getKworkDetailsExtra`)."""
        return self._payload(await self._call("getKworkDetailsExtra", data={"id": kwork_id}))

    async def faq(self, kwork_id: int) -> dict:
        """Вопросы-ответы по kwork (`/getKworkAnswers`)."""
        return self._payload(await self._call("getKworkAnswers", data={"id": kwork_id}))

    async def links_table(self, kwork_id: int, *, page: int = 1) -> dict:
        """Таблица доменов/ссылок kwork (`/getKworkLinksTable`)."""
        return await self._call("getKworkLinksTable", data={"id": kwork_id, "page": page})

    async def complain_categories(self) -> dict:
        """Категории жалоб на kwork (`/getComplainCategories`)."""
        return self._payload(await self._call("getComplainCategories"))

    async def recharge_balance(
        self,
        order_id: int,
        amount: float,
        *,
        payment_id: str = "",
        payment_type: str = "",
        country_group_code: str = "",
    ) -> dict:
        """Пополнить баланс для оплаты заказа (`/rechargeBalance`)."""
        data = {
            "orderId": order_id,
            "amount": amount,
            "payment_id": payment_id,
            "paymentType": payment_type,
            "country_group_code": country_group_code,
        }
        return await self._call("rechargeBalance", data=data)

    # --- управление своими kwork'ами -----------------------------------

    async def mark_favorite(self, kwork_id: int, favorite: bool = True) -> dict:
        """Добавить/убрать kwork из избранного (`/markKworkAsFavorite`)."""
        data = {"kwork_id": kwork_id, "is_favorite": 1 if favorite else 0}
        return await self._call("markKworkAsFavorite", data=data)

    async def mark_hidden(self, kwork_id: int, hidden: bool = True) -> dict:
        """Скрыть/вернуть kwork из скрытых (`/markKworkAsHidden`)."""
        data = {"kwork_id": kwork_id, "is_hidden": 1 if hidden else 0}
        return await self._call("markKworkAsHidden", data=data)

    async def pause(self, kwork_id: int) -> dict:
        """Поставить свой kwork на паузу (`/pauseKwork`)."""
        return await self._call("pauseKwork", data={"kwork_id": kwork_id})

    async def start(self, kwork_id: int) -> dict:
        """Запустить (снять с паузы) свой kwork (`/startKwork`)."""
        return await self._call("startKwork", data={"kwork_id": kwork_id})

    async def delete(self, kwork_id: int) -> dict:
        """Удалить свой kwork (`/deleteKwork`)."""
        return await self._call("deleteKwork", data={"kwork_id": kwork_id})
