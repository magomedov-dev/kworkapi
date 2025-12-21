"""Базовый класс ресурса + хелперы разбора ответа в модели."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from kworkapi.models.common import Page, Paging

if TYPE_CHECKING:
    from kworkapi.client import KworkClient

T = TypeVar("T")


class Resource:
    """Группа методов API. Делегирует низкоуровневые вызовы клиенту."""

    def __init__(self, client: "KworkClient") -> None:
        self._client = client

    async def _call(
        self, method: str, *, data: dict[str, Any] | None = None, auth: bool = True
    ) -> dict:
        return await self._client.call(method, data=data, auth=auth)

    # --- разбор ответа в модели ----------------------------------------

    @staticmethod
    def _payload(body: dict) -> Any:
        """Полезная нагрузка: содержимое `response` (или весь body, если его нет)."""
        if isinstance(body, dict) and "response" in body:
            return body["response"]
        return body

    def _model(self, body: dict, model: type[T]) -> T:
        """Распарсить полезную нагрузку в одну модель."""
        return model(**self._payload(body))

    def _list(self, body: dict, model: type[T]) -> list[T]:
        """Распарсить полезную нагрузку-список в список моделей."""
        payload = self._payload(body)
        return [model(**x) for x in (payload or [])]

    def _page(
        self, body: dict, model: type[T], *, items_key: str | None = None
    ) -> Page[T]:
        """Собрать страницу: элементы (из response или response[items_key]) + paging.

        :param items_key: если элементы лежат в подполе response (например "kworks").
        """
        payload = self._payload(body)
        if items_key and isinstance(payload, dict):
            raw_items = payload.get(items_key, [])
            total = payload.get(f"{items_key}_count")
        else:
            raw_items = payload if isinstance(payload, list) else []
            total = None
        items = [model(**x) for x in (raw_items or [])]
        paging_raw = body.get("paging") if isinstance(body, dict) else None
        paging = Paging(**paging_raw) if isinstance(paging_raw, dict) else None
        if total is None and paging is not None:
            total = paging.total
        return Page[model](items=items, paging=paging, total=total)
