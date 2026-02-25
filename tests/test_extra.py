"""Тесты расширенного покрытия (полнота API): доп. методы ресурсов."""

from __future__ import annotations

import httpx
import respx

from kworkapi import KworkClient
from kworkapi.auth import Session

BASE = "https://api.kwork.ru/"


def client() -> KworkClient:
    return KworkClient.from_session(Session(token="T", uad="U"), base_url=BASE, retry_backoff=0.0)


def anon() -> KworkClient:
    return KworkClient(base_url=BASE, retry_backoff=0.0)


def ok(payload=None):
    body = {"success": True}
    if payload is not None:
        body["response"] = payload
    return httpx.Response(200, json=body)


@respx.mock
async def test_account_geo_and_phone():
    respx.post(BASE + "countries").mock(return_value=ok([{"id": 1, "name": "Россия"}]))
    rc = respx.post(BASE + "cities").mock(return_value=ok([{"id": 930}]))
    rp = respx.post(BASE + "addPhoneNumber").mock(return_value=ok({"timeout": 60}))
    async with client() as kw:
        assert (await kw.account.countries())[0]["name"] == "Россия"
        await kw.account.cities(1)
        await kw.account.add_phone("+79990000000")
        assert b"countryId=1" in rc.calls.last.request.content
        assert b"phone=" in rp.calls.last.request.content


@respx.mock
async def test_account_notifications_received_list_field():
    route = respx.post(BASE + "notificationsReceived").mock(return_value=ok())
    async with client() as kw:
        await kw.account.notifications_received([11, 22])
        body = route.calls.last.request.content
        assert b"ids%5B%5D=11" in body and b"ids%5B%5D=22" in body


@respx.mock
async def test_account_company_and_balance():
    respx.post(BASE + "getCompanyDetails").mock(return_value=ok({"name": "ООО Ромашка"}))
    rb = respx.post(BASE + "getBillRefillUrl").mock(return_value=ok({"url": "https://pay"}))
    async with client() as kw:
        info = await kw.account.company_info("7700000000")
        assert info["name"] == "ООО Ромашка"
        await kw.account.bill_refill_url(1000)
        assert b"sum=1000" in rb.calls.last.request.content


@respx.mock
async def test_auth_register_and_reset():
    respx.post(BASE + "signUp").mock(return_value=ok({"token": "NEW", "expired": 10}))
    rr = respx.post(BASE + "resetPassword").mock(return_value=httpx.Response(200, json={"success": True}))
    async with anon() as kw:
        s = await kw.register("user", "u@e.com", "pass")
        assert s.token == "NEW"
    async with anon() as kw:
        await kw.reset_password("u@e.com")
        assert rr.called


@respx.mock
async def test_users_and_exchange_extras():
    respx.post(BASE + "kworksCategoriesList").mock(return_value=ok([{"id": 1}]))
    respx.post(BASE + "offer").mock(return_value=ok({"id": 5, "price": 100}))
    rpc = respx.post(BASE + "getWantsCount").mock(return_value=ok({"count": 7}))
    async with client() as kw:
        await kw.users.kworks_categories(1548151)
        offer = await kw.exchange.get_offer(5)
        assert offer.id == 5
        cnt = await kw.exchange.projects_count(categories="15", price_from=1000)
        assert cnt["count"] == 7
        assert b"price_from=1000" in rpc.calls.last.request.content


@respx.mock
async def test_kworks_extra_reads():
    respx.post(BASE + "getKworkDetailsExtra").mock(return_value=ok({"x": 1}))
    rf = respx.post(BASE + "getKworkAnswers").mock(return_value=ok([{"q": "a"}]))
    async with client() as kw:
        await kw.kworks.details_extra(52214751)
        await kw.kworks.faq(52214751)
        assert b"id=52214751" in rf.calls.last.request.content


@respx.mock
async def test_messages_extras_list_field():
    rc = respx.post(BASE + "inboxComplainMessage").mock(return_value=ok())
    rm = respx.post(BASE + "markInboxTracksAsRead").mock(return_value=ok())
    async with client() as kw:
        await kw.messages.complain(123, "спам")
        await kw.messages.mark_tracks_read(5, [100, 200])
        assert b"message_id=123" in rc.calls.last.request.content
        body = rm.calls.last.request.content
        assert b"conversationIds%5B%5D=100" in body and b"conversationIds%5B%5D=200" in body


@respx.mock
async def test_orders_worker_actions():
    rw = respx.post(BASE + "workerInprogress").mock(return_value=ok())
    re_ = respx.post(BASE + "editAnswer").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.worker_in_progress(100)
        await kw.orders.edit_answer(7, "ответ")
        assert b"order_id=100" in rw.calls.last.request.content
        assert b"answer_id=7" in re_.calls.last.request.content


@respx.mock
async def test_portfolio_and_tracks():
    respx.post(BASE + "portfolioCategoriesList").mock(return_value=ok([{"id": 1}]))
    rt = respx.post(BASE + "getTracks").mock(return_value=ok([{"id": 9}]))
    rr = respx.post(BASE + "trackRead").mock(return_value=ok())
    async with client() as kw:
        await kw.portfolio.categories(1548151)
        await kw.tracks.list(63294780)
        await kw.tracks.read([1, 2, 3])
        assert b"orderId=63294780" in rt.calls.last.request.content
        assert b"ids%5B%5D=3" in rr.calls.last.request.content


@respx.mock
async def test_misc_legal_pages():
    respx.post(BASE + "tos").mock(return_value=ok({"text": "..."}))
    respx.post(BASE + "getInAppNotification").mock(return_value=ok({"id": 1}))
    async with client() as kw:
        await kw.misc.tos()
        await kw.misc.in_app_notification(app_version="1.0")
