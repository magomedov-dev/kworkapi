# 07. Руководство пользователя

Как пользоваться библиотекой `kworkapi` и REST-сервисом. Примеры — рабочие.

> ⚠️ Библиотека использует приватный API kwork.ru. Применяйте для личной
> автоматизации, соблюдайте Условия использования kwork и включайте троттлинг.

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Авторизация и сессия](#авторизация-и-сессия)
- [Обработка ошибок](#обработка-ошибок)
- [Анти-бот и троттлинг](#анти-бот-и-троттлинг)
- [Ресурсы и методы](#ресурсы-и-методы)
  - [account](#account--аккаунт)
  - [catalog](#catalog--каталог)
  - [search](#search--поиск)
  - [exchange](#exchange--биржа-проектов)
  - [users](#users--пользователи)
  - [kworks](#kworks--kworkи)
  - [orders](#orders--заказы)
  - [messages](#messages--сообщения)
  - [files](#files--файлы)
- [Модели данных](#модели-данных)
- [REST-сервис (FastAPI)](#rest-сервис-fastapi)

## Установка

```bash
pip install -e .              # библиотека
pip install -e ".[server]"    # + FastAPI-сервис
pip install -e ".[dev]"       # + инструменты разработки/тесты
```

Требуется Python ≥ 3.11. Зависимости ядра: `httpx`, `pydantic`.

## Быстрый старт

```python
import asyncio
from kworkapi import KworkClient

async def main():
    async with KworkClient() as kw:
        await kw.login("user@example.com", "password")

        me = await kw.account.me()
        print(me.username, me.free_amount, me.currency)

        result = await kw.search.kworks("логотип", limit=10)
        for k in result.kworks:
            print(k.id, k.title, k.price)

asyncio.run(main())
```

`KworkClient` — асинхронный. Используйте его как контекст-менеджер (`async with`)
или вызывайте `await kw.aclose()` вручную.

## Авторизация и сессия

### Вход по логину/паролю

```python
async with KworkClient() as kw:
    session = await kw.login("user@example.com", "password")
    print(session.token, session.expired, session.need_2fa)
```

### Капча (Google reCAPTCHA v2)

`login()` возвращает либо `Session`, либо `LoginChallenge` (если kwork требует
капчу, `error_code 118`). Капча — **не исключение**, а объект-челлендж:

```python
from kworkapi import KworkClient, Session, LoginChallenge

async with KworkClient() as kw:
    result = await kw.login("user@example.com", "password")
    if isinstance(result, LoginChallenge):
        # result.sitekey   — '6LdX9CAT...' (reCAPTCHA v2)
        # result.page_url  — https://kwork.ru/captcha_only
        token = await solve_recaptcha(result.sitekey, result.page_url)  # ваш способ
        session = await kw.solve_captcha(result, token)
    else:
        session = result
    print(session.token, session.recaptcha_pass_token)
```

Как получить `g-recaptcha-response` (`token`) — на стороне потребителя, любым способом:
- открыть `result.page_url` в WebView (Qt `QWebEngineView`, Electron, браузер), дать
  пользователю решить, перехватить токен из фрагмента `#response=`;
- отрендерить свой reCAPTCHA-виджет с `result.sitekey` на странице origin `kwork.ru`;
- использовать решалку (2captcha/anti-captcha): передать `sitekey` + `pageurl`.

**Чтобы капчу не спрашивали повторно** — сохраните `session.recaptcha_pass_token`
вместе с сессией; при следующем `login()` он подставится автоматически (или передайте
явно через `recaptcha_pass_token=...`):

```python
await kw.login("user@example.com", "password", recaptcha_pass_token="...")
```

### Сохранение и переиспользование сессии

Чтобы не логиниться повторно (и не ловить анти-бот), сохраните сессию и
восстановите её позже:

```python
import json
from kworkapi.auth import Session

# сохранить
data = session.to_dict()
open("session.json", "w").write(json.dumps(data))

# восстановить
saved = Session.from_dict(json.load(open("session.json")))
async with KworkClient.from_session(saved) as kw:
    me = await kw.account.me()      # уже авторизован
```

`Session` хранит `token`, `uad`, `slrememberme`, `expired`. Поле `uad` — стабильный
идентификатор установки; переиспользуйте один и тот же `uad` между запусками.

### Выход

```python
await kw.logout()
```

## Обработка ошибок

Все ошибки наследуются от `KworkError`:

```python
from kworkapi import (
    KworkError, KworkAPIError, KworkAuthError, KworkRateLimitError,
)

try:
    await kw.account.me()
except KworkAuthError:
    ...            # токен протух/неверен — нужен повторный login()
except KworkRateLimitError:
    ...            # HTTP 429/403 — анти-бот/лимит, сделайте паузу
except KworkAPIError as e:
    print(e.message, e.code, e.payload)   # ошибка API kwork (success=false)
```

| Исключение | Когда |
|---|---|
| `KworkAuthError` | нет/протух токен, ошибка входа |
| `KworkRateLimitError` | HTTP 429 или 403 (анти-бот/лимит) |
| `KworkAPIError` | API вернул `success=false` или HTTP ≥ 400 |
| `KworkError` | базовый класс всех ошибок |

## Анти-бот и троттлинг

kwork ограничивает частые входы (`/signIn`) с одного IP — можно получить HTTP 403.
Рекомендации:

- **переиспользуйте сессию** (`from_session`) вместо повторного `login()`;
- **переиспользуйте `uad`** между запусками;
- включите троттлинг — минимальный интервал между запросами:

```python
async with KworkClient(min_request_interval=0.5) as kw:   # ≥0.5с между запросами
    ...
```

Транспорт сам делает ретраи на сетевые ошибки и HTTP 429 с экспоненциальным
бэкоффом.

## Ресурсы и методы

Все методы — корутины (`await`). Методы чтения возвращают pydantic-модели или
`dict`, методы действий — `dict` ответа API.

### `account` — аккаунт

```python
me      = await kw.account.me()                 # -> Actor (профиль, баланс, счётчики)
notes   = await kw.account.notifications(page=1)
methods = await kw.account.payment_methods()
await kw.account.update_settings(username="me", fullname="Имя", city_id=930)
await kw.account.set_taking_orders("stop")      # приём заказов вкл/выкл
await kw.account.change_username("newname")
await kw.account.update_avatar(open("ava.jpg","rb").read(), "ava.jpg")
```

### `catalog` — каталог

```python
tree     = await kw.catalog.categories()        # -> list[Category] (дерево)
listing  = await kw.catalog.kworks(category_id=15, page=1)   # -> KworksResult
favs     = await kw.catalog.favorites()         # -> Page[Kwork]
hidden   = await kw.catalog.hidden()
viewed   = await kw.catalog.viewed()
filters  = await kw.catalog.filters(category_id=15)
```

### `search` — поиск

```python
res   = await kw.search.kworks("логотип", category_id=196, page=1, limit=20)  # KworksResult
hints = await kw.search.suggest("лого")
users = await kw.search.users("designer")       # -> Page[User]
```

### `exchange` — биржа проектов

```python
feed   = await kw.exchange.projects(categories="all", page=1)
info   = await kw.exchange.info()               # -> ExchangeInfo
cats   = await kw.exchange.categories()
count  = await kw.exchange.wants_count()
offers = await kw.exchange.my_offers()          # -> list[Offer]

# откликнуться на проект (multipart)
await kw.exchange.create_offer(want_id=3202099, description="Сделаю", price=5000, duration=3)
await kw.exchange.delete_offer(offer_id=39092325)
```

### `users` — пользователи

```python
user    = await kw.users.get(1548151)           # -> User (по id)
user2   = await kw.users.by_username("gumangee2")
kworks  = await kw.users.kworks(1548151)        # -> Page[Kwork]
reviews = await kw.users.reviews(1548151)
```

### `kworks` — kwork'и

```python
details   = await kw.kworks.details(52214751)   # карточка kwork
reviews   = await kw.kworks.reviews(52214751)
portfolio = await kw.kworks.portfolios(52214751)

# управление своими kwork'ами (исполнитель)
await kw.kworks.mark_favorite(52214751, True)
await kw.kworks.mark_hidden(52214751, True)
await kw.kworks.pause(52214751)
await kw.kworks.start(52214751)
await kw.kworks.delete(52214751)
```

### `orders` — заказы

```python
# списки и детали
worker = await kw.orders.worker()               # как исполнитель
payer  = await kw.orders.payer()                # как покупатель
order  = await kw.orders.details(63294780)
files  = await kw.orders.files(63294780)

# ход работы
await kw.orders.approve(order_id)
await kw.orders.send_for_approval(order_id)
await kw.orders.send_for_revision(order_id, "поправьте логотип")
await kw.orders.send_requirements(order_id, "нужен исходник")
await kw.orders.send_report(order_id, progress=80, comment="идёт работа")
await kw.orders.send_bonus(order_id, 500, comment="спасибо")
await kw.orders.repeat(order_id)

# стадии и экстры
await kw.orders.accept_stage(order_id)
await kw.orders.pay_stage(order_id, stage_id)
await kw.orders.update_stage_progress(order_id, {stage_id: 50})
extras = await kw.orders.available_extras(order_id)
await kw.orders.buy_extras(order_id)

# отзывы
await kw.orders.create_review(order_id, positive=True, text="отлично")
await kw.orders.create_answer(review_id, "спасибо за отзыв")

# отмена
reasons = await kw.orders.cancellation_reasons(order_id)
await kw.orders.cancel_by_payer(order_id, reason_type=3, message="не подошло")
await kw.orders.confirm_cancel_as_worker(order_id)
await kw.orders.rate_arbitration(arbitration_id, rating=5)
```

### `messages` — сообщения

```python
dialogs = await kw.messages.dialogs()           # -> list[Dialog]
history = await kw.messages.history(user_id, limit=30)   # -> list[InboxMessage]
sent    = await kw.messages.send(user_id, "Здравствуйте!")  # -> SentMessage

await kw.messages.edit(message_id, "исправленный текст")
await kw.messages.delete(message_id)
await kw.messages.set_starred(user_id, True)
await kw.messages.block(user_id)
await kw.messages.unblock(user_id)
found = await kw.messages.search("договор")

# голосовые
text = await kw.messages.voice_transcription(conversation_id)
await kw.messages.mark_voice_heard(conversation_id)
```

### `files` — файлы

```python
data = open("doc.pdf", "rb").read()
up   = await kw.files.upload(data, "doc.pdf", content_type="application/pdf")
voice = await kw.files.upload_voice(open("v.ogg","rb").read())
```

## Модели данных

Импорт из `kworkapi.models`. Все модели «мягкие» (`extra="allow"`): неизвестные
поля сохраняются, доступ — как к атрибутам.

```python
from kworkapi.models import Actor, User, Kwork, Dialog, Offer, Project, Page

me = await kw.account.me()
print(me.id, me.username, me.free_amount)

page = await kw.catalog.favorites()             # Page[Kwork]
for kwork in page:                              # Page итерируется
    print(kwork.title)
print(page.paging.total)
```

Основные модели: `Actor`, `User`, `Kwork`/`KworksResult`, `Category`, `Dialog`/
`InboxMessage`/`SentMessage`, `Project`/`Offer`/`ExchangeInfo`, `Paging`, `Page[T]`.
Сериализация в dict — `model.model_dump()`.

## REST-сервис (FastAPI)

```bash
pip install -e ".[server]"
uvicorn api.main:app --reload
```

- Swagger: <http://127.0.0.1:8000/docs>, ReDoc: `/redoc`
- Авторизация: `POST /auth/login` → `{ "token": "..." }`, далее заголовок
  `X-Kwork-Token: <token>` для остальных запросов.

```bash
# логин
curl -s -X POST localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"login":"user@example.com","password":"secret"}'

# профиль
curl -s localhost:8000/account/me -H 'X-Kwork-Token: <token>'

# поиск
curl -s 'localhost:8000/search/kworks?q=логотип' -H 'X-Kwork-Token: <token>'
```

Группы эндпоинтов: `/auth`, `/account`, `/catalog`, `/search`, `/exchange`,
`/users`, `/kworks`, `/orders`, `/messages`, `/files`. Ошибки библиотеки
маппятся в HTTP-коды: 401 (auth), 429 (анти-бот/лимит), 502 (ошибка API), 500.
