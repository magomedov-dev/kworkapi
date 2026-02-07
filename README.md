# KworkAPI

Неофициальная Python-библиотека и REST-обёртка (FastAPI) над приватным API
freelance-площадки **kwork.ru**. У kwork нет публичного API — клиент построен на
реверс-инжиниринге трафика мобильного приложения (`api.kwork.ru`).

> ⚠️ **Дисклеймер.** Проект использует приватный API kwork.ru, не предназначенный
> для сторонних клиентов. Используйте на свой риск и в рамках Условий использования
> kwork. Подходит для личной автоматизации и обучения; публичный коммерческий сервис
> на этой основе рискован.

## Структура

```
kworkapi/        — библиотека-обёртка (ядро)
  transport.py   — httpx-транспорт: заголовки, ретраи, rate-limit, обработка ошибок
  client.py      — KworkClient: сессия + доступ к группам методов (ресурсам)
  auth.py        — авторизация (signIn), хранение токена
  models/        — pydantic-модели ответов
  resources/     — группы методов: catalog, projects, orders, messages, account
api/             — FastAPI-сервис поверх библиотеки (REST + Swagger наружу)
research/        — артефакты реверса: инструкция по захвату + карта эндпоинтов
tests/           — тесты (моки через respx)
```

## Статус

Релиз **0.2.0**: библиотека (авторизация, чтение, действия, заказы, файлы,
голосовые) и FastAPI-сервис. Чтение и вход проверены на живом API. Подробности —
в [`docs/`](docs/README.md), план — в [`docs/05-roadmap.md`](docs/05-roadmap.md).

## Установка (dev)

```bash
python -m venv .venv && source .venv/bin/activate.fish  # fish: source .venv/bin/activate.fish
pip install -e ".[server,dev]"
```

## Быстрый старт (библиотека)

```python
import asyncio
from kworkapi import KworkClient

async def main():
    async with KworkClient() as kw:
        await kw.login("user@example.com", "password")
        me = await kw.account.me()
        print(me.username, me.free_amount, me.currency)
        res = await kw.search.kworks("логотип", limit=10)
        for k in res.kworks:
            print(k.id, k.title, k.price)

asyncio.run(main())
```

Ресурсы клиента: `account`, `catalog`, `search`, `exchange`, `users`, `kworks`,
`orders`, `messages`, `files`.

## Запуск REST-сервиса (FastAPI)

```bash
pip install -e ".[server]"
uvicorn api.main:app --reload
# Swagger: http://127.0.0.1:8000/docs
```

Авторизация сервиса: `POST /auth/login` → токен, далее передавайте его в заголовке
`X-Kwork-Token`.

## Дорожная карта

- [x] Фаза 0 — скелет проекта
- [x] Фаза 1 — разведка: реверс APK + захват трафика, карта эндпоинтов
- [x] Фаза 2 — авторизация (signIn, токен, uad/сессия)
- [x] Фаза 3 — чтение: аккаунт, каталог, поиск, биржа, пользователи (+ модели)
- [x] Фаза 4 — действия: сообщения, отклики, настройки, kwork'и
- [x] Фаза 5 — FastAPI-обёртка
- [ ] Фаза 6 — надёжность: троттлинг, типизация, CI
- [ ] Фаза 7 — релиз
