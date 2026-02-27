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
  resources/     — группы методов: account, catalog, search, exchange, users,
                   kworks, orders, messages, files, portfolio, tracks, misc
api/             — FastAPI-сервис поверх библиотеки (REST + Swagger наружу)
research/        — артефакты реверса: инструкция по захвату + карта эндпоинтов
tests/           — тесты (моки через respx)
```

## Статус

Релиз **0.5.0** (полная типизация: pyright strict, py.typed): полное покрытие API — **12 ресурсов, 166 методов** (авторизация и
регистрация, каталог, поиск, биржа, профили, kwork'и, полный жизненный цикл заказов,
сообщения и голосовые, файлы, портфолио, треки, настройки, гео, правовые страницы) +
FastAPI-сервис. Чтение и вход проверены на живом API. Подробности — в
[`docs/`](docs/README.md), план — в [`docs/05-roadmap.md`](docs/05-roadmap.md).

## Документация

Полное руководство пользователя (установка, авторизация, все ресурсы с примерами,
обработка ошибок, REST-сервис) — в **[`docs/07-usage.md`](docs/07-usage.md)**.
Остальная документация (реверс, справочник API, архитектура, roadmap) — в
[`docs/`](docs/README.md).

## Установка

```bash
git clone https://github.com/magomedov-dev/kworkapi.git
cd kworkapi
python -m venv .venv && source .venv/bin/activate.fish  # bash: source .venv/bin/activate
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
`orders`, `messages`, `files`, `portfolio`, `tracks`, `misc`.

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
- [x] Фаза 6 — надёжность: троттлинг, типизация, CI
- [x] Фаза 7 — релиз (semver, теги)
- [x] Фаза 8 — полное покрытие API (12 ресурсов, 166 методов)
