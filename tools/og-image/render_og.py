#!/usr/bin/env python3
"""Render a 1200x630 OG image for trick32 / Уловка-32 in the site's brand palette.

One template for all articles: only the hook (3-5 words) and the graphic preset change.

Hard guarantees:
  - every text line width <= TEXT_W
  - title fits in <= TITLE_MAX_LINES lines and stays above the accent line
  - accent fits on one line above the graphic panel
If a phrase is too long, words are dropped from the tail (never a broken mid-word cut).

Usage:
  render_og.py --title "СКРЫТЫЙ МАЙНЕР?" --slug kak-najti-majner --graphic miner \
      --accent "6 ПРОВЕРОК" --category windows --out out.jpg

  # from a full article title (auto-hook + auto-accent):
  render_og.py --from-title --title "<full title>" --slug x --out y.jpg
"""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw

import presets as P

W, H = 1200, 630
MARGIN = 72
TEXT_X = MARGIN
TEXT_W = 568                 # x 72..640; graphic panel starts at 672
TITLE_TOP = 168
TITLE_BOTTOM = 418           # accent at 432, divider at 512
ACCENT_Y = 432
GRAPH_BOX = (672, 148, 1128, 466)
DIVIDER_Y = 512
FOOTER_Y = 528
TITLE_HI, TITLE_LO = 118, 68
TITLE_MAX_LINES = 2

STOP = {
    "как", "что", "и", "в", "во", "на", "для", "с", "со", "по", "за", "от", "до",
    "а", "но", "или", "это", "этот", "эта", "эти", "которые", "который", "которая",
    "которое", "почему", "когда", "где", "чем", "все", "весь", "вся", "ещё", "уже",
    "вы", "ваш", "вас", "я", "мы", "он", "она", "оно", "они", "не", "ни", "же", "ли",
    "бы", "то", "так", "свой", "свои", "свою", "меня", "нам", "мне", "без", "про",
    "под", "над", "при", "из", "у", "о", "об", "был", "была", "было", "если", "лишь",
}
WORD_RX = re.compile(r"[A-Za-zА-Яа-яЁё0-9][A-Za-zА-Яа-яЁё0-9\.\-]*")


def _words(text: str):
    return WORD_RX.findall(text or "")


def _trim_tail(words):
    while len(words) > 1 and words[-1].lower().strip(".,:;") in STOP:
        words = words[:-1]
    return words


def split_title(title: str) -> tuple:
    """Full article title -> (hook, accent).

    Keeps word order (no mid-phrase stopword removal), drops only the tail.
    The part after ':' / '—' becomes the accent.
    """
    t = (title or "").strip()
    t = re.sub(r"[\(\[«][^)\]}»]*[\)\]»]", " ", t)
    t = t.replace("«", "").replace("»", "").replace('"', "").strip()
    parts = re.split(r"\s*[:—–]\s*|\s+-\s+", t, maxsplit=1)
    main = parts[0].strip()
    sub = parts[1].strip() if len(parts) > 1 else ""

    mw = _words(main)
    if len(mw) <= 1 and sub:                      # e.g. "BitLocker: как ..."
        mw = mw + _words(sub)
        sub = ""

    hook = " ".join(_trim_tail(mw[:5])).upper()
    accent = " ".join(_trim_tail(_words(sub)[:4])).upper()
    return hook, accent


def _wrap(d, words, fnt, max_w):
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if d.textlength(cand, font=fnt) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _maxw(d, lines, fnt):
    return max((d.textlength(l, font=fnt) for l in lines), default=0)


def _size_for(d, words, max_w, max_lines, hi, floor):
    for size in range(hi, floor - 1, -4):
        f = P.font(P.F_BLACK, size)
        lines = _wrap(d, words, f, max_w)
        if len(lines) <= max_lines and _maxw(d, lines, f) <= max_w:
            return f, lines, size
    return None


def fit_title(d, text, max_w=TEXT_W, max_lines=TITLE_MAX_LINES,
              hi=TITLE_HI, lo=TITLE_LO):
    """Longest prefix of `text` that fits `max_w` in <= max_lines.

    Priority: keep as many words as possible at a readable size. Tries size floors
    84 -> 68 -> 52 -> 40 and, within each floor, the longest prefix first.
    Never cuts mid-word, never returns a lone function word ("КАК", "И", "ОТ").
    """
    words = text.split()
    for floor, min_words in ((84, 2), (lo, 2), (52, 2), (40, 1)):
        min_n = min(min_words, len(words))
        for n in range(len(words), min_n - 1, -1):
            cand = _trim_tail(words[:n])
            if not cand:
                continue
            if len(cand) == 1 and cand[0].lower() in STOP:
                continue
            got = _size_for(d, cand, max_w, max_lines, hi, floor)
            if got:
                return got
    first = [w for w in words if w.lower() not in STOP] or words
    f = P.font(P.F_BLACK, 40)
    return f, [first[0]], 40


def fit_accent(d, text, max_w):
    """One-line accent that fits max_w; drops tail words if needed."""
    words = text.split()
    while words:
        for size in range(42, 24, -2):
            f = P.font(P.F_BOLD, size)
            if d.textlength(" ".join(words), font=f) <= max_w:
                return P.font(P.F_BOLD, size), " ".join(words), size
        words = words[:-1]
    return P.font(P.F_BOLD, 24), text[:10], 24


def render(title, slug="", graphic="auto", accent="", category="", footer="", tags="",
           from_title=False):
    if from_title:
        hook, auto_acc = split_title(title)
        accent = accent or auto_acc
        title = hook

    img = P.background(W, H)
    d = ImageDraw.Draw(img)

    preset = graphic if graphic in P.PRESETS else P.pick_preset(f"{title} {accent} {tags} {category}")
    danger = P.PRESETS.get(preset, P.PRESETS["generic"])[3]
    glow_color = P.RED if danger else P.GREEN_900
    P.glow(img, 900, 307, 250, glow_color, alpha=64 if danger else 58)
    P.draw(img, GRAPH_BOX, preset)
    d = ImageDraw.Draw(img)

    f_brand = P.font(P.F_BOLD, 40)
    bx, by = MARGIN, 46
    d.text((bx, by), "УЛОВКА", font=f_brand, fill=P.WHITE)
    bw = d.textlength("УЛОВКА", font=f_brand)
    dcx = bx + bw + 14
    d.ellipse([dcx - 7, by + 22 - 7, dcx + 7, by + 22 + 7], fill=P.GREEN_600)
    d.text((dcx + 14, by), "32", font=f_brand, fill=P.WHITE)

    cat_disp = category.replace("-", " ").replace(",", " · ").strip()
    if cat_disp:
        d.text((W - MARGIN, 52), cat_disp.upper(),
               font=P.font(P.F_BOLD, 26), fill=P.GREEN, anchor="ra")

    f_title, lines, size = fit_title(d, title)
    lh = int(size * 1.06)
    block_h = len(lines) * lh
    y = TITLE_TOP + (TITLE_BOTTOM - TITLE_TOP - block_h) // 2
    for ln in lines:
        d.text((TEXT_X, y), ln, font=f_title, fill=P.WHITE)
        y += lh

    if accent:
        f_acc, acc_text, asize = fit_accent(d, accent, TEXT_W - 34)
        d.ellipse([TEXT_X, ACCENT_Y + asize // 2 - 3,
                   TEXT_X + 14, ACCENT_Y + asize // 2 + 11], fill=P.GREEN_600)
        d.text((TEXT_X + 30, ACCENT_Y), acc_text, font=f_acc, fill=P.GREEN)

    d.line([(MARGIN, DIVIDER_Y), (W - MARGIN, DIVIDER_Y)], fill=(31, 41, 55), width=2)
    meta = footer or f"trick32.ru · {(cat_disp or 'статьи').lower()}"
    d.text((MARGIN, FOOTER_Y), meta, font=P.font(P.F_REG, 26), fill=P.GRAY)

    return img


def save(img, out: Path, quality=88, max_kb=300):
    out.parent.mkdir(parents=True, exist_ok=True)
    q = quality
    while True:
        img.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        kb = out.stat().st_size / 1024
        if kb <= max_kb or q <= 55:
            return kb
        q -= 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="")
    ap.add_argument("--from-title", dest="from_title", action="store_true")
    ap.add_argument("--slug", default="")
    ap.add_argument("--graphic", default="auto")
    ap.add_argument("--accent", default="")
    ap.add_argument("--category", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--footer", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()
    if not args.title:
        ap.error("--title required")

    img = render(args.title, args.slug, args.graphic, args.accent, args.category,
                 args.footer, args.tags, from_title=args.from_title)
    out = Path(args.out).expanduser()
    if args.png:
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, "PNG")
        kb = out.stat().st_size / 1024
    else:
        kb = save(img, out)

    d = ImageDraw.Draw(img)
    shown = split_title(args.title)[0] if args.from_title else args.title
    f, lines, size = fit_title(d, shown)
    print(f"Saved {out} {W}x{H} ratio {W/H:.4f} {kb:.0f} KB | lines={len(lines)} "
          f"size={size} maxw={int(_maxw(d, lines, f))} (limit {TEXT_W})")


if __name__ == "__main__":
    main()
