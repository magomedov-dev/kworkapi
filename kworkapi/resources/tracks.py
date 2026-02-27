"""Треки заказа (лента событий/сообщений внутри заказа)."""

from __future__ import annotations

from typing import Any

from collections.abc import Sequence

from kworkapi.resources.base import Resource


class TracksResource(Resource):
    async def list(
        self, order_id: int, *, track_id: int | None = None, limit: int = 30, direction: int = 0
    ) -> dict[str, Any]:
        """Лента треков заказа (`/getTracks`)."""
        data = {"orderId": order_id, "trackId": track_id, "limit": limit, "direction": direction}
        return await self._call("getTracks", data=data)

    async def search(self, text: str, order_id: int, *, page: int = 1) -> dict[str, Any]:
        """Поиск по трекам заказа (`/searchOrderTracks`)."""
        return await self._call("searchOrderTracks", data={"text": text, "orderId": order_id, "page": page})

    async def edit(self, track_id: int, text: str, *, quote_id: int | None = None) -> dict[str, Any]:
        """Изменить трек (`/trackEdit`)."""
        return await self._call("trackEdit", data={"id": track_id, "text": text, "quoteId": quote_id})

    async def delete(self, track_id: int) -> dict[str, Any]:
        """Удалить трек (`/trackDelete`)."""
        return await self._call("trackDelete", data={"id": track_id})

    async def read(self, ids: Sequence[int]) -> dict[str, Any]:
        """Отметить треки прочитанными (`/trackRead`)."""
        return await self._call("trackRead", data={"ids[]": list(ids)})
