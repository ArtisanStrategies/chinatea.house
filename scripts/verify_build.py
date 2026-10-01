#!/usr/bin/env python3
"""Verify the generated site's deploy-time contract."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []
        self.json_ld: list[str] = []
        self._in_json_ld = False
        self._json_parts: list[str] = []
        self.h1_count = 0
        self.title_parts: list[str] = []
        self._in_title = False
        self.canonicals: list[str] = []
        self.descriptions: list[str] = []
        self.noindex = False
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self._in_title = True
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonicals.append(attributes.get("href", ""))
        if tag == "meta" and attributes.get("name") == "description":
            self.descriptions.append(attributes.get("content", ""))
        if tag == "meta" and attributes.get("name") == "robots":
            self.noindex = "noindex" in attributes.get("content", "").lower()
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.references.append(value)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._json_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
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
    documents: dict[Path, DocumentParser] = {}
    titles: dict[str, Path] = {}
    for html_path in output.rglob("*.html"):
        parser = DocumentParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        documents[html_path] = parser
        relative = html_path.relative_to(output)
        route = "/" + str(relative).removesuffix("index.html")
        expected = "https://chinatea.house" + route
        if relative == Path("404.html"):
            if not parser.noindex:
                errors.append("404 must be noindexed")
        elif parser.canonicals != [expected]:
            errors.append(f"canonical mismatch: {relative}: {parser.canonicals}")
        if parser.h1_count != 1:
            errors.append(f"expected one h1: {relative}: {parser.h1_count}")
        if len(parser.descriptions) != 1 or not parser.descriptions[0].strip() or "<" in parser.descriptions[0]:
            errors.append(f"missing or malformed description: {relative}")
        title = "".join(parser.title_parts).strip()
        if not title:
            errors.append(f"empty title: {relative}")
        elif not parser.noindex and title in titles:
            errors.append(f"duplicate title: {relative} and {titles[title]}")
        elif not parser.noindex:
            titles[title] = relative
        for index, payload in enumerate(parser.json_ld, 1):
            if not payload:
                errors.append(f"empty JSON-LD: {html_path.relative_to(output)} block {index}")
                continue
            try:
                schema = json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON-LD: {html_path.relative_to(output)} block {index}: {exc}")
                continue
            def unsupported(value):
                if isinstance(value, list):
                    return any(unsupported(item) for item in value)
                if isinstance(value, dict):
                    types = value.get("@type", [])
                    types = [types] if isinstance(types, str) else types
                    return bool(set(types) & {"Product", "AggregateRating", "Review", "Offer"}) or any(unsupported(item) for item in value.values())
                return False
            if html_path.match("*/tea/*/index.html") and unsupported(schema):
                errors.append(f"unsupported commercial schema: {html_path.relative_to(output)}")

        for reference in parser.references:
            target = reference_path(output, reference)
            if target is not None and not target.exists():
                broken.setdefault(reference, []).append(str(html_path.relative_to(output)))

    for reference, sources in sorted(broken.items()):
        sample = ", ".join(sources[:3])
        errors.append(f"broken internal reference {reference!r} from {sample}")
    for html_path, parser in documents.items():
        for reference in parser.references:
            split = urlsplit(reference)
            if split.fragment and not split.scheme and not split.netloc:
                target = html_path if not split.path else reference_path(output, reference)
                if target in documents and unquote(split.fragment) not in documents[target].ids:
                    errors.append(f"missing anchor {reference!r} from {html_path.relative_to(output)}")
    for sitemap in output.glob("sitemap-*.xml"):
        for loc in ElementTree.parse(sitemap).iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            url = loc.text or ""
            if not url.startswith("https://chinatea.house/"):
                errors.append(f"noncanonical sitemap URL: {url}")
                continue
            target = reference_path(output, urlsplit(url).path)
            if target not in documents or documents[target].noindex:
                errors.append(f"sitemap URL missing or noindexed: {url}")
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
