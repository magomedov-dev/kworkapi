"""Сообщения и чаты: диалоги, история переписки, отправка."""

from __future__ import annotations

import os

from kworkapi.models.dialog import Dialog, InboxMessage, SentMessage
from kworkapi.resources.base import Resource


def _message_key() -> str:
    """Случайный идемпотентный ключ сообщения (как в приложении)."""
    return os.urandom(6).hex()[:10]


class MessagesResource(Resource):
    async def dialogs(self, *, page: int = 1, filter: str = "all") -> list[Dialog]:
        """Список диалогов (`/dialogs`)."""
        data = {"page": page, "filter": filter}
        return self._list(await self._call("dialogs", data=data), Dialog)

    async def dialog(self, user_id: int) -> Dialog:
        """Метаданные диалога с пользователем (`/getDialog`)."""
        return self._model(await self._call("getDialog", data={"id": user_id}), Dialog)

    async def history(
        self, user_id: int, *, limit: int = 30, direction: int = 0
    ) -> list[InboxMessage]:
        """История переписки (`/getInboxTracks`).

        Пагинация — через `direction` (лента сообщений), а не страницами.
        """
        data = {"userId": user_id, "limit": limit, "direction": direction, "makeOnline": 0}
        return self._list(await self._call("getInboxTracks", data=data), InboxMessage)

    async def send(self, user_id: int, text: str) -> SentMessage:
        """Отправить сообщение пользователю (`/inboxCreate`)."""
        data = {"user_id": user_id, "text": text, "message_key": _message_key()}
        return self._model(await self._call("inboxCreate", data=data), SentMessage)

    async def mark_read(self, user_id: int) -> dict:
        """Отметить диалог прочитанным (`/inboxRead`)."""
        return await self._call("inboxRead", data={"userId": user_id})
