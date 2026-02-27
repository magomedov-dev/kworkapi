"""Сообщения и чаты: диалоги, история переписки, отправка."""

from __future__ import annotations

from typing import Any

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

    async def mark_read(self, user_id: int) -> dict[str, Any]:
        """Отметить диалог прочитанным (`/inboxRead`)."""
        return await self._call("inboxRead", data={"userId": user_id})

    async def mark_unread(self, user_id: int) -> dict[str, Any]:
        """Отметить диалог непрочитанным (`/unreadDialog`)."""
        return await self._call("unreadDialog", data={"user_id": user_id})

    async def set_starred(self, user_id: int, starred: bool = True) -> dict[str, Any]:
        """Добавить/убрать диалог из избранного (`/setDialogStarred`)."""
        data = {"userId": user_id, "isStarred": 1 if starred else 0}
        return self._payload(await self._call("setDialogStarred", data=data))

    async def block(self, user_id: int) -> dict[str, Any]:
        """Заблокировать диалог с пользователем (`/blockDialog`)."""
        return self._payload(await self._call("blockDialog", data={"blockUserId": user_id}))

    async def unblock(self, user_id: int) -> dict[str, Any]:
        """Разблокировать диалог (`/unblockDialog`)."""
        return self._payload(await self._call("unblockDialog", data={"blockUserId": user_id}))

    async def edit(self, message_id: int, text: str, *, reply_message_id: int | None = None) -> dict[str, Any]:
        """Отредактировать сообщение (`/inboxEdit`)."""
        data = {"id": message_id, "text": text, "reply_message_id": reply_message_id}
        return await self._call("inboxEdit", data=data)

    async def delete(self, message_id: int) -> dict[str, Any]:
        """Удалить сообщение (`/inboxDelete`)."""
        return await self._call("inboxDelete", data={"id": message_id})

    async def search(self, text: str, *, user_id: int = 0, page: int = 1) -> dict[str, Any]:
        """Поиск по сообщениям (`/searchInboxes`)."""
        data = {"text": text, "userId": user_id, "page": page}
        return await self._call("searchInboxes", data=data)

    # --- голосовые сообщения -------------------------------------------

    async def voice_transcription(self, conversation_id: int) -> dict[str, Any]:
        """Транскрипция голосового сообщения (`/getVoiceMessageTranscription`)."""
        data = {"conversation_id": conversation_id}
        return await self._call("getVoiceMessageTranscription", data=data)

    async def mark_voice_heard(self, conversation_id: int) -> dict[str, Any]:
        """Отметить голосовое прослушанным (`/markVoiceMessageHeard`)."""
        return await self._call("markVoiceMessageHeard", data={"conversation_id": conversation_id})

    async def voice_convert_status(self, file_id: int) -> dict[str, Any]:
        """Статус конвертации голосового (`/getVoiceMessageConvertStatus`)."""
        return await self._call("getVoiceMessageConvertStatus", data={"file_id": file_id})

    # --- прочее --------------------------------------------------------

    async def get_message(self, conversation_id: int) -> dict[str, Any]:
        """Получить одно сообщение по conversation_id (`/inboxTrackMessage`)."""
        return self._payload(
            await self._call("inboxTrackMessage", data={"conversationId": conversation_id})
        )

    async def complain(self, message_id: int, comment: str) -> dict[str, Any]:
        """Пожаловаться на сообщение (`/inboxComplainMessage`)."""
        data = {"message_id": message_id, "comment": comment}
        return await self._call("inboxComplainMessage", data=data)

    async def mark_tracks_read(self, user_id: int, conversation_ids: list[int]) -> dict[str, Any]:
        """Отметить сообщения прочитанными (`/markInboxTracksAsRead`)."""
        data = {"userId": user_id, "conversationIds[]": conversation_ids}
        return await self._call("markInboxTracksAsRead", data=data)

    async def hide_dialog(self, user_id: int, *, restore: bool = False) -> dict[str, Any]:
        """Скрыть/восстановить диалог (`/hideDialog`)."""
        data = {"userId": user_id, "isRestore": 1 if restore else 0}
        return await self._call("hideDialog", data=data)

    async def send_status(self, user_id: int, *, order_id: int = 0, status: str = "typing") -> dict[str, Any]:
        """Отправить статус взаимодействия (печатает и т.п., `/sendUserStatus`)."""
        data = {"user_id": user_id, "orderId": order_id, "status": status}
        return await self._call("sendUserStatus", data=data)
