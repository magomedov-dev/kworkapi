"""Опциональный интеграционный тест против живого api.kwork.ru.

По умолчанию ПРОПУСКАЕТСЯ. Запуск:

    KWORK_LIVE=1 .venv/bin/python -m pytest tests/test_live.py -v

Важно: kwork ограничивает частые входы (анти-бот, HTTP 403). Поэтому тест
делает РОВНО ОДИН вход и переиспользует сессию для всех проверок. Только чтение —
аккаунт не мутируется. Креды берутся из .env (KWORK_LOGIN / KWORK_PASSWORD).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from kworkapi import KworkClient
from kworkapi.models import Actor, ExchangeInfo
from kworkapi.models.kwork import KworksResult

pytestmark = pytest.mark.skipif(
    os.environ.get("KWORK_LIVE") != "1",
    reason="живые тесты выключены (установите KWORK_LIVE=1)",
)


def _env() -> dict:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    env = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


def _creds() -> tuple[str, str]:
    env = _env()
    login = os.environ.get("KWORK_LOGIN") or env.get("KWORK_LOGIN")
    password = os.environ.get("KWORK_PASSWORD") or env.get("KWORK_PASSWORD")
    if not login or not password:
        pytest.skip("нет KWORK_LOGIN/KWORK_PASSWORD")
    return login, password


def _creds2() -> tuple[str, str]:
    env = _env()
    login = os.environ.get("KWORK_LOGIN2") or env.get("KWORK_LOGIN2")
    password = os.environ.get("KWORK_PASSWORD2") or env.get("KWORK_PASSWORD2")
    if not login or not password:
        pytest.skip("нет второго аккаунта (KWORK_LOGIN2)")
    return login, password


async def test_live_read_flow():
    """Один вход + чтение профиля, каталога, поиска, диалогов, биржи."""
    login, password = _creds()
    async with KworkClient() as kw:
        session = await kw.login(login, password)
        assert session.token and session.is_authenticated

        me = await kw.account.me()
        assert isinstance(me, Actor) and me.id

        cats = await kw.catalog.categories()
        assert cats and cats[0].subcategories is not None

        res = await kw.search.kworks("logo", limit=5)
        assert isinstance(res, KworksResult) and res.kworks
        assert res.kworks[0].id

        dialogs = await kw.messages.dialogs()
        assert isinstance(dialogs, list)

        info = await kw.exchange.info()
        assert isinstance(info, ExchangeInfo)


async def test_live_messaging_between_own_accounts():
    """Безопасные обратимые действия: сообщение между своими аккаунтами + звезда.

    Использует второй аккаунт (KWORK_LOGIN2), чтобы не писать посторонним.
    """
    login1, pass1 = _creds()
    login2, pass2 = _creds2()

    async with KworkClient() as kw2:
        await kw2.login(login2, pass2)
        uid2 = (await kw2.account.me()).id

    async with KworkClient() as kw1:
        await kw1.login(login1, pass1)
        sent = await kw1.messages.send(uid2, "Тест KworkAPI: автоматическое сообщение.")
        assert sent.id and sent.conversation_id
        # звезда вкл/выкл — обратимо
        await kw1.messages.set_starred(uid2, True)
        await kw1.messages.set_starred(uid2, False)
        history = await kw1.messages.history(uid2, limit=3)
        assert isinstance(history, list)
