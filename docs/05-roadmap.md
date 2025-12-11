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
- ⬜ (опц.) Валидация живым трафиком через mitmproxy/Frida — подтвердить формы ответов.

## Фаза 2 — Ядро транспорта и авторизация ⬜
**Ветка:** `feature/phase-2-core-auth`
- Подставить реальные константы: base URL, `Authorization`, генератор `uad`.
- `transport`: общие поля, `Cookie: slrememberme`, разбор `DataResponse`/`paging`/`error`.
- `auth`: `signIn` → `Session{token, slrememberme, expired}`; ветки `signInWithCaptcha`,
  подтверждение телефоном; `logout`.
- Хранилище сессии (файл/конфиг) + переиспользование `uad`.
- **Проверка:** реальный логин тестовым аккаунтом, получение `token` (с учётом капчи).
- Тесты: разбор обёрток, ошибки, авторизация (моки) + 1 интеграционный (опц., помечен).

## Фаза 3 — Чтение каталога и бирж ⬜
**Ветка:** `feature/phase-3-read`
- `account`: `me`/`actor`, `notifications`, `balance`, `features`.
- `catalog`: `rubrics`, `categories`, `kworks`, `favorites`, `viewed`, `filters`.
- `search`: `kworks`, `users`.
- `exchange`: `projects` (лента биржи), `categories`, `getProjectsCount`.
- `users`: `info`, `userKworks`, `reviews`.
- `kworks`: `details`, `reviews`, `answers`, `portfolios`.
- Pydantic-модели для этих ответов (по полям из кода + проверка).
- Тесты на каждый ресурс (моки фикстур ответов).

## Фаза 4 — Действия и сообщения ⬜
**Ветка:** `feature/phase-4-actions`
- `messages`: `dialogs`, `getDialog` (история), `inboxCreate` (отправка), `forward`,
  `edit`, `delete`, `read`, `searchMessages`, голосовые/треки.
- `exchange`: `offer`/`deleteOffer`/`myOffers`, управление «wants», `setFavorite`.
- `orders`: `workerOrders`/`payerOrders`, `details`, `approve`, `cancel`*, стадии,
  экстры, отзывы (`createReview`), отчёты.
- `kworks` (исполнитель): `create`/`pause`/`start`/`delete`, статусы.
- `account` (настройки): `updateSettings`, смена email/username/пароля/телефона,
  `setTakingOrders`, голосовые настройки, аватар (multipart).
- Тесты действий (моки) + проверка корректных тел запросов.

## Фаза 5 — FastAPI-сервис ⬜
**Ветка:** `feature/phase-5-fastapi`
- Роутеры на все группы ресурсов, аккуратные request/response-схемы.
- Аутентификация сервиса (`/auth/login` → токен, `X-Kwork-Token`).
- Обработчики ошибок → корректные HTTP-коды (401/429/4xx).
- Swagger с примерами, README по запуску.
- Тесты эндпоинтов (FastAPI TestClient + замоканный клиент).

## Фаза 6 — Надёжность и качество ⬜
**Ветка:** `feature/phase-6-hardening`
- Rate-limit/троттлинг, бэкофф, обработка капчи/ограничений.
- Логирование, ретраи, таймауты, корректное закрытие пулов.
- Полная типизация (`mypy`), линт (`ruff`), pre-commit.
- Покрытие тестами ≥ 80%, фикстуры реальных ответов из перехвата.
- CI (GitHub Actions): линт + типы + тесты.

## Фаза 7 — Релиз и DX ⬜
**Ветка:** `release/0.1.0` → `main`
- README с примерами по каждому ресурсу, CHANGELOG.
- Публикация на PyPI (опц.), версионирование semver.
- Дисклеймер ToS, гайд по этичному использованию (троттлинг, личное применение).

---

## Сквозные правила
- **gitflow**: фичи → `develop`, релизы → `main`, теги semver.
- **Коммиты**: Conventional Commits (`feat:`/`fix:`/`docs:`/`refactor:`/`test:`/`chore:`),
  подробно, на русском.
- **Тесты**: новый функционал — только с тестами; сеть мокается.
- **Документация**: каждая фаза обновляет `docs/` (особенно `03-endpoints.md` при изменениях).
- **Секреты**: только в `.env` (gitignore); артефакты перехвата — в `research/captures/` (gitignore).
