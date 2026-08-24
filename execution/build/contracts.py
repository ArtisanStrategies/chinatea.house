"""Stable build contracts shared by generators, templates, and tests."""

from __future__ import annotations

import json
from typing import Any

import xxhash


def hash_text(value: str) -> str:
    """Return a stable xxHash digest for Unicode text.

    xxhash 4 requires bytes for one-shot hashing. Keeping the conversion here
    prevents dependency behavior from leaking into the build pipeline.
    """
    return xxhash.xxh64(value.encode("utf-8")).hexdigest()


def hash_data(value: Any) -> str:
    """Serialize structured data deterministically and hash it."""
    serialized = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    return hash_text(serialized)


def comparison_url(tea_a_id: str, tea_b_id: str) -> str:
    """Return the one canonical URL for a tea pair."""
    tea_a_id, tea_b_id = sorted((tea_a_id, tea_b_id))
    return f"/compare/{tea_a_id}-vs-{tea_b_id}/"
