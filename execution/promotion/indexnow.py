"""IndexNow submission helper for chinatea.house.

IndexNow notifies search engines (Bing, Yandex, etc.) that pages have been
updated so they can recrawl them. No account is required; only a key file
hosted on the domain and a POST to the IndexNow endpoint.
"""

import argparse
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

INDEXNOW_KEY = "chinateahouse2026"
KEY_FILE_NAME = f"indexnow-{INDEXNOW_KEY}.txt"
ENDPOINTS = [
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
    "https://api.indexnow.org/indexnow",
]


def create_key_file(output_dir: str) -> list[Path]:
    """Write the IndexNow key file(s) to the site output directory."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    # Named-key file (spec-compliant)
    named_path = out / KEY_FILE_NAME
    named_path.write_text(INDEXNOW_KEY + "\n", encoding="utf-8")
    paths.append(named_path)
    # Generic indexnow.txt for search engines that prefer it
    generic_path = out / "indexnow.txt"
    generic_path.write_text(INDEXNOW_KEY + "\n", encoding="utf-8")
    paths.append(generic_path)
    return paths


def _resolve_sub_sitemap_path(sitemap_url: str, base_dir: Path) -> str | None:
    """Map an absolute sitemap URL to a local file if it exists."""
    from urllib.parse import urlparse

    parsed = urlparse(sitemap_url)
    local_candidate = base_dir / Path(parsed.path).name
    if local_candidate.is_file():
        return str(local_candidate)
    return None


def _urls_from_sitemap(sitemap_path: str) -> list[str]:
    """Recursively extract URLs from a sitemap or sitemap index."""
    sitemap_path_obj = Path(sitemap_path)
    base_dir = sitemap_path_obj.parent

    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    urls = []
    if root.tag.endswith("sitemapindex"):
        for loc in root.findall(".//sm:loc", ns):
            sub_url = loc.text
            if not sub_url:
                continue
            local_path = _resolve_sub_sitemap_path(sub_url, base_dir)
            if local_path:
                urls.extend(_urls_from_sitemap(local_path))
                continue
            # Fall back to downloading sub-sitemap.
            import tempfile

            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb", delete=False, suffix=".xml"
                ) as tmp:
                    urllib.request.urlretrieve(sub_url, tmp.name)
                    tmp_path = tmp.name
                urls.extend(_urls_from_sitemap(tmp_path))
            except Exception as e:
                print(f"Warning: could not fetch sub-sitemap {sub_url}: {e}")
            finally:
                if tmp_path:
                    os.unlink(tmp_path)
    else:
        for loc in root.findall(".//sm:loc", ns):
            if loc.text:
                urls.append(loc.text)
    return urls


def submit_urls(urls: list[str], key: str = INDEXNOW_KEY) -> dict:
    """Submit a list of URLs to IndexNow endpoints."""
    if not urls:
        return {"submitted": 0, "results": []}

    # IndexNow accepts up to 10,000 URLs per request.
    BATCH_SIZE = 10_000
    results = []

    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        host = None
        for url in batch:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            host = parsed.netloc
            break

        if not host:
            continue

        payload = {
            "host": host,
            "key": key,
            "urlList": batch,
        }
        data = (
            "{"
            + f'"host": "{host}", "key": "{key}", "urlList": {batch}'
            + "}"
        ).encode("utf-8")
        # Build JSON manually to avoid importing json when not needed; but
        # we'll just use urllib with json.
        import json

        data = json.dumps(payload).encode("utf-8")

        for endpoint in ENDPOINTS:
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    status = resp.getcode()
                    body = resp.read().decode("utf-8", errors="ignore")[:200]
            except urllib.error.HTTPError as e:
                status = e.code
                body = e.read().decode("utf-8", errors="ignore")[:200]
            except Exception as e:
                status = 0
                body = str(e)
            results.append(
                {
                    "endpoint": endpoint,
                    "batch": f"{i + 1}-{min(i + BATCH_SIZE, len(urls))}",
                    "status": status,
                    "body": body,
                }
            )

    return {"submitted": len(urls), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="IndexNow submission helper")
    parser.add_argument(
        "--create-key",
        metavar="OUTPUT_DIR",
        help="Create the IndexNow key file in OUTPUT_DIR",
    )
    parser.add_argument(
        "--submit",
        metavar="SITEMAP_PATH",
        help="Submit all URLs in SITEMAP_PATH to IndexNow endpoints",
    )
    args = parser.parse_args()

    if args.create_key:
        key_path = create_key_file(args.create_key)
        print(f"Created {key_path}")
        return 0

    if args.submit:
        urls = _urls_from_sitemap(args.submit)
        print(f"Found {len(urls)} URLs in sitemap")
        result = submit_urls(urls)
        print(f"Submitted {result['submitted']} URLs")
        for r in result["results"]:
            print(f"{r['endpoint']} {r['batch']}: {r['status']} {r['body']}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
