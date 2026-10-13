"""Frontmatter and hook storage shared by the MCP server and the CI generator."""
import json
import re
from pathlib import Path

HOOKS_FILE = Path(__file__).parent / "hooks.json"


def load_hooks() -> dict:
    if HOOKS_FILE.exists():
        try:
            return json.loads(HOOKS_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_hooks(data: dict) -> None:
    HOOKS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_frontmatter(path: Path):
    """Return (info, text, frontmatter_match). info: title/categories/tags/draft/images/slug.

    A BOM or CRLF (Windows editors) breaks the `---` match, and the card would be
    titled with the folder name — so both are normalised before parsing.
    """
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    slug = path.parent.name if path.name.startswith("index") else path.stem
    if not m:
        return {"title": path.stem, "categories": [], "tags": [], "images": [],
                "draft": False, "slug": slug}, text, None
    fm = m.group(1)

    def scalar(key):
        mm = re.search(rf"^{key}:\s*[\"']?(.+?)[\"']?\s*$", fm, re.MULTILINE)
        return mm.group(1).strip() if mm else ""

    def arr(key):
        mm = re.search(rf"^{key}:\s*\[(.*?)\]", fm, re.MULTILINE)
        if not mm:
            return []
        return [x.strip().strip("\"'") for x in mm.group(1).split(",") if x.strip()]

    info = {"title": scalar("title"), "categories": arr("categories"), "tags": arr("tags"),
            "images": arr("images"), "draft": scalar("draft").lower() == "true", "slug": slug}
    return info, text, m


def apply_images(path: Path, slug: str, overwrite: bool = False) -> bool:
    """Make frontmatter point at /og/<slug>.jpg. Returns True if the file changed.

    overwrite=False adds the line only when `images:` is missing — an article may
    deliberately use another picture, and the build must not clobber that.
    """
    _, text, m = read_frontmatter(path)
    if m is None:
        return False
    fm = m.group(1)
    want = f'images: ["/og/{slug}.jpg"]'
    cur = re.search(r"^images:.*$", fm, re.MULTILINE)
    if cur:
        if cur.group(0).strip() == want or not overwrite:
            return False
        new_fm = fm[:cur.start()] + want + fm[cur.end():]
    else:
        anchor = (re.search(r"^(tags:.*)$", fm, re.MULTILINE)
                  or re.search(r"^(categories:.*)$", fm, re.MULTILINE))
        new_fm = fm[:anchor.end()] + "\n" + want + fm[anchor.end():] if anchor else fm + "\n" + want
    path.write_text(text[:m.start(1)] + new_fm + text[m.end(1):], encoding="utf-8")
    return True
