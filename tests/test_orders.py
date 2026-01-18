"""Тесты Фазы 4b: заказы, детали kwork, загрузка файлов (моки respx)."""

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
async def test_order_details_sends_order_id():
    route = respx.post(BASE + "getOrderDetails").mock(return_value=ok({"id": 63294780, "status": "work"}))
    async with client() as kw:
        d = await kw.orders.details(63294780)
        assert d["id"] == 63294780
        assert b"orderId=63294780" in route.calls.last.request.content


@respx.mock
async def test_order_approve_fields():
    route = respx.post(BASE + "approveOrder").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.approve(100, portfolio=1)
        body = route.calls.last.request.content
        assert b"orderId=100" in body and b"portfolio=1" in body


@respx.mock
async def test_order_create_review_type():
    route = respx.post(BASE + "createReview").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.create_review(100, positive=False, text="плохо")
        body = route.calls.last.request.content
        assert b"order_id=100" in body and b"type=negative" in body


@respx.mock
async def test_order_send_bonus():
    route = respx.post(BASE + "sendBonus").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.send_bonus(100, 500, comment="спасибо")
        body = route.calls.last.request.content
        assert b"orderId=100" in body and b"bonus=500" in body


@respx.mock
async def test_kwork_details_and_reviews():
    rd = respx.post(BASE + "getKworkDetails").mock(return_value=ok({"id": 52214751, "title": "x"}))
    rr = respx.post(BASE + "getKworkReviews").mock(return_value=ok([{"id": 1}]))
    async with client() as kw:
        d = await kw.kworks.details(52214751)
        assert d["id"] == 52214751
        await kw.kworks.reviews(52214751, page=2)
        body = rr.calls.last.request.content
        assert b"kwork_id=52214751" in body and b"page=2" in body
        assert rd.called


@respx.mock
async def test_file_upload_multipart_with_file_part():
    route = respx.post(BASE + "fileUpload").mock(
        return_value=httpx.Response(200, json={"success": True, "response": {"id": 7}})
    )
    async with client() as kw:
        res = await kw.files.upload(b"hello-bytes", "doc.txt")
        assert res["response"]["id"] == 7
        req = route.calls.last.request
        assert req.headers["content-type"].startswith("multipart/form-data")
        body = req.content
        # файловая часть + общие поля как части
        assert b'filename="doc.txt"' in body and b"hello-bytes" in body
        assert b'name="token"' in body and b'name="uad"' in body
