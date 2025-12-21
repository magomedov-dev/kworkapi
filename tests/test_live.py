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


def _creds() -> tuple[str, str]:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    env = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    login = os.environ.get("KWORK_LOGIN") or env.get("KWORK_LOGIN")
    password = os.environ.get("KWORK_PASSWORD") or env.get("KWORK_PASSWORD")
    if not login or not password:
        pytest.skip("нет KWORK_LOGIN/KWORK_PASSWORD")
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
