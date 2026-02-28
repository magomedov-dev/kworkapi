"""Тесты капча-челленджа: error_code 118 → LoginChallenge → solve_captcha."""

from __future__ import annotations

import httpx
import respx

from kworkapi import KworkClient, LoginChallenge, Session
from kworkapi.auth import RECAPTCHA_SITEKEY

BASE = "https://api.kwork.ru/"


def captcha_response():
    return httpx.Response(
        200,
        json={"success": False, "error": "Подтвердите, что вы не робот", "error_code": 118},
    )


def signin_ok(token="TOK", pass_token="PASS123"):
    return httpx.Response(
        200,
        json={
            "success": True,
            "response": {"token": token, "expired": 31536000, "need_2fa": False},
            "recaptcha_pass_token": pass_token,
        },
    )


@respx.mock
async def test_login_returns_challenge_on_118():
    respx.post(BASE + "signIn").mock(return_value=captcha_response())
    async with KworkClient(base_url=BASE, retry_backoff=0.0) as kw:
        result = await kw.login("marcusplay@mail.ru", "secret")
        assert isinstance(result, LoginChallenge)
        assert result.kind == "recaptcha"
        assert result.provider == "recaptcha"
        assert result.sitekey == RECAPTCHA_SITEKEY
        assert result.page_url == "https://kwork.ru/captcha_only"
        assert result.login == "marcusplay@mail.ru"
        # сессия не установлена, пока капча не решена
        assert not kw.is_authenticated


@respx.mock
async def test_solve_captcha_completes_login():
    respx.post(BASE + "signIn").mock(return_value=captcha_response())
    route = respx.post(BASE + "signInWithCaptcha").mock(return_value=signin_ok())
    async with KworkClient(base_url=BASE, retry_backoff=0.0) as kw:
        challenge = await kw.login("user@example.com", "secret")
        assert isinstance(challenge, LoginChallenge)
        session = await kw.solve_captcha(challenge, "g-recaptcha-token-xyz")
        assert isinstance(session, Session)
        assert session.token == "TOK"
        assert session.recaptcha_pass_token == "PASS123"
        assert kw.is_authenticated
        # отправлены креды + решение капчи
        body = route.calls.last.request.content
        assert b"login=user%40example.com" in body
        assert b"g-recaptcha-response=g-recaptcha-token-xyz" in body


@respx.mock
async def test_login_reuses_recaptcha_pass_token():
    route = respx.post(BASE + "signIn").mock(return_value=signin_ok(pass_token="REUSED"))
    sess = Session(token="OLD", uad="U", recaptcha_pass_token="REUSED")
    async with KworkClient.from_session(sess, base_url=BASE, retry_backoff=0.0) as kw:
        result = await kw.login("user", "pass")
        assert isinstance(result, Session)
        # сохранённый pass-токен подставлен в запрос signIn
        assert b"recaptcha_pass_token=REUSED" in route.calls.last.request.content


def test_session_roundtrip_includes_pass_token():
    sess = Session(token="t", uad="u", recaptcha_pass_token="p")
    restored = Session.from_dict(sess.to_dict())
    assert restored.recaptcha_pass_token == "p"
