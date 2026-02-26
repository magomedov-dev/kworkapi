# 05. Roadmap реализации KworkAPI

План до полноценной, качественной библиотеки. Ведём по gitflow: каждая фаза —
ветка `feature/*` → merge `--no-ff` в `develop`; релизы — в `main`. Коммиты —
Conventional Commits на русском. Каждая фаза заканчивается зелёными тестами и
обновлённой документацией в `docs/`.

Легенда: ✅ готово · 🚧 в работе · ⬜ не начато

---

## Фаза 0 — Скелет проекта ✅
- ✅ Структура `kworkapi/` + `api/` + `tests/` + `research/` + `docs/`.
- ✅ `pyproject.toml`, окружение, базовые `transport`/`client`/`auth`/ресурсы.
- ✅ git (gitflow), `.tooling/`, `.env` (gitignore).
- ✅ 11 тестов проходят.

## Фаза 1 — Разведка и документация ✅
- ✅ Декомпиляция `ru.kwork.app`, парсер Retrofit-сервисов.
- ✅ Найдено: base URL, `Authorization`, схема `token`/`uad`/`slrememberme`, обёртки ответов.
- ✅ Каталог 192 эндпоинтов + документация `docs/`.
- ✅ Валидация живым трафиком (mitmproxy, 2 прогона, 895 flows): подтверждены base URL,
  схема авторизации, формы ответов 63 эндпоинтов → `docs/06-captured-responses.md`.

## Фаза 2 — Ядро транспорта и авторизация ⬜
**Ветка:** `feature/phase-2-core-auth`
- Подставить реальные константы: base URL, `Authorization`, генератор `uad`.
- `transport`: общие поля, `Cookie: slrememberme`, разбор `DataResponse`/`paging`/`error`.
- `auth`: `signIn` → `Session{token, slrememberme, expired}`; ветки `signInWithCaptcha`,
  подтверждение телефоном; `logout`.
- Хранилище сессии (файл/конфиг) + переиспользование `uad`.
- **Проверка:** реальный логин тестовым аккаунтом, получение `token` (с учётом капчи).
- Тесты: разбор обёрток, ошибки, авторизация (моки) + 1 интеграционный (опц., помечен).

## Фаза 3 — Чтение каталога и бирж ✅
**Ветка:** `feature/phase-3-read`
- ✅ `account`: `me` (/actor), `notifications`, `security_data`, `payment_methods`, `badges`, `available_features`.
- ✅ `catalog`: `categories` (дерево), `rubrics`, `main`, `kworks`, `favorites`, `hidden`, `viewed`, `filters`.
- ✅ `search`: `kworks`, `suggest`, `users`.
- ✅ `exchange`: `projects` (лента биржи), `info`, `categories`, `favorite_categories`, `wants_count`, `my_offers`, `my_wants`.
- ✅ `users`: `get`, `by_username`, `kworks`, `reviews`.
- ✅ `orders` (чтение): `worker`, `payer` (с обработкой «нет заказов», code 151).
- ✅ Pydantic-модели: Actor, User, Kwork/KworksResult, Dialog/InboxMessage, Category,
  Project/Offer, ExchangeInfo, Paging, Page[T] (extra=allow).
- ✅ Тесты: моки (respx) + опциональный живой тест (KWORK_LIVE=1).
- ✅ Проверено на живом API: профиль, дерево категорий, поиск (54k+), диалоги, биржа.
- ⬜ Перенести (Фаза 4) детали kwork: открываются в webview через `getWebAuthToken`.

## Фаза 4 — Действия и сообщения ✅ (частично)
**Ветка:** `feature/phase-4-actions`
- ✅ `messages`: `send` (inboxCreate), `edit`, `delete`, `mark_read`, `mark_unread`,
  `set_starred`, `block`/`unblock`, `search`.
- ✅ `exchange`: `create_offer`/`edit_offer` (multipart `/api/offer/*`), `delete_offer`.
- ✅ `account`: `update_settings`, `set_taking_orders`, `change_username`/`change_password`,
  `request_email_change`.
- ✅ `kworks` (исполнитель): `mark_favorite`, `mark_hidden`, `pause`, `start`, `delete`.
- ✅ Транспорт: поддержка multipart; HTTP 403 → понятная ошибка (анти-бот).
- ✅ Тесты: моки тел запросов (multipart, поля) + живой тест действий между двумя
  аккаунтами (KWORK_LOGIN2), запуск по KWORK_LIVE=1.
- ⚠️ Живая проверка отложена: IP под анти-бот троттлингом (403) после серии входов —
  повторить позже. Логика подтверждена моками.

## Фаза 4b — Заказы, файлы, детали kwork ✅ (основное)
**Ветка:** `feature/phase-4b-orders-files`
- ✅ `orders`: `details`, `header`, `files`, `approve`, `approve_stages`,
  `send_for_approval`/`send_for_revision`/`send_requirements`, `repeat`, `send_bonus`,
  `cancel_by_worker`/`cancel_by_payer` (best-effort), `create_review`/`edit_review`/
  `delete_review`, `create_answer`.
- ✅ `kworks` (чтение): `details` (getKworkDetails), `reviews`, `portfolios`.
- ✅ `files`: `upload`, `upload_voice` (multipart с файловой частью; транспорт расширен).
- ✅ FastAPI: детали/приём заказа, загрузка файла (UploadFile).
- ✅ Экстры: `available_extras`, `ordered_extras`, `buy_extras`, `accept_extra`,
  `decline_extra`, `delete_extra`.
- ✅ Стадии: `accept_stage`, `reject_stage`, `pay_stage`, `update_stage_progress`.
- ✅ Арбитраж/отчёты: `rate_arbitration`, `send_report`.
- ✅ Голосовые: `voice_transcription`, `mark_voice_heard`, `voice_convert_status`,
  `files.upload_voice`.
- ✅ Аватар: `account.update_avatar` (multipart `/updateAvatar`).
- ✅ Полный поток отмены заказа: `cancel_by_payer`/`cancel_by_worker` (с reason_type/
  message), `cancellation_reasons`, `cancel_awaiting_payment`/`pay_awaiting_payment`,
  `confirm_cancel_*`/`reject_cancel_*`/`delete_cancel_*` (payer/worker).
- ✅ Пресеты опций: `custom_options_presets`, `offer_options`.
- ✅ Тесты: моки полей и multipart-загрузки (58 тестов всего).

## Фаза 5 — FastAPI-сервис ✅
**Ветка:** `feature/phase-5-fastapi`
- ✅ Роутеры на все группы: auth, account, catalog, search, exchange, users, kworks,
  orders, messages.
- ✅ Аутентификация сервиса: `/auth/login` → токен, далее заголовок `X-Kwork-Token`.
- ✅ Стателесс-зависимости (клиент на запрос, стабильный `uad` сервиса).
- ✅ Маппинг ошибок библиотеки в HTTP: 401 (auth), 429 (rate-limit/анти-бот),
  502 (ошибка API kwork), 500 (прочее).
- ✅ Swagger `/docs`, ReDoc `/redoc`.
- ✅ Тесты: FastAPI TestClient с фейковым транспортом (9 тестов, проверка
  маршрутов/ошибок/OpenAPI).

## Фаза 6 — Надёжность и качество ✅
**Ветка:** `feature/phase-6-hardening`
- **Анти-бот (подтверждено на практике):** частые входы `/signIn` с разными `uad`
  с одного IP приводят к HTTP 403. Реализовано: 403 → понятная ошибка,
  опциональный троттлинг (`min_request_interval`), переиспользование `uad`/сессии
  (`from_session`), ретраи и бэкофф на 429/сеть.
- ✅ Троттлинг (минимальный интервал между запросами), ретраи, таймауты,
  корректное закрытие пулов (`aclose`/контекст-менеджер).
- ✅ Типизация `mypy` (чисто по `kworkapi`), линт `ruff` (чисто).
- ✅ Покрытие тестами **88%** (цель ≥80%), 41 тест.
- ✅ CI (GitHub Actions): ruff + mypy + pytest на Python 3.11–3.13.

## Фаза 7 — Релиз и DX ✅
**Ветка:** `release/0.1.0` → `main` (тег `v0.1.0`)
- ✅ README с быстрым стартом (библиотека + сервис), CHANGELOG (0.1.0).
- ✅ Версия 0.1.0 (semver) в pyproject и `kworkapi.__version__`.
- ✅ Дисклеймер ToS в README; рекомендации по этичному использованию (троттлинг,
  личное применение, переиспользование сессии).
- ⬜ Публикация на PyPI — по необходимости.

---

## Фаза 8 — Полное покрытие API ✅
**Ветка:** `feature/phase-8-completeness`
- ✅ `account`: телефон (add/verify/whatsapp), удаление аккаунта, компания/yescrow,
  баланс (bill_refill_url, set_notify_card_refill), push (allow/register/received),
  голосовые настройки, роль/самозанятость/выходные, гео (countries/cities/timezones),
  public_features/captcha_status/web_auth_token/is_dialog_allowed.
- ✅ `auth`: регистрация (`register`), сброс пароля (`reset_password`).
- ✅ `users`: kworks_categories, kworks_statuses, blocked_dialogs.
- ✅ `exchange`: get_offer, projects_count (с фильтрами), set_favorite_categories.
- ✅ `kworks`: details_extra, faq, links_table, complain_categories, recharge_balance.
- ✅ `messages`: get_message, complain, mark_tracks_read, hide_dialog, send_status.
- ✅ `orders`: worker_in_progress, allow/delete_portfolio, edit_answer, send_receipt,
  экстры исполнителя (decline/delete) и поток удаления экстры (accept/decline).
- ✅ Новые ресурсы: `portfolio` (categories/list), `tracks` (list/search/edit/delete/
  read), `misc` (tos/terms/privacy/resolution/in_app_notification).
- ✅ **12 ресурсов, 166 публичных методов**, 68 тестов, покрытие 84%.
- ⬜ Сознательно опущены методы с JSON-телом (`@Body`), форму которого не дал захват:
  deleteWant/stopWant/restartWant/wantsStatusList, orderKwork, createKworkComplain,
  socialSignIn — добавятся при появлении образца тела.

## Сквозные правила
- **gitflow**: фичи → `develop`, релизы → `main`, теги semver.
- **Коммиты**: Conventional Commits (`feat:`/`fix:`/`docs:`/`refactor:`/`test:`/`chore:`),
  подробно, на русском.
- **Тесты**: новый функционал — только с тестами; сеть мокается.
- **Документация**: каждая фаза обновляет `docs/` (особенно `03-endpoints.md` при изменениях).
- **Секреты**: только в `.env` (gitignore); артефакты перехвата — в `research/captures/` (gitignore).
