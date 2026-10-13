# og-image — генератор OG-карточек для trick32.ru

Рисует OG-превью 1200×630 для статей сайта trick32.ru и канала «Уловка-32»
в корпоративной палитре сайта (зелёный на почти-чёрном). Один шаблон: меняются
только заголовок 3–5 слов и векторный образ.

Живёт в репозитории сайта, поэтому карточку умеет нарисовать и GitHub Actions
(шаг «Draw missing OG cards» в `.github/workflows/hugo.yml`), и локальный MCP-сервер.

## Зачем

Telegram/VK/OK сжимают превью до ~300 px, поэтому нужен крупный текст и один образ,
а не весь заголовок. Единый шаблон = узнаваемость в лентах.

## Что где

| Файл | Назначение |
|---|---|
| `render_og.py` | шаблон карточки, вписывание хука в блок 568×250, сохранение JPEG ≤300 КБ |
| `presets.py` | палитра, шрифты, пресеты-иконки, авто-выбор пресета по ключевым словам |
| `icons.py`, `icons/` | растеризация SVG Lucide (ISC) через cairosvg |
| `articles.py` | frontmatter статей и `hooks.json` — общий код CLI и MCP |
| `generate_og.py` | пакетный прогон по `content/articles` + сторож |
| `server.py` | MCP-сервер (6 инструментов) |
| `fonts/` | вшитые шрифты, см. `fonts/README.md` |
| `hooks.json` | ручные хуки `slug → {hook, accent}` |

## CLI

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# дорисовать только отсутствующие карточки (то, что делает CI)
.venv/bin/python generate_og.py

# проверить, что у каждой не-черновой статьи есть карточка
.venv/bin/python generate_og.py --check-only

# перерисовать одну карточку
.venv/bin/python generate_og.py --only kak-najti-majner --force

# одна карточка вручную
.venv/bin/python render_og.py --title "СКРЫТЫЙ МАЙНЕР?" --slug kak-najti-majner \
  --graphic miner --accent "6 ПРОВЕРОК" --category windows --out /tmp/out.jpg
```

`generate_og.py` не трогает существующие карточки (кроме `--force`) и падает
с кодом 1, если карточку не удалось нарисовать или у не-черновой статьи её нет.
Черновики (`draft: true`) сборку не роняют.

Если во frontmatter нет `images:`, скрипт дописывает `images: ["/og/<slug>.jpg"]` —
иначе нарисованная карточка не попадёт в HTML. Существующее значение не перезаписывается:
картинку могли выбрать вручную. Frontmatter читается с терпимостью к BOM и CRLF
(иначе статья с Windows получила бы карточку с именем папки вместо заголовка).

Вывод по умолчанию: `static/og/<slug>.jpg` → URL `/og/<slug>.jpg`.
Фолбэк `/og-img.jpg` остаётся для страниц без своей картинки.

## Хуки (`hooks.json`)

`slug → {hook, accent}`. `generate_og.py` берёт хук оттуда; если записи нет — строит
авто-хук из заголовка (без обрубков вроде одиночного «КАК»). Качественные хуки пишет
агент через MCP-инструмент `og_set_hook`.

Смена хука не перерисовывает уже готовую карточку: запусти
`generate_og.py --only <slug> --force` и закоммить `.jpg`.

Вёрстка жёстко ограничена: строка заголовка ≤ 568 px, ≤ 2 строк, блок не заходит на
акцент и панель. Длинная фраза укорачивается отбрасыванием хвоста, без обрезки посреди слова.

## Шрифты

Вшиты в репозиторий (OFL 1.1): Russo One — заголовок, Liberation Sans Regular/Bold —
бренд, акцент, футер. Так macOS и раннер GitHub Actions рисуют одинаково, и не нужен
ни Arial, ни EULA mscorefonts. Подробности — `fonts/README.md`.

## MCP-сервер

```bash
.venv/bin/pip install -r requirements-mcp.txt
```

Регистрация в `~/.config/opencode/opencode.jsonc`: `server.py` через
`.venv/bin/python3`. Инструменты: `og_generate`, `og_preview`, `og_batch`,
`og_set_hook`, `og_apply_frontmatter`, `og_list_presets`.

## Пресеты (иконки Lucide)

| Пресет | Иконка | Подпись |
|---|---|---|
| `miner` | activity | ЗАГРУЗКА ЦП (красный) |
| `malware` | bug | ВРЕДОНОС (красный) |
| `lock` | lock | ПАРОЛЬ |
| `shield` | shield-check | ЗАЩИТА |
| `key` | key-round | АКТИВАЦИЯ |
| `update` | refresh-cw | ОБНОВЛЕНИЕ |
| `error` | triangle-alert | ОШИБКА (красный) |
| `network` | wifi | СЕТЬ И WI-FI |
| `download` | download | СКАЧАТЬ |
| `monitor` | monitor | ЭКРАН |
| `apps` | layout-grid | ПРОГРАММЫ |
| `phone` | smartphone | ВНИМАНИЕ |
| `hardware` | cpu | ЖЕЛЕЗО |
| `disk` | hard-drive | НАКОПИТЕЛЬ |
| `terminal` | terminal | КОМАНДЫ |
| `settings` | settings | НАСТРОЙКИ |
| `user` | user-round | ПОЛЬЗОВАТЕЛЬ |
| `time` | clock | НАПОМИНАНИЯ |
| `generic` | circle-dot | — |
| `auto` | — | выбор по заголовку/тегам/категории |

Добавить иконку: положить SVG Lucide в `icons/` и дописать строку в `PRESETS` (`presets.py`).

## Палитра (из assets/css/schemes/trick32.css + custom.css)

- primary `#00E07F`, brand-точка `#00C871`, тёмный `#00AC61` / `#00703F`
- фон `#030712` → `#0B0F14`, текст `#FFFFFF` / `#ECFDF5`, второстепенный `#A1A1AA`
- ink `#022C22`
- красный `#EF4444` — только семантика опасности (`miner`, `malware`, `error`)

## Скилл

`~/.config/opencode/skills/og-image/SKILL.md` — воркфлоу: прочитать статью → хук 3–5 слов
→ пресет → генерация → превью 300px → frontmatter по подтверждению.
