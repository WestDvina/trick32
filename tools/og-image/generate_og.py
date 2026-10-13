#!/usr/bin/env python3
"""Draw the OG cards that are missing for trick32 articles, then verify the rest.

CI entry point: runs before the Hugo build. Never touches cards that already
exist unless --force is given, so the committed cards stay as they are.

Exit code 1 if a card could not be drawn, or if a non-draft article is left
without any card (hard guard: the OG tag must not point at a 404).

Usage:
  generate_og.py                                  # fill gaps in static/og
  generate_og.py --check-only                     # verify only
  generate_og.py --only some-slug --force         # redraw one card
"""
import argparse
import sys
from pathlib import Path

import render_og
from articles import load_hooks, read_frontmatter

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_STATIC = REPO_ROOT / "static"
CONTENT_DIR = REPO_ROOT / "content" / "articles"


def collect(content_dir: Path, only: list):
    files = sorted(p for p in content_dir.rglob("*.md") if p.name != "_index.md")
    out = []
    for path in files:
        info, _, _ = read_frontmatter(path)
        if only and info["slug"] not in only:
            continue
        out.append(info)
    return out


def draw(info, hook):
    if hook:
        return render_og.render(hook.get("hook", info["title"]), info["slug"], "auto",
                                hook.get("accent", ""), ",".join(info["categories"]), "",
                                ",".join(info["tags"]))
    return render_og.render(info["title"], info["slug"], "auto", "",
                            ",".join(info["categories"]), "", ",".join(info["tags"]),
                            from_title=True)


def has_card(info, out_dir: Path) -> bool:
    if (out_dir / f"{info['slug']}.jpg").exists():
        return True
    return any((SITE_STATIC / ref.lstrip("/")).exists() for ref in info["images"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles-dir", default=str(CONTENT_DIR))
    ap.add_argument("--out-dir", default=str(SITE_STATIC / "og"))
    ap.add_argument("--only", default="", help="comma-separated slugs")
    ap.add_argument("--force", action="store_true", help="redraw even if the card exists")
    ap.add_argument("--max", type=int, default=0, help="stop after N drawn cards")
    ap.add_argument("--check-only", action="store_true", help="verify, do not draw")
    args = ap.parse_args()

    content_dir = Path(args.articles_dir).expanduser()
    out_dir = Path(args.out_dir).expanduser()
    only = [s.strip() for s in args.only.split(",") if s.strip()]
    hooks = load_hooks()
    items = collect(content_dir, only)

    drawn, skipped, failed = [], [], []
    if not args.check_only:
        out_dir.mkdir(parents=True, exist_ok=True)
        for info in items:
            dst = out_dir / f"{info['slug']}.jpg"
            if dst.exists() and not args.force:
                skipped.append(info["slug"])
                continue
            try:
                render_og.save(draw(info, hooks.get(info["slug"])), dst)
                drawn.append(info["slug"])
            except Exception as e:  # noqa: BLE001
                failed.append(f"{info['slug']}: {e}")
            if args.max and len(drawn) >= args.max:
                break

    missing = [i["slug"] for i in items if not i["draft"] and not has_card(i, out_dir)]

    print(f"articles: {len(items)} | drawn: {len(drawn)} | already there: {len(skipped)} "
          f"| cards: {out_dir}")
    if drawn:
        print("drawn: " + ", ".join(drawn))
    if failed:
        print("DRAW FAILED:\n  " + "\n  ".join(failed))
    if missing:
        print("NO CARD (non-draft article without an OG image):\n  " + "\n  ".join(missing))
    return 1 if (failed or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
