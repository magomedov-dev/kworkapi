"""Заказы: списки, детали и управление (исполнитель/покупатель).

Поля сверены с кодом OrderService. У части методов (отмена, причины отмены)
точные поля не подтверждены захватом — помечены best-effort.
"""

from __future__ import annotations

from typing import Any, cast

from kworkapi.exceptions import KworkAPIError
from kworkapi.resources.base import Resource

# Код ответа «нет заказов» — приложение отдаёт его как ошибку, мы трактуем как пустой список.
_EMPTY_ORDERS_CODE = 151


class OrdersResource(Resource):
    # --- списки --------------------------------------------------------

    async def worker(self, *, filter: str = "all") -> list[Any]:
        """Заказы текущего пользователя как исполнителя (`/workerOrders`)."""
        return await self._orders("workerOrders", {"filter": filter})

    async def payer(self, *, filter: str = "all", company_orders: int = 0) -> list[Any]:
        """Заказы текущего пользователя как покупателя (`/payerOrders`)."""
        return await self._orders("payerOrders", {"filter": filter, "company_orders": company_orders})

    async def _orders(self, method: str, data: dict[str, Any]) -> list[Any]:
        try:
            body = await self._call(method, data=data)
        except KworkAPIError as exc:
            if exc.code == _EMPTY_ORDERS_CODE:
                return []
            raise
        payload: Any = self._payload(body)
        result: list[Any] = cast("list[Any]", payload) if isinstance(payload, list) else []
        return result

    # --- детали --------------------------------------------------------

    async def details(self, order_id: int) -> dict[str, Any]:
        """Детали заказа (`/getOrderDetails`)."""
        return self._payload(await self._call("getOrderDetails", data={"orderId": order_id}))

    async def header(self, order_id: int) -> dict[str, Any]:
        """Шапка заказа (`/getOrderHeader`)."""
        return self._payload(await self._call("getOrderHeader", data={"orderId": order_id}))

    async def files(self, order_id: int) -> dict[str, Any]:
        """Файлы заказа (`/getOrderFiles`)."""
        return self._payload(await self._call("getOrderFiles", data={"id": order_id}))

    # --- управление (исполнитель) --------------------------------------

    async def approve(self, order_id: int, *, portfolio: int = 0) -> dict[str, Any]:
        """Принять/подтвердить заказ (`/approveOrder`)."""
        return await self._call("approveOrder", data={"orderId": order_id, "portfolio": portfolio})

    async def approve_stages(self, order_id: int) -> dict[str, Any]:
        """Подтвердить стадии заказа (`/approveOrderStages`)."""
        return await self._call("approveOrderStages", data={"orderId": order_id})

    async def send_for_approval(self, order_id: int) -> dict[str, Any]:
        """Отправить заказ на проверку покупателю (`/sendOrderForApproval`)."""
        return await self._call("sendOrderForApproval", data={"orderId": order_id})

    async def send_requirements(self, order_id: int, requirements: str) -> dict[str, Any]:
        """Отправить требования к заказу (`/sendOrderRequirements`)."""
        data = {"orderId": order_id, "requirements": requirements}
        return await self._call("sendOrderRequirements", data=data)

    async def send_for_revision(self, order_id: int, revision: str) -> dict[str, Any]:
        """Вернуть заказ на доработку (`/sendOrderForRevision`)."""
        data = {"orderId": order_id, "revision": revision}
        return await self._call("sendOrderForRevision", data=data)

    async def repeat(self, order_id: int) -> dict[str, Any]:
        """Повторить заказ (`/repeatOrder`)."""
        return await self._call("repeatOrder", data={"orderId": order_id})

    async def send_bonus(self, order_id: int, bonus: int, *, comment: str = "") -> dict[str, Any]:
        """Отправить бонус исполнителю (`/sendBonus`)."""
        data = {"orderId": order_id, "bonus": bonus, "comment": comment}
        return await self._call("sendBonus", data=data)

    # --- отмена заказа -------------------------------------------------

    async def cancellation_reasons(self, order_id: int) -> dict[str, Any]:
        """Доступные причины отмены заказа (`/getOrderCancellationReasons`)."""
        return self._payload(
            await self._call("getOrderCancellationReasons", data={"orderId": order_id})
        )

    async def cancel_by_payer(
        self, order_id: int, *, reason_type: int, message: str = "", hide_kworks: bool = False
    ) -> dict[str, Any]:
        """Запросить отмену заказа как покупатель (`/cancelOrderByPayer`)."""
        data = {
            "order_id": order_id,
            "reason_type": reason_type,
            "message": message,
            "hideKworks": 1 if hide_kworks else 0,
        }
        return await self._call("cancelOrderByPayer", data=data)

    async def cancel_by_worker(self, order_id: int, *, reason_type: int, message: str = "") -> dict[str, Any]:
        """Запросить отмену заказа как исполнитель (`/cancelOrderByWorker`)."""
        data = {"order_id": order_id, "reason_type": reason_type, "message": message}
        return await self._call("cancelOrderByWorker", data=data)

    async def cancel_awaiting_payment(self, order_id: int) -> dict[str, Any]:
        """Отменить заказ, ожидающий оплаты (`/cancelOrderAwaitingPayment`)."""
        return await self._call("cancelOrderAwaitingPayment", data={"order_id": order_id})

    async def pay_awaiting_payment(self, order_id: int) -> dict[str, Any]:
        """Оплатить заказ, ожидающий оплаты (`/payOrderAwaitingPayment`)."""
        return await self._call("payOrderAwaitingPayment", data={"order_id": order_id})

    # --- ответ на запрос отмены (встречная сторона) -------------------

    async def confirm_cancel_as_payer(self, order_id: int, *, reply_type: int) -> dict[str, Any]:
        """Подтвердить запрос отмены как покупатель (`/confirmCancelOrderRequestByPayer`)."""
        data = {"order_id": order_id, "reply_type": reply_type}
        return await self._call("confirmCancelOrderRequestByPayer", data=data)

    async def confirm_cancel_as_worker(self, order_id: int) -> dict[str, Any]:
        """Подтвердить запрос отмены как исполнитель (`/confirmCancelOrderRequestByWorker`)."""
        return await self._call("confirmCancelOrderRequestByWorker", data={"order_id": order_id})

    async def reject_cancel_as_payer(self, order_id: int) -> dict[str, Any]:
        """Отклонить запрос отмены как покупатель (`/rejectCancelOrderRequestByPayer`)."""
        return await self._call("rejectCancelOrderRequestByPayer", data={"order_id": order_id})

    async def reject_cancel_as_worker(self, order_id: int) -> dict[str, Any]:
        """Отклонить запрос отмены как исполнитель (`/rejectCancelOrderRequestByWorker`)."""
        return await self._call("rejectCancelOrderRequestByWorker", data={"order_id": order_id})

    async def delete_cancel_as_payer(self, order_id: int) -> dict[str, Any]:
        """Отозвать свой запрос отмены как покупатель (`/deleteCancelOrderRequestByPayer`)."""
        return await self._call("deleteCancelOrderRequestByPayer", data={"order_id": order_id})

    async def delete_cancel_as_worker(self, order_id: int) -> dict[str, Any]:
        """Отозвать свой запрос отмены как исполнитель (`/deleteCancelOrderRequestByWorker`)."""
        return await self._call("deleteCancelOrderRequestByWorker", data={"order_id": order_id})

    # --- пресеты кастомных опций (экстр) -------------------------------

    async def custom_options_presets(self, order_id: int) -> dict[str, Any]:
        """Пресеты кастомных опций для заказа (`/getCustomOptionsPresets`)."""
        return self._payload(
            await self._call("getCustomOptionsPresets", data={"order_id": order_id})
        )

    async def offer_options(self, order_id: int) -> dict[str, Any]:
        """Предложить опции (экстры) по заказу (`/offerOrderOptions`)."""
        return await self._call("offerOrderOptions", data={"orderId": order_id})

    # --- исполнитель: статус, портфолио, чек, ответы ------------------

    async def worker_in_progress(self, order_id: int, *, contracts_agreement: int = 1) -> dict[str, Any]:
        """Взять заказ в работу как исполнитель (`/workerInprogress`)."""
        data = {"order_id": order_id, "contracts_agreement": contracts_agreement}
        return await self._call("workerInprogress", data=data)

    async def allow_portfolio(self, order_id: int) -> dict[str, Any]:
        """Разрешить загрузку портфолио по заказу (`/allowOrderPortfolioUpload`)."""
        return await self._call("allowOrderPortfolioUpload", data={"order_id": order_id})

    async def delete_portfolio(self, portfolio_id: int, *, unlink: int = 0) -> dict[str, Any]:
        """Удалить портфолио (`/deletePortfolio`)."""
        return await self._call("deletePortfolio", data={"portfolio_id": portfolio_id, "unlink": unlink})

    async def edit_answer(self, answer_id: int, text: str) -> dict[str, Any]:
        """Изменить ответ на отзыв (`/editAnswer`)."""
        return await self._call("editAnswer", data={"answer_id": answer_id, "text": text})

    async def send_receipt(self, receipt_id: int, receipt_link: str) -> dict[str, Any]:
        """Отправить ссылку на чек для верификации (`/sendOrderReceiptLinkForVerification`)."""
        data = {"receiptId": receipt_id, "receiptLink": receipt_link}
        return await self._call("sendOrderReceiptLinkForVerification", data=data)

    # --- экстры со стороны исполнителя --------------------------------

    async def worker_decline_extra(self, order_id: int, track_id: int) -> dict[str, Any]:
        """Отклонить экстру как исполнитель (`/workerDeclineExtras`)."""
        return await self._call("workerDeclineExtras", data={"order_id": order_id, "track_id": track_id})

    async def worker_delete_extra(self, extra_id: int) -> dict[str, Any]:
        """Удалить экстру как исполнитель (`/workerExtraDelete`)."""
        return await self._call("workerExtraDelete", data={"extra_id": extra_id})

    async def accept_extra_removal(self, track_id: int) -> dict[str, Any]:
        """Подтвердить запрос на удаление экстры (`/workerConfirmsExtraRemovalRequest`)."""
        return await self._call("workerConfirmsExtraRemovalRequest", data={"track_id": track_id})

    async def decline_extra_removal(self, track_id: int) -> dict[str, Any]:
        """Отклонить запрос на удаление экстры (`/workerDeclinesExtraRemovalRequest`)."""
        return await self._call("workerDeclinesExtraRemovalRequest", data={"track_id": track_id})

    # --- отзывы и ответы ----------------------------------------------

    async def create_review(self, order_id: int, *, positive: bool, text: str) -> dict[str, Any]:
        """Оставить отзыв по заказу (`/createReview`). type: positive/negative."""
        data = {"order_id": order_id, "type": "positive" if positive else "negative", "text": text}
        return await self._call("createReview", data=data)

    async def edit_review(self, order_id: int, *, positive: bool, text: str) -> dict[str, Any]:
        """Изменить отзыв (`/editReview`)."""
        data = {"order_id": order_id, "type": "positive" if positive else "negative", "text": text}
        return await self._call("editReview", data=data)

    async def delete_review(self, order_id: int) -> dict[str, Any]:
        """Удалить отзыв (`/deleteReview`)."""
        return await self._call("deleteReview", data={"order_id": order_id})

    async def create_answer(self, review_id: int, text: str) -> dict[str, Any]:
        """Ответить на отзыв (`/createAnswer`)."""
        return await self._call("createAnswer", data={"review_id": review_id, "text": text})

    # --- экстры (доп. опции заказа) ------------------------------------

    async def available_extras(self, order_id: int) -> dict[str, Any]:
        """Доступные экстры для заказа (`/getExtrasAvailableForOrder`)."""
        return self._payload(
            await self._call("getExtrasAvailableForOrder", data={"orderId": order_id})
        )

    async def ordered_extras(self, order_id: int) -> dict[str, Any]:
        """Заказанные экстры (`/getOrderedExtras`)."""
        return self._payload(await self._call("getOrderedExtras", data={"orderId": order_id}))

    async def buy_extras(self, order_id: int, *, as_volume: int = 0) -> dict[str, Any]:
        """Купить экстры как покупатель (`/payerBuyExtras`)."""
        return await self._call("payerBuyExtras", data={"order_id": order_id, "as_volume": as_volume})

    async def accept_extra(self, order_id: int, track_id: int) -> dict[str, Any]:
        """Принять предложенную экстру (`/acceptExtras`)."""
        return await self._call("acceptExtras", data={"order_id": order_id, "track_id": track_id})

    async def decline_extra(self, order_id: int, track_id: int) -> dict[str, Any]:
        """Отклонить предложенную экстру (`/payerDeclineExtras`)."""
        data = {"order_id": order_id, "track_id": track_id}
        return await self._call("payerDeclineExtras", data=data)

    async def delete_extra(self, extra_id: int) -> dict[str, Any]:
        """Удалить экстру как покупатель (`/payerExtraDelete`)."""
        return await self._call("payerExtraDelete", data={"extra_id": extra_id})

    # --- стадии заказа -------------------------------------------------

    async def accept_stage(self, order_id: int) -> dict[str, Any]:
        """Принять предложение по стадиям (`/acceptStageSuggestion`)."""
        return await self._call("acceptStageSuggestion", data={"order_id": order_id})

    async def reject_stage(self, order_id: int) -> dict[str, Any]:
        """Отклонить предложение по стадиям (`/rejectStageSuggestion`)."""
        return await self._call("rejectStageSuggestion", data={"order_id": order_id})

    async def pay_stage(self, order_id: int, stage_id: int) -> dict[str, Any]:
        """Оплатить стадию заказа (`/orderStage`)."""
        return await self._call("orderStage", data={"order_id": order_id, "stage_id": stage_id})

    async def update_stage_progress(
        self, order_id: int, progress: dict[int, int], *, comment: str = ""
    ) -> dict[str, Any]:
        """Обновить прогресс по стадиям (`/updateStageProgress`).

        :param progress: соответствие stage_id → процент (0..100).
        """
        data: dict[str, Any] = {"order_id": order_id, "comment": comment}
        data.update({str(stage): pct for stage, pct in progress.items()})
        return await self._call("updateStageProgress", data=data)

    # --- арбитраж и отчёты --------------------------------------------

    async def rate_arbitration(self, arbitration_id: int, rating: int) -> dict[str, Any]:
        """Оценить решение арбитража (`/rateArbitration`)."""
        return await self._call("rateArbitration", data={"id": arbitration_id, "rating": rating})

    async def send_report(
        self, order_id: int, progress: int, *, comment: str = "", track_id: int | None = None
    ) -> dict[str, Any]:
        """Отправить отчёт о ходе работы (`/sendReport`)."""
        data = {"order_id": order_id, "progress": progress, "comment": comment, "track_id": track_id}
        return await self._call("sendReport", data=data)
