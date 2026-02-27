"""Аккаунт: профиль, баланс, уведомления, безопасность, оплата."""

from __future__ import annotations

from typing import Any

from kworkapi.models.user import Actor
from kworkapi.resources.base import Resource


class AccountResource(Resource):
    async def me(self) -> Actor:
        """Профиль и состояние текущего пользователя (`/actor`)."""
        return self._model(await self._call("actor"), Actor)

    async def notifications(self, *, page: int = 1) -> dict[str, Any]:
        """Лента уведомлений (`/notificationsFetch`)."""
        return self._payload(await self._call("notificationsFetch", data={"page": page}))

    async def security_data(self) -> dict[str, Any]:
        """Данные безопасности аккаунта (`/getSecurityUserData`)."""
        return self._payload(await self._call("getSecurityUserData"))

    async def payment_methods(self, *, with_company: int = 0) -> dict[str, Any]:
        """Доступные способы оплаты и комиссии (`/getPaymentMethods`)."""
        return self._payload(
            await self._call("getPaymentMethods", data={"withCompany": with_company})
        )

    async def available_features(self) -> dict[str, Any]:
        """Доступные фичи аккаунта (`/getAvailableFeatures`)."""
        return self._payload(await self._call("getAvailableFeatures"))

    async def badges(self) -> dict[str, Any]:
        """Бейджи/счётчики (`/getBadgesInfo`)."""
        return self._payload(await self._call("getBadgesInfo", data={"makeOnline": 0}))

    # --- действия ------------------------------------------------------

    async def update_settings(
        self,
        *,
        username: str,
        fullname: str = "",
        email: str = "",
        timezone_id: int | None = None,
        country_id: int | None = None,
        city_id: int | None = None,
        details: str = "",
        profession: str = "",
        is_consent: int | None = None,
    ) -> dict[str, Any]:
        """Сохранить настройки профиля (`/updateSettings`).

        Поля передаются целиком (как в приложении) — указывайте текущие значения
        для тех, что не меняете.
        """
        data = {
            "username": username,
            "fullname": fullname,
            "email": email,
            "timezoneId": timezone_id,
            "countryId": country_id,
            "cityId": city_id,
            "details": details,
            "profession": profession,
            "is_consent": is_consent,
        }
        return self._payload(await self._call("updateSettings", data=data))

    async def set_taking_orders(self, status: str) -> dict[str, Any]:
        """Включить/выключить приём заказов (`/setTakingOrders`)."""
        return await self._call("setTakingOrders", data={"status": status})

    async def change_username(self, username: str) -> dict[str, Any]:
        """Сменить username (`/changeUsername`)."""
        return await self._call("changeUsername", data={"username": username})

    async def change_password(self, password: str) -> dict[str, Any]:
        """Сменить пароль (`/changePassword`)."""
        return await self._call("changePassword", data={"password": password})

    async def request_email_change(self, email: str) -> dict[str, Any]:
        """Запросить смену email (письмо подтверждения, `/emailVerificationLetter`)."""
        return await self._call("emailVerificationLetter", data={"email": email})

    async def update_avatar(
        self,
        content: bytes,
        filename: str = "avatar.jpg",
        *,
        field: str = "file",
        content_type: str = "image/jpeg",
    ) -> dict[str, Any]:
        """Загрузить аватар профиля (`/updateAvatar`, multipart).

        Имя файловой части на сервере не подтверждено захватом — по умолчанию
        "file", можно переопределить через ``field``.
        """
        files = {field: (filename, content, content_type)}
        return await self._call("updateAvatar", files=files)

    # --- телефон -------------------------------------------------------

    async def add_phone(self, phone: str) -> dict[str, Any]:
        """Привязать номер телефона (`/addPhoneNumber`)."""
        return await self._call("addPhoneNumber", data={"phone": phone})

    async def verify_phone(self, code: str) -> dict[str, Any]:
        """Подтвердить телефон кодом активации (`/verifyPhoneActivationCode`)."""
        return await self._call("verifyPhoneActivationCode", data={"code": code})

    async def send_whatsapp_code(self, phone: str, *, hash: str = "") -> dict[str, Any]:
        """Отправить код подтверждения в WhatsApp (`/sendWhatsAppCode`)."""
        return await self._call("sendWhatsAppCode", data={"phone": phone, "hash": hash})

    # --- удаление аккаунта ---------------------------------------------

    async def delete_account(self) -> dict[str, Any]:
        """Запросить удаление аккаунта (`/deleteAccount`)."""
        return await self._call("deleteAccount")

    async def verify_delete_code(self, code: str) -> dict[str, Any]:
        """Подтвердить удаление аккаунта SMS-кодом (`/verifySmsCodeForAccountDeleting`)."""
        return await self._call("verifySmsCodeForAccountDeleting", data={"code": code})

    # --- компания / yescrow --------------------------------------------

    async def company_info(self, tax_number: str) -> dict[str, Any]:
        """Данные компании по ИНН (`/getCompanyDetails`)."""
        return self._payload(await self._call("getCompanyDetails", data={"tax_number": tax_number}))

    async def verify_company(self, tax_number: str, address: str) -> dict[str, Any]:
        """Отправить компанию на верификацию (`/sendCompanyForVerification`)."""
        data = {"tax_number": tax_number, "address": address}
        return await self._call("sendCompanyForVerification", data=data)

    async def change_payer_sub_role(self, payer_sub_role: int) -> dict[str, Any]:
        """Сменить подроль покупателя (физлицо/компания, `/changePayerSubRole`)."""
        return await self._call("changePayerSubRole", data={"payerSubRole": payer_sub_role})

    # --- баланс / оплата -----------------------------------------------

    async def bill_refill_url(self, amount: float) -> dict[str, Any]:
        """Ссылка на пополнение баланса (`/getBillRefillUrl`)."""
        return self._payload(await self._call("getBillRefillUrl", data={"sum": amount}))

    async def set_notify_card_refill(self, flag: int) -> dict[str, Any]:
        """Уведомлять о пополнении картой (`/setNotifyCardRefill`)."""
        return await self._call("setNotifyCardRefill", data={"flag": flag})

    # --- push / уведомления --------------------------------------------

    async def allow_mobile_push(self, allow: int) -> dict[str, Any]:
        """Разрешить мобильные пуши (`/allowMobilePush`)."""
        return await self._call("allowMobilePush", data={"allow": allow})

    async def register_push_token(self, cloud_token: str, *, os: str = "android", app_version: str = "") -> dict[str, Any]:
        """Зарегистрировать FCM/push-токен (`/registerCloudToken`)."""
        data = {"cloud_token": cloud_token, "os": os, "app_version": app_version}
        return await self._call("registerCloudToken", data=data)

    async def notifications_received(self, ids: list[int], *, make_online: int = 0) -> dict[str, Any]:
        """Отметить уведомления полученными (`/notificationsReceived`)."""
        return await self._call("notificationsReceived", data={"ids[]": ids, "makeOnline": make_online})

    # --- голосовые настройки -------------------------------------------

    async def set_voice_receiving(self, is_allowed: int) -> dict[str, Any]:
        """Разрешить приём голосовых (`/setVoiceMessageReceiving`)."""
        return await self._call("setVoiceMessageReceiving", data={"is_allowed": is_allowed})

    async def set_voice_speed(self, speed: float) -> dict[str, Any]:
        """Скорость воспроизведения голосовых (`/setVoiceMessageSpeed`)."""
        return await self._call("setVoiceMessageSpeed", data={"speed": speed})

    # --- прочее --------------------------------------------------------

    async def set_user_type(self, type: int) -> dict[str, Any]:
        """Переключить роль (исполнитель/покупатель, `/setUserType`)."""
        return await self._call("setUserType", data={"type": type})

    async def set_available_at_weekends(self, available: bool) -> dict[str, Any]:
        """Доступность по выходным (`/setAvailableAtWeekends`)."""
        return await self._call("setAvailableAtWeekends", data={"available": available})

    async def self_employed_survey(self, answer: int) -> dict[str, Any]:
        """Ответ опроса самозанятости (`/sendSelfEmployedSurveyResult`)."""
        return await self._call("sendSelfEmployedSurveyResult", data={"answer": answer})

    async def public_features(self) -> dict[str, Any]:
        """Публичные фичи (без авторизации, `/getPublicFeatures`)."""
        return self._payload(await self._call("getPublicFeatures", auth=False))

    async def captcha_status(self) -> dict[str, Any]:
        """Статус капчи (`/getCaptchaStatus`)."""
        return self._payload(await self._call("getCaptchaStatus"))

    async def web_auth_token(self, url_to_redirect: str = "") -> dict[str, Any]:
        """Токен для авторизованного открытия веб-страниц (`/getWebAuthToken`)."""
        return self._payload(
            await self._call("getWebAuthToken", data={"url_to_redirect": url_to_redirect})
        )

    async def is_dialog_allowed(self, receiver_id: int) -> dict[str, Any]:
        """Можно ли писать пользователю (`/isDialogAllow`)."""
        return self._payload(await self._call("isDialogAllow", data={"receiverId": receiver_id}))

    # --- география -----------------------------------------------------

    async def countries(self) -> dict[str, Any]:
        """Список стран (`/countries`)."""
        return self._payload(await self._call("countries"))

    async def cities(self, country_id: int) -> dict[str, Any]:
        """Города страны (`/cities`)."""
        return self._payload(await self._call("cities", data={"countryId": country_id}))

    async def timezones(self) -> dict[str, Any]:
        """Список часовых поясов (`/timezones`)."""
        return self._payload(await self._call("timezones"))
