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

    # --- экстры (доп. опции заказа) ------------------------------------

    async def available_extras(self, order_id: int) -> dict:
        """Доступные экстры для заказа (`/getExtrasAvailableForOrder`)."""
        return self._payload(
            await self._call("getExtrasAvailableForOrder", data={"orderId": order_id})
        )

    async def ordered_extras(self, order_id: int) -> dict:
        """Заказанные экстры (`/getOrderedExtras`)."""
        return self._payload(await self._call("getOrderedExtras", data={"orderId": order_id}))

    async def buy_extras(self, order_id: int, *, as_volume: int = 0) -> dict:
        """Купить экстры как покупатель (`/payerBuyExtras`)."""
        return await self._call("payerBuyExtras", data={"order_id": order_id, "as_volume": as_volume})

    async def accept_extra(self, order_id: int, track_id: int) -> dict:
        """Принять предложенную экстру (`/acceptExtras`)."""
        return await self._call("acceptExtras", data={"order_id": order_id, "track_id": track_id})

    async def decline_extra(self, order_id: int, track_id: int) -> dict:
        """Отклонить предложенную экстру (`/payerDeclineExtras`)."""
        data = {"order_id": order_id, "track_id": track_id}
        return await self._call("payerDeclineExtras", data=data)

    async def delete_extra(self, extra_id: int) -> dict:
        """Удалить экстру как покупатель (`/payerExtraDelete`)."""
        return await self._call("payerExtraDelete", data={"extra_id": extra_id})

    # --- стадии заказа -------------------------------------------------

    async def accept_stage(self, order_id: int) -> dict:
        """Принять предложение по стадиям (`/acceptStageSuggestion`)."""
        return await self._call("acceptStageSuggestion", data={"order_id": order_id})

    async def reject_stage(self, order_id: int) -> dict:
        """Отклонить предложение по стадиям (`/rejectStageSuggestion`)."""
        return await self._call("rejectStageSuggestion", data={"order_id": order_id})

    async def pay_stage(self, order_id: int, stage_id: int) -> dict:
        """Оплатить стадию заказа (`/orderStage`)."""
        return await self._call("orderStage", data={"order_id": order_id, "stage_id": stage_id})

    async def update_stage_progress(
        self, order_id: int, progress: dict[int, int], *, comment: str = ""
    ) -> dict:
        """Обновить прогресс по стадиям (`/updateStageProgress`).

        :param progress: соответствие stage_id → процент (0..100).
        """
        data: dict = {"order_id": order_id, "comment": comment}
        data.update({str(stage): pct for stage, pct in progress.items()})
        return await self._call("updateStageProgress", data=data)

    # --- арбитраж и отчёты --------------------------------------------

    async def rate_arbitration(self, arbitration_id: int, rating: int) -> dict:
        """Оценить решение арбитража (`/rateArbitration`)."""
        return await self._call("rateArbitration", data={"id": arbitration_id, "rating": rating})

    async def send_report(
        self, order_id: int, progress: int, *, comment: str = "", track_id: int | None = None
    ) -> dict:
        """Отправить отчёт о ходе работы (`/sendReport`)."""
        data = {"order_id": order_id, "progress": progress, "comment": comment, "track_id": track_id}
        return await self._call("sendReport", data=data)
