"""Аккаунт: профиль, баланс, уведомления, безопасность, оплата."""

from __future__ import annotations

from kworkapi.models.user import Actor
from kworkapi.resources.base import Resource


class AccountResource(Resource):
    async def me(self) -> Actor:
        """Профиль и состояние текущего пользователя (`/actor`)."""
        return self._model(await self._call("actor"), Actor)

    async def notifications(self, *, page: int = 1) -> dict:
        """Лента уведомлений (`/notificationsFetch`)."""
        return self._payload(await self._call("notificationsFetch", data={"page": page}))

    async def security_data(self) -> dict:
        """Данные безопасности аккаунта (`/getSecurityUserData`)."""
        return self._payload(await self._call("getSecurityUserData"))

    async def payment_methods(self, *, with_company: int = 0) -> dict:
        """Доступные способы оплаты и комиссии (`/getPaymentMethods`)."""
        return self._payload(
            await self._call("getPaymentMethods", data={"withCompany": with_company})
        )

    async def available_features(self) -> dict:
        """Доступные фичи аккаунта (`/getAvailableFeatures`)."""
        return self._payload(await self._call("getAvailableFeatures"))

    async def badges(self) -> dict:
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
    ) -> dict:
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

    async def set_taking_orders(self, status: str) -> dict:
        """Включить/выключить приём заказов (`/setTakingOrders`)."""
        return await self._call("setTakingOrders", data={"status": status})

    async def change_username(self, username: str) -> dict:
        """Сменить username (`/changeUsername`)."""
        return await self._call("changeUsername", data={"username": username})

    async def change_password(self, password: str) -> dict:
        """Сменить пароль (`/changePassword`)."""
        return await self._call("changePassword", data={"password": password})

    async def request_email_change(self, email: str) -> dict:
        """Запросить смену email (письмо подтверждения, `/emailVerificationLetter`)."""
        return await self._call("emailVerificationLetter", data={"email": email})
