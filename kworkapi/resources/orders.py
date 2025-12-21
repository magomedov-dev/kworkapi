"""Заказы: заказы исполнителя и покупателя."""

from __future__ import annotations

from kworkapi.exceptions import KworkAPIError
from kworkapi.resources.base import Resource

# Код ответа «нет заказов» — приложение отдаёт его как ошибку, мы трактуем как пустой список.
_EMPTY_ORDERS_CODE = 151


class OrdersResource(Resource):
    async def worker(self, *, filter: str = "all") -> list:
        """Заказы текущего пользователя как исполнителя (`/workerOrders`)."""
        try:
            body = await self._call("workerOrders", data={"filter": filter})
        except KworkAPIError as exc:
            if exc.code == _EMPTY_ORDERS_CODE:
                return []
            raise
        payload = self._payload(body)
        return payload if isinstance(payload, list) else []

    async def payer(self, *, filter: str = "all", company_orders: int = 0) -> list:
        """Заказы текущего пользователя как покупателя (`/payerOrders`)."""
        try:
            body = await self._call(
                "payerOrders", data={"filter": filter, "company_orders": company_orders}
            )
        except KworkAPIError as exc:
            if exc.code == _EMPTY_ORDERS_CODE:
                return []
            raise
        payload = self._payload(body)
        return payload if isinstance(payload, list) else []
