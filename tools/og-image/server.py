import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import presets as P
import render_og
from articles import load_hooks, read_frontmatter, save_hooks

mcp = FastMCP(
    "og-image",
    instructions=(
        "Генератор OG-картинок 1200x630 для trick32.ru / «Уловка-32». "
        "Один шаблон в корпоративной палитре сайта (зелёный на почти-чёрном), "
        "меняются только заголовок 3-5 слов и векторный образ. "
        "output: trick32/static/og/<slug>.jpg, frontmatter images: ['/og/<slug>.jpg']"
    ),
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_STATIC = REPO_ROOT / "static"
OUT_DIR = SITE_STATIC / "og"
CONTENT_DIR = REPO_ROOT / "content" / "articles"
PREVIEW_DIR = Path(__file__).parent / "previews"


def _resolve_out(slug: str, out: str = "") -> Path:
    if out:
        return Path(out).expanduser()
    return OUT_DIR / f"{slug}.jpg"


@mcp.tool()
def og_generate(title: str, slug: str, graphic: str = "auto", accent: str = "",
                category: str = "", tags: str = "", out: str = "",
                from_title: bool = False) -> str:
    """Сгенерировать OG-картинку 1200x630 (одна статья).

    title     — хук 3-5 слов крупным текстом (напр. "СКРЫТЫЙ МАЙНЕР"),
                либо полный заголовок статьи, если from_title=True
    slug      — имя файла без расширения (напр. kak-najti-majner)
    graphic   — auto|miner|malware|lock|shield|key|update|error|network|download|
                monitor|apps|phone|hardware|disk|terminal|settings|user|time|generic
                (полный список — og_list_presets)
    accent    — короткая подпись под заголовком (опц.; при from_title=True
                подставляется автоматически из части после ":")
    category  — категория/рубрика для верхнего бейджа (напр. windows)
    tags      — теги строкой, помогают авто-выбору пресета
    from_title— True: title = полный заголовок, хук и акцент обрежутся автоматически
    """
    path = _resolve_out(slug, out)
    img = render_og.render(title, slug, graphic, accent, category, "", tags,
                           from_title=from_title)
    kb = render_og.save(img, path)
    preset = graphic if graphic in P.PRESETS else P.pick_preset(f"{title} {accent} {tags} {category}")
    return (f"✅ {path}\n   {render_og.W}x{render_og.H} (1.905:1), {kb:.0f} КБ, пресет: {preset}\n"
            f"   frontmatter: images: [\"/og/{path.stem}.jpg\"]")


@mcp.tool()
def og_preview(path_or_slug: str, width: int = 300) -> str:
    """Миниатюра OG-картинки (по умолчанию 300px) — проверка читаемости в ленте Telegram/VK."""
    from PIL import Image
    p = Path(path_or_slug).expanduser()
    if not p.exists():
        p = _resolve_out(path_or_slug)
    if not p.exists():
        return f"❌ не найдено: {path_or_slug}"
    img = Image.open(p)
    h = round(img.height * width / img.width)
    prev = img.resize((width, h), Image.LANCZOS)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out = PREVIEW_DIR / f"{p.stem}-{width}.png"
    prev.save(out, "PNG")
    return f"👁 {out} — {width}x{h}px (проверь: читается ли заголовок в миниатюре)"


@mcp.tool()
def og_batch(articles_dir: str = "", overwrite: bool = False, limit: int = 0,
             out_dir: str = "") -> str:
    """Пакетная генерация OG для всех статей сайта. По умолчанию — content/articles."""
    base = Path(articles_dir).expanduser() if articles_dir else CONTENT_DIR
    if not base.exists():
        return f"❌ нет папки: {base}"
    out_d = Path(out_dir).expanduser() if out_dir else OUT_DIR
    hooks = load_hooks()
    files = sorted([p for p in base.rglob("*.md") if p.name not in ("_index.md",)])
    made, skipped, failed = [], [], []
    for p in files:
        info, _, _ = read_frontmatter(p)
        slug = info["slug"]
        dst = out_d / f"{slug}.jpg"
        if dst.exists() and not overwrite:
            skipped.append(slug)
            continue
        try:
            h = hooks.get(slug)
            if h:                      # hand-written hook from hooks.json wins
                img = render_og.render(h.get("hook", info["title"]), slug, "auto",
                                       h.get("accent", ""), ",".join(info["categories"]),
                                       "", ",".join(info["tags"]))
            else:                      # auto-hook from the full title
                img = render_og.render(info["title"], slug, "auto", "",
                                       ",".join(info["categories"]), "", ",".join(info["tags"]),
                                       from_title=True)
            render_og.save(img, dst)
            made.append(slug)
        except Exception as e:  # noqa: BLE001
            failed.append(f"{slug}: {e}")
        if limit and len(made) >= limit:
            break
    out = [f"Сгенерировано: {len(made)}", f"Пропущено (уже есть): {len(skipped)}"]
    if made:
        out.append("  " + ", ".join(made[:20]) + (" …" if len(made) > 20 else ""))
    if failed:
        out.append("Ошибки: " + "; ".join(failed[:10]))
    out.append(f"Папка: {out_d}")
    return "\n".join(out)


@mcp.tool()
def og_set_hook(slug: str, hook: str, accent: str = "", regenerate: bool = True) -> str:
    """Записать ручной хук (3-5 слов) для статьи в hooks.json и перерисовать картинку.

    Батч уважает hooks.json: где хук задан вручную — берётся он, где нет — авто из заголовка.
    """
    data = load_hooks()
    data[slug] = {"hook": hook.upper(), "accent": accent.upper()}
    save_hooks(data)
    msg = f"✅ hook: {slug} = «{hook.upper()}»" + (f" / «{accent.upper()}»" if accent else "")
    if regenerate:
        info = None
        for p in CONTENT_DIR.rglob("*.md"):
            i, _, _ = read_frontmatter(p)
            if i["slug"] == slug:
                info = i
                break
        cat = ",".join(info["categories"]) if info else ""
        tags = ",".join(info["tags"]) if info else ""
        img = render_og.render(hook, slug, "auto", accent, cat, "", tags)
        kb = render_og.save(img, OUT_DIR / f"{slug}.jpg")
        msg += f"\n   перерисовано: {OUT_DIR / f'{slug}.jpg'} ({kb:.0f} КБ)"
    return msg


@mcp.tool()
def og_apply_frontmatter(article_path: str, slug: str = "", dry_run: bool = True) -> str:
    """Прописать images: ["/og/<slug>.jpg"] в frontmatter статьи.

    Сначала вызывай с dry_run=True и покажи diff автору. После подтверждения — dry_run=False.
    """
    path = Path(article_path).expanduser()
    if not path.exists():
        return f"❌ нет файла: {path}"
    info, text, m = read_frontmatter(path)
    slug = slug or info["slug"]
    new_val = f'images: ["/og/{slug}.jpg"]'

    if m is None:
        return "❌ не нашёл YAML-frontmatter (нет --- в начале файла)"

    fm = m.group(1)
    if re.search(r"^images:.*$", fm, re.MULTILINE):
        new_fm = re.sub(r"^images:.*$", new_val, fm, count=1, flags=re.MULTILINE)
    else:
        anchor = re.search(r"^(tags:.*)$", fm, re.MULTILINE) or re.search(r"^(categories:.*)$", fm, re.MULTILINE)
        if anchor:
            new_fm = fm[:anchor.end()] + "\n" + new_val + fm[anchor.end():]
        else:
            new_fm = fm + "\n" + new_val

    diff = f"- images: {re.search(r'^images:.*$', fm, re.MULTILINE).group(0)[8:] if re.search(r'^images:.*$', fm, re.MULTILINE) else '(нет)'}\n+ {new_val}"
    if dry_run:
        return f"🔍 DRY-RUN {path}\n{diff}\n\nПодтверди — вызову с dry_run=False."

    new_text = text[:m.start(1)] + new_fm + text[m.end(1):]
    path.write_text(new_text, encoding="utf-8")
    return f"✅ Обновлён {path}\n{diff}"


@mcp.tool()
def og_list_presets() -> str:
    """Список доступных пресетов (иконки Lucide) и корпоративная палитра."""
    lines = ["Пресеты (graphic) — иконки Lucide:"]
    for name, (icon, label, color, danger) in P.PRESETS.items():
        tag = " (красный, риск)" if danger else ""
        lbl = label or "без подписи"
        lines.append(f"  {name:9} — {icon:14} {lbl}{tag}")
    lines.append(f"  {'auto':9} — выбор по заголовку/тегам/категории")
    lines.append("")
    lines.append(f"Доступные иконки: {', '.join(P.I.available())}")
    lines.append("")
    lines.append("Палитра: primary #00E07F / #00C871, фон #030712→#0B0F14, "
                 "текст #FFFFFF/#ECFDF5, второстепенный #A1A1AA, "
                 "красный #EF4444 только для риска (miner, error).")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
