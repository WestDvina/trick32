"""Brand palette (trick32.ru) + graphic presets: real Lucide icons in the OG panel."""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import icons as I

# --- Corporate palette of trick32.ru (assets/css/schemes/trick32.css + custom.css) ---
BG_TOP = (3, 7, 18)            # neutral-950  #030712
BG_BOT = (11, 15, 20)          # #0B0F14
WHITE = (255, 255, 255)
MINT = (236, 253, 245)         # #ECFDF5
GREEN = (0, 224, 127)          # primary-500  #00E07F
GREEN_600 = (0, 200, 113)      # primary-600  #00C871 (brand dot)
GREEN_700 = (0, 172, 97)       # primary-700  #00AC61
GREEN_900 = (0, 112, 63)       # primary-900  #00703F
INK = (2, 44, 34)              # #022C22
GRAY = (161, 161, 170)         # neutral-400  #A1A1AA
PANEL_BG = (24, 24, 27)        # neutral-900  #18181B
PANEL_BORDER = (38, 38, 38)    # #262626
RED = (239, 68, 68)            # semantic danger (miner / error)

FONT_DIR = Path(__file__).parent / "fonts"
F_BLACK = FONT_DIR / "RussoOne-Regular.ttf"
F_BOLD = FONT_DIR / "LiberationSans-Bold.ttf"
F_REG = FONT_DIR / "LiberationSans-Regular.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def background(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), BG_BOT)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)],
               fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    return img


def glow(img: Image.Image, cx: int, cy: int, r: int, color, alpha: int = 80):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in range(r, 0, -6):
        a = int(alpha * (1 - i / r) ** 1.6)
        od.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(*color, a))
    ov = ov.filter(ImageFilter.GaussianBlur(46))
    img.paste(ov, (0, 0), ov)


def panel(img: Image.Image, box, radius: int = 18):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=PANEL_BG, outline=PANEL_BORDER, width=2)


def _hex(rgb):
    return "#%02x%02x%02x" % rgb


# preset -> (lucide icon, label, color, danger)
PRESETS = {
    "miner":    ("activity",      "ЗАГРУЗКА ЦП",   RED,   True),
    "malware":  ("bug",           "ВРЕДОНОС",      RED,   True),
    "lock":     ("lock",          "ПАРОЛЬ",        GREEN, False),
    "shield":   ("shield-check",  "ЗАЩИТА",        GREEN, False),
    "key":      ("key-round",     "АКТИВАЦИЯ",     GREEN, False),
    "update":   ("refresh-cw",    "ОБНОВЛЕНИЕ",    GREEN, False),
    "error":    ("triangle-alert", "ОШИБКА",       RED,   True),
    "network":  ("wifi",          "СЕТЬ И WI-FI",  GREEN, False),
    "download": ("download",      "СКАЧАТЬ",       GREEN, False),
    "hardware": ("cpu",           "ЖЕЛЕЗО",        GREEN, False),
    "monitor":  ("monitor",       "ЭКРАН",         GREEN, False),
    "apps":     ("layout-grid",   "ПРОГРАММЫ",     GREEN, False),
    "phone":    ("smartphone",    "ВНИМАНИЕ",      GREEN, False),
    "disk":     ("hard-drive",    "НАКОПИТЕЛЬ",    GREEN, False),
    "terminal": ("terminal",      "КОМАНДЫ",       GREEN, False),
    "settings": ("settings",      "НАСТРОЙКИ",     GREEN, False),
    "user":     ("user-round",    "ПОЛЬЗОВАТЕЛЬ",  GREEN, False),
    "time":     ("clock",         "НАПОМИНАНИЯ",   GREEN, False),
    "generic":  ("circle-dot",    "",              GREEN, False),
}

GRAPHICS = {k: v[0] for k, v in PRESETS.items()}


def draw(img: Image.Image, box, preset: str):
    x0, y0, x1, y1 = box
    panel(img, box)
    icon, label, color, _ = PRESETS.get(preset, PRESETS["generic"])
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2 - (18 if label else 0)
    size = int(min(x1 - x0, y1 - y0) * 0.52)
    I.paste(img, icon, cx, cy, size, _hex(color), stroke=1.5)
    if label:
        d = ImageDraw.Draw(img)
        d.text((cx, y1 - 44), label, font=font(F_BOLD, 25), fill=color, anchor="mm")


_KEYWORDS = [
    ("miner",    r"майнер|майнинг|скрыт.*процесс|нагрузк.*цп"),
    ("malware",  r"вредонос|вирус|шифровальщик|ransom|malware|зловред|троян|заражен|бэкдор|шпион"),
    ("lock",     r"пароль|bitlocker|битлокер|шифрован|вход в систему|логин"),
    ("shield",   r"defender|антивирус|безопасн|firewall|брандмауэр|фаервол|целостност|изоляц|защит|ublock|блокировщик|adblock"),
    ("key",      r"активац|kms|лиценз|ключ"),
    ("error",    r"ошибк|error|сбо[йя]|не работает|перестал|зависа|вылет|не ставится|не запускается|ms-gamingoverlay|sentinel"),
    ("network",  r"wi-fi|wifi|сеть|интернет|трафик|подключен|прокси|dns"),
    ("settings", r"настройк|меню|панель задач|контекстн|тема|интерфейс|\bпуск\b|powertoys|конфиденц|параметр"),
    ("download", r"\biso\b|скачать|загрузк|cloud rebuild"),
    ("monitor",  r"скриншот|экран|дисплей|монитор|разрешен"),
    ("apps",     r"open-source|программ|утилит|софт|приложен|portable"),
    ("phone",    r"телефон|смартфон|мозг|внимани|привычк|экранное время"),
    ("hardware", r"процессор|ddr\d|\bintel\b|amd|видеокарт|gpu|материнск|железо|чип"),
    ("disk",     r"диск|ssd|hdd|раздел|накопит|формат|ntfs|exfat|gpt|памят|место|хранилищ|резервн|onedrive|бэкап|backup"),
    ("terminal", r"терминал|powershell|команд|консоль|скрипт|разработчик|wsl|zenith|linux|ubuntu"),
    ("user",     r"возраст|пользовател|родител|аккаунт|профил|age api"),
    ("time",     r"напоминалк|даты|коммуналк|поверк|календар|расписан|таймер"),
    ("update",   r"обновлен|26h2|25h2|24h2|kb\d|версия|апдейт|release|preview|сборк|hiberfil|сброс"),
]


def pick_preset(text: str) -> str:
    t = (text or "").lower()
    for name, rx in _KEYWORDS:
        if re.search(rx, t):
            return name
    return "generic"
