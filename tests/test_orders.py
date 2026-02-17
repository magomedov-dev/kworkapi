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
async def test_buy_extras_fields():
    route = respx.post(BASE + "payerBuyExtras").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.buy_extras(100, as_volume=2)
        body = route.calls.last.request.content
        assert b"order_id=100" in body and b"as_volume=2" in body


@respx.mock
async def test_accept_extra_and_delete():
    ra = respx.post(BASE + "acceptExtras").mock(return_value=ok())
    rd = respx.post(BASE + "payerExtraDelete").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.accept_extra(100, 555)
        await kw.orders.delete_extra(777)
        assert b"order_id=100" in ra.calls.last.request.content
        assert b"track_id=555" in ra.calls.last.request.content
        assert b"extra_id=777" in rd.calls.last.request.content


@respx.mock
async def test_pay_stage_and_update_progress():
    rp = respx.post(BASE + "orderStage").mock(return_value=ok())
    ru = respx.post(BASE + "updateStageProgress").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.pay_stage(100, 9)
        await kw.orders.update_stage_progress(100, {9: 50, 10: 100}, comment="готово")
        assert b"stage_id=9" in rp.calls.last.request.content
        body = ru.calls.last.request.content
        assert b"order_id=100" in body and b"9=50" in body and b"10=100" in body


@respx.mock
async def test_rate_arbitration_and_report():
    ra = respx.post(BASE + "rateArbitration").mock(return_value=ok())
    rr = respx.post(BASE + "sendReport").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.rate_arbitration(42, 5)
        await kw.orders.send_report(100, 80, comment="идёт работа")
        assert b"id=42" in ra.calls.last.request.content
        assert b"rating=5" in ra.calls.last.request.content
        assert b"progress=80" in rr.calls.last.request.content


@respx.mock
async def test_voice_transcription_and_heard():
    rt = respx.post(BASE + "getVoiceMessageTranscription").mock(return_value=ok({"text": "привет"}))
    rh = respx.post(BASE + "markVoiceMessageHeard").mock(return_value=ok())
    async with client() as kw:
        await kw.messages.voice_transcription(529722055)
        await kw.messages.mark_voice_heard(529722055)
        assert b"conversation_id=529722055" in rt.calls.last.request.content
        assert b"conversation_id=529722055" in rh.calls.last.request.content


@respx.mock
async def test_cancel_by_payer_fields():
    route = respx.post(BASE + "cancelOrderByPayer").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.cancel_by_payer(100, reason_type=3, message="не подошло", hide_kworks=True)
        body = route.calls.last.request.content
        assert b"order_id=100" in body and b"reason_type=3" in body and b"hideKworks=1" in body


@respx.mock
async def test_cancel_request_flow():
    rc = respx.post(BASE + "confirmCancelOrderRequestByPayer").mock(return_value=ok())
    rr = respx.post(BASE + "rejectCancelOrderRequestByWorker").mock(return_value=ok())
    async with client() as kw:
        await kw.orders.confirm_cancel_as_payer(100, reply_type=1)
        await kw.orders.reject_cancel_as_worker(100)
        assert b"order_id=100" in rc.calls.last.request.content
        assert b"reply_type=1" in rc.calls.last.request.content
        assert b"order_id=100" in rr.calls.last.request.content


@respx.mock
async def test_custom_options_presets():
    route = respx.post(BASE + "getCustomOptionsPresets").mock(return_value=ok([{"id": 1}]))
    async with client() as kw:
        await kw.orders.custom_options_presets(100)
        assert b"order_id=100" in route.calls.last.request.content


@respx.mock
async def test_update_avatar_multipart():
    route = respx.post(BASE + "updateAvatar").mock(return_value=ok())
    async with client() as kw:
        await kw.account.update_avatar(b"\xff\xd8jpegbytes", "me.jpg")
        req = route.calls.last.request
        assert req.headers["content-type"].startswith("multipart/form-data")
        body = req.content
        assert b'filename="me.jpg"' in body and b"jpegbytes" in body
        assert b'name="token"' in body


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
