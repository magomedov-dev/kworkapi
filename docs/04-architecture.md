# 04. Архитектура библиотеки

Два уровня: переиспользуемая библиотека-клиент `kworkapi/` и опциональный
REST-сервис `api/` (FastAPI) поверх неё.

```
┌─────────────────────────────────────────────┐
│  api/  (FastAPI)   — REST + Swagger наружу    │  опционально
├─────────────────────────────────────────────┤
│  kworkapi/  (библиотека)                      │
│                                               │
│   KworkClient ── session(token, slrememberme) │
│       │                                        │
│       ├─ resources/  (группы методов)          │
│       │     catalog · search · exchange ·      │
│       │     orders · messages · account · …    │
│       │                                        │
│       ├─ auth        (signIn, captcha, refresh)│
│       ├─ models/     (pydantic: ответы)        │
│       └─ transport   (httpx: заголовки,         │
│                       uad, ретраи, rate-limit,  │
│                       разбор обёрток/ошибок)     │
└─────────────────────────────────────────────┘
                     │ HTTPS form-urlencoded
                     ▼
              https://api.kwork.ru/
```

## Слои

### `transport.py`
Единственная точка сетевого общения. Отвечает за:
- базовый URL и статичный `Authorization`;
- автоподстановку общих полей (`token`, `uad`, `slrememberme`, `device`) и `Cookie`;
- ретраи с бэкоффом, обработку 429 (rate-limit);
- разбор обёрток (`success`/`response`/`error`/`paging`) и подъём типизированных исключений.

### `auth.py`
Логин (`signIn`), ветки с капчей и подтверждением телефона, модель `Session`
(`token`, `slrememberme`, `expired`). Хранение токена — снаружи (передаётся в клиент).

### `resources/` — группы методов
Отражают сервисы приложения, но сгруппированы по смыслу для удобного публичного API:

| Ресурс | Покрывает сервисы | Примеры методов |
|---|---|---|
| `account` | Actor, частично User | `me`, `settings`, `balance`, `notifications`, `set_taking_orders` |
| `catalog` | Catalog | `categories`, `rubrics`, `kworks`, `favorites` |
| `search` | Catalog/Search | `kworks`, `users`, `dialogs`, `messages` |
| `kworks` | Kwork, KworkDetails, User | `details`, `reviews`, `order`, `create/pause/start` |
| `exchange` | Exchange | `projects`, `offer`, `my_offers`, `categories` |
| `orders` | Order | `worker_orders`, `payer_orders`, `details`, `approve`, `cancel`, `stages` |
| `messages` | Dialog, Inbox, Track | `dialogs`, `history`, `send`, `forward`, `delete` |
| `portfolio` | Portfolio, File | `list`, `upload` |
| `users` | User | `info`, `kworks`, `reviews`, `block/unblock` |

### `models/`
Pydantic-модели ответов. До валидации живым трафиком — «мягкие» (`extra="allow"`),
с базовыми обёртками `DataResponse`/`PagedResponse`/`BooleanResponse`. По мере
проверки ужесточаются.

## Принципы

- **Async-first** (httpx.AsyncClient), один пул соединений на клиент.
- **Типизация**: публичные методы возвращают pydantic-модели, не сырой dict.
- **Изоляция знаний об API**: пути/поля живут в ресурсах, транспорт их не знает.
- **Тестируемость**: сеть мокается (`respx`), каждый ресурс покрыт тестами.
- **Без побочной телеметрии**: не тащим appmetrica/firebase из оригинала — только то,
  что нужно для работы API.

## FastAPI-слой (`api/`)
Тонкий REST поверх библиотеки: токен пользователя приходит в заголовке
`X-Kwork-Token`, сервис конструирует `KworkClient` и проксирует в ресурсы.
Автодоки — Swagger `/docs`.
