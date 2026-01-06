"""Тесты транспорта: разбор успешных и ошибочных ответов, ретраи."""

from __future__ import annotations

import httpx
import pytest
import respx

from kworkapi.exceptions import KworkAPIError, KworkAuthError, KworkRateLimitError
from kworkapi.transport import Transport

BASE = "https://api.kwork.ru/"


@pytest.fixture
async def transport():
    t = Transport(base_url=BASE, retry_backoff=0.0)
    yield t
    await t.aclose()


@respx.mock
async def test_call_success_returns_json(transport):
    respx.post(BASE + "ping").mock(return_value=httpx.Response(200, json={"success": True, "x": 1}))
    body = await transport.call("ping")
    assert body == {"success": True, "x": 1}


@respx.mock
async def test_token_injected_into_form(transport):
    route = respx.post(BASE + "me").mock(return_value=httpx.Response(200, json={"success": True}))
    await transport.call("me", token="T123")
    assert b"token=T123" in route.calls.last.request.content


@respx.mock
async def test_api_error_raised(transport):
    respx.post(BASE + "boom").mock(
        return_value=httpx.Response(200, json={"success": False, "error": "что-то пошло не так"})
    )
    with pytest.raises(KworkAPIError):
        await transport.call("boom")


@respx.mock
async def test_auth_error_detected_from_message(transport):
    respx.post(BASE + "secure").mock(
        return_value=httpx.Response(200, json={"success": False, "error": "Invalid token"})
    )
    with pytest.raises(KworkAuthError):
        await transport.call("secure")


@respx.mock
async def test_rate_limit_after_retries(transport):
    respx.post(BASE + "spam").mock(return_value=httpx.Response(429))
    with pytest.raises(KworkRateLimitError):
        await transport.call("spam")


@respx.mock
async def test_403_maps_to_rate_limit(transport):
    respx.post(BASE + "signIn").mock(return_value=httpx.Response(403))
    with pytest.raises(KworkRateLimitError):
        await transport.call("signIn", auth=False)


async def test_throttle_requests_wait(monkeypatch):
    import kworkapi.transport as tmod

    waits: list[float] = []

    async def fake_sleep(seconds):
        waits.append(seconds)

    monkeypatch.setattr(tmod.asyncio, "sleep", fake_sleep)
    t = Transport(min_request_interval=0.5)
    await t._await_throttle()  # первый — без ожидания
    await t._await_throttle()  # второй — должен запросить паузу
    await t.aclose()
    assert waits and waits[-1] > 0


@respx.mock
async def test_retries_on_network_error_then_succeeds(transport):
    route = respx.post(BASE + "flaky")
    route.side_effect = [
        httpx.ConnectError("boom"),
        httpx.Response(200, json={"success": True, "ok": 1}),
    ]
    body = await transport.call("flaky")
    assert body == {"success": True, "ok": 1}
    assert route.call_count == 2
