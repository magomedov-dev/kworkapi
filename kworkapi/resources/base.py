"""Базовый класс ресурса + хелперы разбора ответа в модели."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from kworkapi.models.common import Page, Paging

if TYPE_CHECKING:
    from kworkapi.client import KworkClient

T = TypeVar("T")


class Resource:
    """Группа методов API. Делегирует низкоуровневые вызовы клиенту."""

    def __init__(self, client: KworkClient) -> None:
        self._client = client

    async def _call(
        self,
        method: str,
        *,
        data: dict[str, Any] | None = None,
        auth: bool = True,
        multipart: bool = False,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._client.call(
            method, data=data, auth=auth, multipart=multipart, files=files
        )

    # --- разбор ответа в модели ----------------------------------------

    @staticmethod
    def _payload(body: dict[str, Any]) -> Any:
        """Полезная нагрузка: содержимое ``response`` (или весь body, если его нет)."""
        if "response" in body:
            return body["response"]
        return body

    def _model(self, body: dict[str, Any], model: type[T]) -> T:
        """Распарсить полезную нагрузку в одну модель."""
        payload: Any = self._payload(body)
        return model(**payload)

    def _list(self, body: dict[str, Any], model: type[T]) -> list[T]:
        """Распарсить полезную нагрузку-список в список моделей."""
        payload: Any = self._payload(body)
        raw: list[Any] = cast("list[Any]", payload) if isinstance(payload, list) else []
        return [model(**item) for item in raw]

    def _page(
        self, body: dict[str, Any], model: type[T], *, items_key: str | None = None
    ) -> Page[T]:
        """Собрать страницу: элементы (из ``response`` или ``response[items_key]``) + paging.

        :param items_key: если элементы лежат в подполе response (например "kworks").
        """
        payload: Any = self._payload(body)
        total: int | None = None
        raw: list[Any]
        if items_key and isinstance(payload, dict):
            src = cast("dict[str, Any]", payload)
            raw = src.get(items_key) or []
            count = src.get(f"{items_key}_count")
            total = count if isinstance(count, int) else None
        elif isinstance(payload, list):
            raw = cast("list[Any]", payload)
        else:
            raw = []
        items: list[T] = [model(**item) for item in raw]
        paging_raw: Any = body.get("paging")
        paging = Paging(**cast("dict[str, Any]", paging_raw)) if isinstance(paging_raw, dict) else None
        if total is None and paging is not None:
            total = paging.total
        return Page(items=items, paging=paging, total=total)
