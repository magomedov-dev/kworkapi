"""Управление своими kwork'ами (исполнитель) и пометками каталога.

Имена методов подтверждены кодом UserService.
"""

from __future__ import annotations

from kworkapi.resources.base import Resource


class KworksResource(Resource):
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
