# 02. Справочник по API kwork

Описание приватного API `api.kwork.ru`, реконструированного из приложения.

## Базовый URL

```
https://api.kwork.ru/
```

Хост зависит от языкового сервера: `ru` → `api.kwork.ru`, `en` → `api.kwork.com`.
По умолчанию работаем с `api.kwork.ru`.

## Транспорт

- Метод: преимущественно **POST**, тело `application/x-www-form-urlencoded`
  (несколько методов — `@Body` JSON или `multipart` для загрузки файлов).
- Путь метода добавляется к базовому URL: `POST https://api.kwork.ru/signIn`.

## Заголовки

| Заголовок | Значение | Обязателен |
|---|---|---|
| `Authorization` | `Basic bW9iaWxlX2FwaTpxRnZmUmw3dw==` | да, на каждом запросе |
| `Cookie` | `slrememberme=<value>` | для авторизованных запросов |
| `User-Agent` | UA приложения (уточняется перехватом) | желательно |

`Authorization` — статичный идентификатор клиента: `Basic base64("mobile_api:qFvfRl7w")`.
Это не пользователь — это «ключ приложения», одинаковый для всех.

## Общие поля формы

Большинство методов принимают общий набор полей:

| Поле | Назначение |
|---|---|
| `token` | пользовательский токен сессии (после `/signIn`) |
| `uad` | идентификатор установки приложения (см. ниже) |
| `slrememberme` | значение сессии (дублируется в Cookie) |
| `device` | название устройства/клиента |
| `makeOnline` | флаг «отметить пользователя онлайн» (0/1), у части методов |

### Генерация `uad`

```
uad = SHA1_hex( "35"
               + Σ(len(BuildProp_i) % 10)   // 14 свойств Build.*
               + ANDROID_ID
               + currentTimeMillis )
```

Создаётся один раз при первом запуске и кэшируется. В библиотеке генерируем один
стабильный hex-идентификатор и храним его (конфиг/файл), переиспользуя между запусками.

## Авторизация

1. `POST /signIn` с полями `login`, `password`, `recaptcha_pass_token` (опц.) +
   заголовок `Authorization`.
2. Ответ — `SignInResponse`:

```jsonc
{
  "success": true,
  "response": {            // полезная нагрузка DataResponse
    "token": "<user-token>",
    "expired": 1718900000  // срок действия токена
  },
  "phone_mask": "+7 *** *** ** 00",
  "recaptcha_pass_token": "...",
  "is_registration": false
}
```

3. Дальше `token` кладём в поле формы каждого запроса, плюс `Cookie: slrememberme=...`.

> При срабатывании анти-бота вход может потребовать капчу: `signInWithCaptcha`
> (поле `g-recaptcha-response`) или подтверждение телефоном (`phone_last`).

## Капча (Google reCAPTCHA v2) — подтверждено живым трафиком

Признак: `POST /signIn` возвращает **HTTP 200** с телом

```json
{"success": false, "error": "Подтвердите, что вы не робот", "error_code": 118}
```

`error_code 118` = нужна капча. Параметры (захвачены со страницы `/captcha_only`):

| Параметр | Значение |
|---|---|
| Провайдер | Google reCAPTCHA v2 (`https://www.google.com/recaptcha/api.js`) |
| sitekey | `6LdX9CATAAAAAARb0rBU8FXXdUBajy3IlVjZ2qHS` (одинаков для .ru/.com) |
| Страница виджета | `https://kwork.ru/captcha_only` (callback `RecaptchaSuccess`, токен в `#response=`) |

Поток решения:

1. `signIn` → `error_code 118`.
2. Получить `g-recaptcha-response` (WebView на `/captcha_only`, свой виджет с sitekey,
   или решалка вроде 2captcha по sitekey+pageurl). Токен привязан к домену `kwork.ru`
   и живёт ~2 минуты.
3. `POST /signInWithCaptcha` с полями `login`, `password`, `g-recaptcha-response`,
   `recaptcha_pass_token`, `phone_last` → успех + `recaptcha_pass_token` (на верхнем
   уровне ответа, рядом с `response`).
4. `recaptcha_pass_token` передавать в последующие `signIn` (поле `recaptcha_pass_token`),
   чтобы капчу больше не спрашивали.

В библиотеке это `login()` → `LoginChallenge` → `kw.solve_captcha(challenge, token)`
(см. [07-usage.md](07-usage.md)). Есть также картиночная ветка (`captcha_img`/
`captcha_sid`/`captchaCode`) и подтверждение телефоном — для аккаунтов, где включены.

> Внимание: `server: QRATOR` — анти-DDoS Qrator. Его **WAF может отдать HTTP 403**
> без тела — это НЕ капча (решать нечего), а жёсткий лимит; библиотека поднимает
> `KworkRateLimitError`. Капча (118) и WAF-блок (403) — разные механизмы.

## Формат ответов (обёртки)

Иерархия Gson-моделей:

```
BooleanResponse                 // база
  ├─ success: boolean
  ├─ error: String?
  ├─ errorCode: Integer?
  ├─ errors: List<String>?
  └─ restriction: Restriction?  // ограничения/баны

DataResponse<T> extends BooleanResponse
  └─ response: T                // alternate-имена: "data", "portfolio"

PagedResponse<T> extends DataResponse<...>
  └─ paging: { page, total, limit, pages }

MessageResponse extends BooleanResponse
  └─ message: String
```

Практические выводы для клиента:
- **Успех** — `success == true`; данные — в `response` (или `data`/`portfolio`).
- **Ошибка** — `success == false`; текст в `error`, код в `errorCode`, иногда список `errors`.
- **Пагинация** — в объекте `paging` (`page`/`pages`/`total`/`limit`).
- **Ограничения аккаунта** — объект `restriction`.

## Обработка ошибок

| Признак | Трактовка | Исключение в библиотеке |
|---|---|---|
| `success=false` + текст про token/auth | протух/неверен токен | `KworkAuthError` |
| `success=false` + `restriction` | бан/ограничение | `KworkAPIError` (+ payload) |
| HTTP 429 | rate-limit / анти-бот | `KworkRateLimitError` |
| HTTP ≥ 400 | транспортная ошибка | `KworkAPIError` |

## Полный список методов

См. [03-endpoints.md](03-endpoints.md) — 192 эндпоинта в 14 сервисах:
`Actor`, `User`, `Catalog`, `Search`, `Exchange`, `Order`, `Dialog`, `Inbox`,
`Track`, `Notification`, `KworkDetails`, `Kwork`, `Portfolio`, `File`.
