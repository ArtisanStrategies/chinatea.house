#!/usr/bin/env python3
"""Verify the generated site's deploy-time contract."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []
        self.json_ld: list[str] = []
        self._in_json_ld = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.references.append(value)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_parts).strip())
            self._in_json_ld = False


def reference_path(output: Path, reference: str) -> Path | None:
    split = urlsplit(reference)
    if split.scheme or split.netloc or reference.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    path = unquote(split.path)
    if not path or path == "/":
        return output / "index.html"
    candidate = output / path.lstrip("/")
    return candidate / "index.html" if path.endswith("/") else candidate


def verify(output: Path) -> list[str]:
    errors: list[str] = []
    required = (
        "index.html", "404.html", "robots.txt", "sitemap.xml", "favicon.svg",
        "_headers", "_redirects", "brewing/index.html", "best-tea-for/index.html",
    )
    for relative in required:
        if not (output / relative).is_file():
            errors.append(f"missing required deploy file: /{relative}")

    comparison_pages = list((output / "compare").glob("*/index.html"))
    if len(comparison_pages) > 8:
        errors.append(f"comparison publication exceeds policy: {len(comparison_pages)} pages")

    broken: dict[str, list[str]] = {}
    for html_path in output.rglob("*.html"):
        parser = DocumentParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for index, payload in enumerate(parser.json_ld, 1):
            if not payload:
                errors.append(f"empty JSON-LD: {html_path.relative_to(output)} block {index}")
                continue
            try:
                schema = json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON-LD: {html_path.relative_to(output)} block {index}: {exc}")
                continue
            if html_path.match("*/tea/*/index.html") and schema.get("@type") in {
                "Product", "AggregateRating", "Review"
            }:
                errors.append(f"unsupported commercial schema: {html_path.relative_to(output)}")

        for reference in parser.references:
            target = reference_path(output, reference)
            if target is not None and not target.exists():
                broken.setdefault(reference, []).append(str(html_path.relative_to(output)))

    for reference, sources in sorted(broken.items()):
        sample = ", ".join(sources[:3])
        errors.append(f"broken internal reference {reference!r} from {sample}")
    return errors


def main() -> int:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "output").resolve()
    errors = verify(output)
    if errors:
        print(f"Generated-site verification failed with {len(errors)} error(s):")
        for error in errors[:100]:
            print(f"- {error}")
        return 1
    html_count = sum(1 for _ in output.rglob("*.html"))
    print(f"Generated-site contract passed for {html_count} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
