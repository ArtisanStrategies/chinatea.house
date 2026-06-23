"""
IndexNow integration for fast search-engine indexing.

IndexNow is supported by Bing, Yandex, and others. It lets you notify search
engines immediately when URLs are added, updated, or removed.

To use it:
1. Generate a 32-character hex API key (e.g., uuid.uuid4().hex).
2. Expose the key at https://<host>/<key>.txt (no extension).
3. Submit URLs via the IndexNow endpoint.
"""

from __future__ import annotations

import os
import random
import string
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests


DEFAULT_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]


def generate_key() -> str:
    """Generate a 32-character hex IndexNow API key."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=32))


def get_key() -> Optional[str]:
    """Get the configured IndexNow API key."""
    key = os.getenv("INDEXNOW_KEY")
    if key:
        return key
    key_file = Path("config/indexnow.key")
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    return None


def write_key_file(key: str, output_dir: Path) -> Path:
    """Write the verification file at <output_dir>/<key>.txt"""
    path = output_dir / f"{key}.txt"
    path.write_text(key, encoding="utf-8")
    return path


def ping(
    urls: list[str],
    key: Optional[str] = None,
    host: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> dict:
    """Ping IndexNow endpoints with a list of URLs.

    If host is provided, the verification file is assumed to be available at
    https://<host>/<key>.txt. If no host is provided, only the URL list is
    submitted and search engines will attempt to discover the key file.
    """
    key = key or get_key()
    if not key:
        raise ValueError(
            "IndexNow key is required. Set INDEXNOW_KEY env var, create "
            "config/indexnow.key, or pass key explicitly."
        )

    if not urls:
        return {"success": False, "error": "No URLs provided"}

    endpoints = [endpoint] if endpoint else DEFAULT_ENDPOINTS
    payload = {
        "host": host or urls[0].split("/")[2],
        "key": key,
        "urlList": urls,
        "keyLocation": f"https://{host or urls[0].split('/')[2]}/{key}.txt" if host else None,
    }
    if not payload["keyLocation"]:
        del payload["keyLocation"]

    results = []
    for ep in endpoints:
        try:
            response = requests.post(
                ep,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30,
            )
            results.append({
                "endpoint": ep,
                "status_code": response.status_code,
                "ok": response.ok,
                "response": response.text[:500],
            })
        except Exception as exc:
            results.append({
                "endpoint": ep,
                "status_code": None,
                "ok": False,
                "response": str(exc),
            })

    return {
        "success": any(r["ok"] for r in results),
        "key": key,
        "urls_submitted": len(urls),
        "results": results,
    }


def ping_single(
    url: str,
    key: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> dict:
    """Ping IndexNow for a single URL."""
    key = key or get_key()
    if not key:
        raise ValueError("IndexNow key is required.")

    endpoints = [endpoint] if endpoint else DEFAULT_ENDPOINTS
    results = []
    host = url.split("/")[2]
    for ep in endpoints:
        try:
            full_url = f"{ep}?url={url}&key={key}"
            response = requests.get(full_url, timeout=30)
            results.append({
                "endpoint": ep,
                "status_code": response.status_code,
                "ok": response.ok,
                "response": response.text[:500],
            })
        except Exception as exc:
            results.append({
                "endpoint": ep,
                "status_code": None,
                "ok": False,
                "response": str(exc),
            })

    return {
        "success": any(r["ok"] for r in results),
        "key": key,
        "url": url,
        "results": results,
    }
