"""Тесты read-ресурсов на замоканных ответах (respx) + разбор в модели."""

from __future__ import annotations

import httpx
import respx

from kworkapi import KworkClient
from kworkapi.auth import Session
from kworkapi.models import Actor, Dialog, ExchangeInfo, Offer, SentMessage
from kworkapi.models.kwork import KworksResult

BASE = "https://api.kwork.ru/"


def client() -> KworkClient:
    return KworkClient.from_session(Session(token="T", uad="U"), base_url=BASE, retry_backoff=0.0)


def ok(payload):
    return httpx.Response(200, json={"success": True, "response": payload})


@respx.mock
async def test_account_me_parses_actor():
    respx.post(BASE + "actor").mock(
        return_value=ok({"id": 1548151, "username": "u", "type": "payer", "free_amount": 0, "currency": "₽"})
    )
    async with client() as kw:
        me = await kw.account.me()
        assert isinstance(me, Actor)
        assert me.id == 1548151 and me.type == "payer"


@respx.mock
async def test_catalog_categories_tree():
    respx.post(BASE + "categories").mock(
        return_value=ok([{"id": 15, "name": "Дизайн", "subcategories": [{"id": 25, "name": "Лого"}]}])
    )
    async with client() as kw:
        cats = await kw.catalog.categories()
        assert cats[0].name == "Дизайн"
        assert cats[0].subcategories[0].id == 25


@respx.mock
async def test_search_kworks_sends_query_and_parses():
    route = respx.post(BASE + "search").mock(
        return_value=ok({"kworks_count": 2, "kworks": [
            {"id": 1, "title": "a", "price": 500, "worker": {"id": 9, "username": "w"}},
            {"id": 2, "title": "b", "price": 10},
        ]})
    )
    async with client() as kw:
        res = await kw.search.kworks("logo", category_id=196, page=2)
        assert isinstance(res, KworksResult)
        assert res.kworks_count == 2
        assert res.kworks[0].worker.username == "w"
        body = route.calls.last.request.content
        assert b"query=logo" in body and b"categoryId=196" in body and b"page=2" in body


@respx.mock
async def test_catalog_favorites_page_with_paging():
    respx.post(BASE + "favoriteKworks").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "response": [{"id": 1, "title": "x"}],
            "paging": {"page": 1, "total": 1, "limit": 30, "pages": 1},
        })
    )
    async with client() as kw:
        page = await kw.catalog.favorites()
        assert len(page) == 1 and page.items[0].id == 1
        assert page.paging.total == 1


@respx.mock
async def test_messages_dialogs_list():
    respx.post(BASE + "dialogs").mock(
        return_value=ok([{"user_id": 5, "username": "bob", "unread": True}])
    )
    async with client() as kw:
        dialogs = await kw.messages.dialogs()
        assert isinstance(dialogs[0], Dialog)
        assert dialogs[0].username == "bob"


@respx.mock
async def test_messages_send_fields_and_model():
    route = respx.post(BASE + "inboxCreate").mock(
        return_value=ok({"id": 42, "conversation_id": 7, "type": "message"})
    )
    async with client() as kw:
        sent = await kw.messages.send(17828374, "Hello")
        assert isinstance(sent, SentMessage) and sent.id == 42
        body = route.calls.last.request.content
        assert b"user_id=17828374" in body and b"text=Hello" in body and b"message_key=" in body


@respx.mock
async def test_exchange_info_without_success_wrapper():
    # /exchangeInfo возвращает плоский объект без success/response
    respx.post(BASE + "exchangeInfo").mock(
        return_value=httpx.Response(200, json={"archived_count": 0, "exchange_response_count": 2})
    )
    async with client() as kw:
        info = await kw.exchange.info()
        assert isinstance(info, ExchangeInfo)
        assert info.exchange_response_count == 2


@respx.mock
async def test_exchange_my_offers_list():
    respx.post(BASE + "offers").mock(
        return_value=ok([{"id": 1, "price": 9000, "want_id": 3, "project": {"id": 3, "title": "p"}}])
    )
    async with client() as kw:
        offers = await kw.exchange.my_offers()
        assert isinstance(offers[0], Offer)
        assert offers[0].project.id == 3


@respx.mock
async def test_orders_worker_empty_code_151_returns_list():
    respx.post(BASE + "workerOrders").mock(
        return_value=httpx.Response(200, json={"success": False, "error": "nothing booked", "error_code": 151})
    )
    async with client() as kw:
        assert await kw.orders.worker() == []
