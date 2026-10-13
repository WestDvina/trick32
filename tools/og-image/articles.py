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
    """Return (info, text, frontmatter_match). info: title/categories/tags/draft/images/slug."""
    text = path.read_text(encoding="utf-8")
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
