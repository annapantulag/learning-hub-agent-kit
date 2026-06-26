#!/usr/bin/env python3
"""Verify relative href targets in learning-hub.html files exist in the repo."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

HREF_RE = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "javascript:", "data:")
REPO_ROOT = Path(__file__).resolve().parents[2]


def tracked_html_files() -> list[Path]:
    out = subprocess.check_output(
        ["git", "ls-files", "*learning-hub.html"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [REPO_ROOT / line for line in out.splitlines() if line.strip()]


def resolve_href(html_path: Path, href: str) -> Path | None:
    href = unquote(href.strip())
    if not href or href.startswith("#") or href.startswith(SKIP_PREFIXES):
        return None
    path_part = href.split("#", 1)[0].split("?", 1)[0]
    if not path_part:
        return None
    return (html_path.parent / path_part).resolve()


def main() -> int:
    errors: list[str] = []
    html_files = tracked_html_files()
    if not html_files:
        print("No tracked learning-hub.html files found.")
        return 0

    for html in html_files:
        content = html.read_text(encoding="utf-8", errors="replace")
        for href in HREF_RE.findall(content):
            target = resolve_href(html, href)
            if target is None:
                continue
            try:
                target.relative_to(REPO_ROOT.resolve())
            except ValueError:
                errors.append(f"{html.relative_to(REPO_ROOT)}: escapes repo: {href}")
                continue
            if not target.is_file():
                errors.append(
                    f"{html.relative_to(REPO_ROOT)}: missing target for href={href!r} "
                    f"(expected {target.relative_to(REPO_ROOT)})"
                )

    if errors:
        print("Broken relative links in learning-hub.html files:\n")
        for err in errors:
            print(f"  ::error::{err}")
        print(f"\n{len(errors)} broken link(s).")
        return 1

    print(f"Checked {len(html_files)} learning-hub.html file(s); all relative links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
