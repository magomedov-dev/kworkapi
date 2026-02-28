"""Тесты FastAPI-сервиса: подменяем сетевой транспорт клиента на фейковый."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api import deps
from api.main import app
from kworkapi import KworkClient
from kworkapi.auth import Session


class FakeTransport:
    """Заглушка транспорта: возвращает заранее заданные ответы по имени метода."""

    def __init__(self, responses: dict[str, dict]):
        self.responses = responses
        self.uad = "FAKEUAD"
        self.base_url = "https://api.kwork.ru/"
        self.calls: list[tuple[str, dict]] = []

    async def call(self, method, *, data=None, token=None, auth=True, multipart=False, files=None):
        self.calls.append((method, data or {}))
        if method not in self.responses:
            raise AssertionError(f"неожиданный вызов метода {method}")
        value = self.responses[method]
        if isinstance(value, Exception):
            raise value
        return value

    def current_slrememberme(self):
        return ""

    async def aclose(self):
        pass


def _override(responses: dict[str, dict], *, anon: bool = False) -> FakeTransport:
    transport = FakeTransport(responses)

    def factory():
        if anon:
            return KworkClient(transport=transport)
        return KworkClient(session=Session(token="T", uad="U"), transport=transport)

    dep = deps.get_anon_client if anon else deps.get_client
    app.dependency_overrides[dep] = factory
    return transport


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def ok(payload=None):
    body = {"success": True}
    if payload is not None:
        body["response"] = payload
    return body


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_requires_token():
    # без X-Kwork-Token авторизованный эндпоинт отдаёт 401
    r = client.get("/account/me")
    assert r.status_code == 401


def test_login_returns_token():
    _override({"signIn": ok({"token": "TOK123", "expired": 100, "need_2fa": False})}, anon=True)
    r = client.post("/auth/login", json={"login": "u", "password": "p"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["token"] == "TOK123"


def test_login_captcha_then_solve():
    from kworkapi.exceptions import KworkAPIError

    _override(
        {
            "signIn": KworkAPIError("Подтвердите, что вы не робот", code=118),
            "signInWithCaptcha": {
                "success": True,
                "response": {"token": "TOK", "expired": 100},
                "recaptcha_pass_token": "PASS",
            },
        },
        anon=True,
    )
    # шаг 1: логин → требуется капча
    r1 = client.post("/auth/login", json={"login": "u@e.com", "password": "p"})
    assert r1.status_code == 200
    b1 = r1.json()
    assert b1["status"] == "captcha"
    assert b1["sitekey"] and b1["page_url"].endswith("/captcha_only")
    # шаг 2: решение капчи → токен
    r2 = client.post(
        "/auth/login/captcha",
        json={"login": "u@e.com", "password": "p", "solution": "g-token"},
    )
    assert r2.status_code == 200
    b2 = r2.json()
    assert b2["status"] == "ok" and b2["token"] == "TOK"
    assert b2["recaptcha_pass_token"] == "PASS"


def test_account_me():
    _override({"actor": ok({"id": 1548151, "username": "gumangee2", "type": "payer"})})
    r = client.get("/account/me", headers={"X-Kwork-Token": "T"})
    assert r.status_code == 200
    assert r.json()["id"] == 1548151


def test_search_kworks():
    _override({"search": ok({"kworks_count": 1, "kworks": [{"id": 9, "title": "x"}]})})
    r = client.get("/search/kworks", params={"q": "logo"}, headers={"X-Kwork-Token": "T"})
    assert r.status_code == 200
    assert r.json()["kworks"][0]["id"] == 9


def test_messages_send():
    t = _override({"inboxCreate": ok({"id": 42, "conversation_id": 7})})
    r = client.post("/messages/send", json={"user_id": 5, "text": "hi"}, headers={"X-Kwork-Token": "T"})
    assert r.status_code == 200 and r.json()["id"] == 42
    method, data = t.calls[-1]
    assert method == "inboxCreate" and data["user_id"] == 5


def test_auth_error_maps_to_401():
    from kworkapi.exceptions import KworkAuthError

    class Boom(FakeTransport):
        async def call(self, *a, **k):
            raise KworkAuthError("bad token")

    def factory():
        return KworkClient(session=Session(token="T", uad="U"), transport=Boom({}))

    app.dependency_overrides[deps.get_client] = factory
    r = client.get("/account/me", headers={"X-Kwork-Token": "T"})
    assert r.status_code == 401
    assert "error" in r.json()


def test_rate_limit_maps_to_429():
    from kworkapi.exceptions import KworkRateLimitError

    class Boom(FakeTransport):
        async def call(self, *a, **k):
            raise KworkRateLimitError("403 anti-bot", code=403)

    def factory():
        return KworkClient(session=Session(token="T", uad="U"), transport=Boom({}))

    app.dependency_overrides[deps.get_client] = factory
    r = client.get("/account/me", headers={"X-Kwork-Token": "T"})
    assert r.status_code == 429


def test_order_details_endpoint():
    _override({"getOrderDetails": ok({"id": 100, "status": "work"})})
    r = client.get("/orders/100", headers={"X-Kwork-Token": "T"})
    assert r.status_code == 200 and r.json()["id"] == 100


def test_file_upload_endpoint():
    t = _override({"fileUpload": ok({"id": 7})})
    r = client.post(
        "/files/upload",
        files={"file": ("doc.txt", b"data", "text/plain")},
        headers={"X-Kwork-Token": "T"},
    )
    assert r.status_code == 200
    assert t.calls[-1][0] == "fileUpload"


def test_openapi_has_all_groups():
    spec = client.get("/openapi.json").json()
    tags = {t for path in spec["paths"].values() for op in path.values() for t in op.get("tags", [])}
    expected = {"auth", "account", "catalog", "search", "exchange", "users",
                "kworks", "orders", "messages", "files"}
    assert expected <= tags
