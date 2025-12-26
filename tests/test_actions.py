"""Тесты действий (Фаза 4) на замоканных ответах (respx)."""

from __future__ import annotations

import httpx
import respx

from kworkapi import KworkClient
from kworkapi.auth import Session

BASE = "https://api.kwork.ru/"


def client() -> KworkClient:
    return KworkClient.from_session(Session(token="T", uad="U"), base_url=BASE, retry_backoff=0.0)


def ok(payload=None):
    body = {"success": True}
    if payload is not None:
        body["response"] = payload
    return httpx.Response(200, json=body)


@respx.mock
async def test_set_starred_fields():
    route = respx.post(BASE + "setDialogStarred").mock(return_value=ok({"message": "ok"}))
    async with client() as kw:
        await kw.messages.set_starred(17828374, True)
        body = route.calls.last.request.content
        assert b"userId=17828374" in body and b"isStarred=1" in body


@respx.mock
async def test_block_and_unblock():
    rb = respx.post(BASE + "blockDialog").mock(return_value=ok({"message": "blocked"}))
    ru = respx.post(BASE + "unblockDialog").mock(return_value=ok({"message": "unblocked"}))
    async with client() as kw:
        await kw.messages.block(5)
        await kw.messages.unblock(5)
        assert b"blockUserId=5" in rb.calls.last.request.content
        assert b"blockUserId=5" in ru.calls.last.request.content


@respx.mock
async def test_edit_and_delete_message():
    re_ = respx.post(BASE + "inboxEdit").mock(return_value=ok())
    rd = respx.post(BASE + "inboxDelete").mock(return_value=ok())
    async with client() as kw:
        await kw.messages.edit(402350047, "fixed")
        await kw.messages.delete(402350047)
        assert b"id=402350047" in re_.calls.last.request.content
        assert b"text=fixed" in re_.calls.last.request.content
        assert b"id=402350047" in rd.calls.last.request.content


@respx.mock
async def test_create_offer_is_multipart_with_fields():
    route = respx.post(BASE + "api/offer/createoffer").mock(
        return_value=httpx.Response(200, json={"success": True, "data": None, "redirect": "/projects"})
    )
    async with client() as kw:
        await kw.exchange.create_offer(3202099, "Сделаю", price=5000, duration=3)
        req = route.calls.last.request
        assert req.headers["content-type"].startswith("multipart/form-data")
        body = req.content
        assert b'name="wantId"' in body and b"3202099" in body
        assert b'name="offerType"' in body and b"custom" in body
        assert b'name="kwork_price"' in body and b"5000" in body
        assert b'name="kwork_duration"' in body and b"3" in body
        # общие поля тоже уходят как части multipart
        assert b'name="token"' in body and b'name="uad"' in body


@respx.mock
async def test_delete_offer():
    route = respx.post(BASE + "api/offer/deleteoffer").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    async with client() as kw:
        await kw.exchange.delete_offer(39092325)
        assert b"id=39092325" in route.calls.last.request.content


@respx.mock
async def test_update_settings_fields():
    route = respx.post(BASE + "updateSettings").mock(return_value=ok({"message": "Сохранено"}))
    async with client() as kw:
        res = await kw.account.update_settings(username="gumangee2", fullname="Хамид", city_id=930)
        assert res["message"] == "Сохранено"
        body = route.calls.last.request.content
        assert b"username=gumangee2" in body and b"cityId=930" in body


@respx.mock
async def test_kworks_mark_favorite_fields():
    route = respx.post(BASE + "markKworkAsFavorite").mock(return_value=ok())
    async with client() as kw:
        await kw.kworks.mark_favorite(52214751, True)
        body = route.calls.last.request.content
        assert b"kwork_id=52214751" in body and b"is_favorite=1" in body


@respx.mock
async def test_set_taking_orders():
    route = respx.post(BASE + "setTakingOrders").mock(return_value=ok())
    async with client() as kw:
        await kw.account.set_taking_orders("stop")
        assert b"status=stop" in route.calls.last.request.content
