"""Модели сообщений: диалоги и сообщения переписки."""

from __future__ import annotations

from kworkapi.models.base import KworkModel


class LastMessage(KworkModel):
    unread: bool | None = None
    fromUsername: str | None = None
    fromUserId: int | None = None
    type: str | None = None
    time: int | None = None
    message: str | None = None
    originText: str | None = None
    profilePicture: str | None = None


class Dialog(KworkModel):
    """Диалог (ответ `/dialogs` — список, `/getDialog` — один)."""

    user_id: int | None = None
    username: str | None = None
    profilepicture: str | None = None
    unread: bool | None = None
    unread_count: int | None = None
    last_message: str | None = None
    time: int | None = None
    is_online: bool | None = None
    lastOnlineTime: int | None = None
    link: str | None = None
    status: str | None = None
    blocked_by_user: bool | None = None
    allowedDialog: bool | None = None
    has_active_order: bool | None = None
    archived: bool | None = None
    isStarred: bool | None = None
    is_important: bool | None = None
    has_answer: bool | None = None
    draft: str | None = None
    lastMessage: LastMessage | None = None


class InboxMessage(KworkModel):
    """Сообщение переписки (ответ `/getInboxTracks`)."""

    message_id: int | None = None
    conversation_id: int | None = None
    entity_type: int | None = None
    from_id: int | None = None
    from_username: str | None = None
    to_id: int | None = None
    to_username: str | None = None
    message: str | None = None
    time: int | None = None
    unread: bool | None = None
    type: str | None = None
    status: str | None = None
    forwarded: bool | None = None
    created_order_id: int | None = None
    message_page: int | None = None


class SentMessage(KworkModel):
    """Результат отправки сообщения (ответ `/inboxCreate`)."""

    id: int | None = None
    conversation_id: int | None = None
    type: str | None = None
    page: int | None = None
    time: int | None = None
    mass_mailing_notification: bool | None = None
