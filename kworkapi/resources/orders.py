"""Заказы: списки, детали и управление (исполнитель/покупатель).

Поля сверены с кодом OrderService. У части методов (отмена, причины отмены)
точные поля не подтверждены захватом — помечены best-effort.
"""

from __future__ import annotations

from kworkapi.exceptions import KworkAPIError
from kworkapi.resources.base import Resource

# Код ответа «нет заказов» — приложение отдаёт его как ошибку, мы трактуем как пустой список.
_EMPTY_ORDERS_CODE = 151


class OrdersResource(Resource):
    # --- списки --------------------------------------------------------

    async def worker(self, *, filter: str = "all") -> list:
        """Заказы текущего пользователя как исполнителя (`/workerOrders`)."""
        return await self._orders("workerOrders", {"filter": filter})

    async def payer(self, *, filter: str = "all", company_orders: int = 0) -> list:
        """Заказы текущего пользователя как покупателя (`/payerOrders`)."""
        return await self._orders("payerOrders", {"filter": filter, "company_orders": company_orders})

    async def _orders(self, method: str, data: dict) -> list:
        try:
            body = await self._call(method, data=data)
        except KworkAPIError as exc:
            if exc.code == _EMPTY_ORDERS_CODE:
                return []
            raise
        payload = self._payload(body)
        return payload if isinstance(payload, list) else []

    # --- детали --------------------------------------------------------

    async def details(self, order_id: int) -> dict:
        """Детали заказа (`/getOrderDetails`)."""
        return self._payload(await self._call("getOrderDetails", data={"orderId": order_id}))

    async def header(self, order_id: int) -> dict:
        """Шапка заказа (`/getOrderHeader`)."""
        return self._payload(await self._call("getOrderHeader", data={"orderId": order_id}))

    async def files(self, order_id: int) -> dict:
        """Файлы заказа (`/getOrderFiles`)."""
        return self._payload(await self._call("getOrderFiles", data={"id": order_id}))

    # --- управление (исполнитель) --------------------------------------

    async def approve(self, order_id: int, *, portfolio: int = 0) -> dict:
        """Принять/подтвердить заказ (`/approveOrder`)."""
        return await self._call("approveOrder", data={"orderId": order_id, "portfolio": portfolio})

    async def approve_stages(self, order_id: int) -> dict:
        """Подтвердить стадии заказа (`/approveOrderStages`)."""
        return await self._call("approveOrderStages", data={"orderId": order_id})

    async def send_for_approval(self, order_id: int) -> dict:
        """Отправить заказ на проверку покупателю (`/sendOrderForApproval`)."""
        return await self._call("sendOrderForApproval", data={"orderId": order_id})

    async def send_requirements(self, order_id: int, requirements: str) -> dict:
        """Отправить требования к заказу (`/sendOrderRequirements`)."""
        data = {"orderId": order_id, "requirements": requirements}
        return await self._call("sendOrderRequirements", data=data)

    async def send_for_revision(self, order_id: int, revision: str) -> dict:
        """Вернуть заказ на доработку (`/sendOrderForRevision`)."""
        data = {"orderId": order_id, "revision": revision}
        return await self._call("sendOrderForRevision", data=data)

    async def repeat(self, order_id: int) -> dict:
        """Повторить заказ (`/repeatOrder`)."""
        return await self._call("repeatOrder", data={"orderId": order_id})

    async def send_bonus(self, order_id: int, bonus: int, *, comment: str = "") -> dict:
        """Отправить бонус исполнителю (`/sendBonus`)."""
        data = {"orderId": order_id, "bonus": bonus, "comment": comment}
        return await self._call("sendBonus", data=data)

    # --- отмена (best-effort: точные поля не подтверждены) -------------

    async def cancel_by_worker(self, order_id: int) -> dict:
        """Отменить заказ как исполнитель (`/cancelOrderByWorker`)."""
        return await self._call("cancelOrderByWorker", data={"orderId": order_id})

    async def cancel_by_payer(self, order_id: int) -> dict:
        """Отменить заказ как покупатель (`/cancelOrderByPayer`)."""
        return await self._call("cancelOrderByPayer", data={"orderId": order_id})

    # --- отзывы и ответы ----------------------------------------------

    async def create_review(self, order_id: int, *, positive: bool, text: str) -> dict:
        """Оставить отзыв по заказу (`/createReview`). type: positive/negative."""
        data = {"order_id": order_id, "type": "positive" if positive else "negative", "text": text}
        return await self._call("createReview", data=data)

    async def edit_review(self, order_id: int, *, positive: bool, text: str) -> dict:
        """Изменить отзыв (`/editReview`)."""
        data = {"order_id": order_id, "type": "positive" if positive else "negative", "text": text}
        return await self._call("editReview", data=data)

    async def delete_review(self, order_id: int) -> dict:
        """Удалить отзыв (`/deleteReview`)."""
        return await self._call("deleteReview", data={"order_id": order_id})

    async def create_answer(self, review_id: int, text: str) -> dict:
        """Ответить на отзыв (`/createAnswer`)."""
        return await self._call("createAnswer", data={"review_id": review_id, "text": text})
