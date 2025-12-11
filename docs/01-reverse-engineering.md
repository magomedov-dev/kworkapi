# 01. Реверс-инжиниринг приватного API kwork

Как мы получили карту API без официальной документации.

## Окружение

- Рутованное устройство **Redmi Note 7 (lavender)**, Android **13**, arm64-v8a, root через Magisk.
- adb-serial: `276bcca9`.
- Пакет приложения: **`ru.kwork.app`** (App Bundle: `base.apk` + `split_config.arm64_v8a` + `split_config.xxhdpi`).

## Инструменты (в `.tooling/`, вне репозитория)

| Инструмент | Назначение |
|---|---|
| `adb` (android-tools) | связь с устройством, извлечение APK |
| `jadx` 1.5.5 | декомпиляция APK → Java-исходники |
| `mitmproxy` | перехват HTTPS-трафика (этап валидации) |
| `frida` 17.12.0 + `frida-server` (на устройстве) | обход SSL pinning (этап валидации) |

## Шаг 1. Извлечение и декомпиляция APK

```bash
adb -s 276bcca9 shell pm path ru.kwork.app
adb -s 276bcca9 pull <path>/base.apk research/captures/kwork-base.apk
.tooling/jadx/bin/jadx -d research/captures/kwork-src research/captures/kwork-base.apk
```

Результат: ~16 000 Java-файлов. Код частично обфусцирован (короткие имена пакетов
`cy`, `nr`, `mc`…), но **слой данных `ru.kwork.app.data` сохранил осмысленные имена**.

## Шаг 2. Что найдено в коде

### Retrofit-слой — главный источник

`ru/kwork/app/data/remote/*Service.java` — 14 интерфейсов Retrofit. Это и есть
описание API: каждый метод аннотирован HTTP-глаголом и путём, параметры —
аннотациями полей. Пример из `CatalogService`:

```java
@e                                  // @FormUrlEncoded
@o("/searchKworks")                 // @POST("/searchKworks")
Object searchKworks(@c("query") String query, @c("categoryId") Integer cat,
                    @c("page") Integer page, @c("token") String token,
                    @i("Authorization") String auth, @i("Cookie") Set<String> cookie, ...);
```

Соответствие обфусцированных аннотаций Retrofit:

| В коде | Retrofit | Значение |
|---|---|---|
| `@o("…")` | `@POST` | путь, POST |
| `@f("…")` | `@GET` | путь, GET |
| `@e` | `@FormUrlEncoded` | форма |
| `@c("name")` | `@Field` | поле формы |
| `@d` | `@FieldMap` | карта полей |
| `@i("Header")` | `@Header` | заголовок |
| `@a` | `@Body` | тело (JSON) |
| `@q` | `@Part` | multipart |

Каталог всех методов сгенерирован парсером `research/extract_endpoints.py` →
[03-endpoints.md](03-endpoints.md).

### Базовый URL — `cy/d.java` (ServerManager)

```java
// host: "ru" → "kwork.ru", "en" → "kwork.com", иначе "<lang>.kwork.com"
// baseUrl:
return "https://api." + host + "/";   // => https://api.kwork.ru/
```

### Авторизация — `nr/d.java` (PreferencesHelper) + `ActorRepo`

Заголовок `Authorization` берётся из `preferencesHelper.a()` и подставляется в
**каждый** вызов сервиса (включая `/signIn`). Значение строится из двух констант:

```java
getString("serverlogin",    "mobile_api")   // c()
getString("serverpassword", "qFvfRl7w")     // d()
// a() = "Basic " + base64("mobile_api:qFvfRl7w")
//     = Basic bW9iaWxlX2FwaTpxRnZmUmw3dw==
```

Это не пользовательский токен, а статичный идентификатор клиента-приложения.

### Параметр `uad` — идентификатор установки (`nr/d.java` метод `i()`)

```java
SHA-1( "35" + Σ(len(BuildProp_i) % 10 для 14 build-свойств)
            + Settings.Secure.ANDROID_ID
            + System.currentTimeMillis() )
```

Считается один раз и кэшируется в SharedPreferences (`uad`). Для нашей библиотеки
достаточно сгенерировать один стабильный псевдослучайный hex и переиспользовать.

### Сессия — `token` + cookie `slrememberme` (`nr/d.java`)

- `/signIn` возвращает `SignInResponse` с пользовательским `token`.
- `token` передаётся полем формы во всех авторизованных запросах.
- Дополнительно отправляется `Cookie: slrememberme=<value>`.
- На устройстве `token`/`slrememberme` хранятся **зашифрованными** (Crypto + Base64),
  но в сеть уходят в открытом виде — нам шифрование хранилища не нужно.

## Шаг 3. Валидация живым трафиком (этап roadmap)

Статический анализ даёт пути и поля; формы ответов уточняются перехватом:

1. CA mitmproxy в системные сертификаты (Android 13 + Magisk-модуль/bind-mount cacerts).
2. `frida-server` (root) + universal SSL unpinning, если приложение использует pinning.
3. Прогон сценариев в приложении → экспорт flow в `research/captures/` (gitignore).

См. [research/README.md](../research/README.md) для пошаговых команд.
