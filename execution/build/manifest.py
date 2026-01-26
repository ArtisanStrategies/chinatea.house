"""
Page manifest management for incremental builds.

Tracks page generation state to enable efficient rebuilds when only
data or templates have changed.
"""

import json
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import xxhash

if TYPE_CHECKING:
    from execution.data.db import Database
    from execution.data.models import PageManifest


class PageManifestManager:
    """Manages page build state for incremental builds."""

    def __init__(self, db: "Database"):
        self.db = db

    def compute_data_hash(self, data: dict) -> str:
        """Compute hash of page data for change detection."""
        # Serialize to JSON with sorted keys for deterministic hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return xxhash.xxh64(json_str).hexdigest()

    def is_page_stale(
        self,
        url: str,
        data_hash: str,
        template_hash: str
    ) -> bool:
        """Check if a page needs regeneration."""
        # Query existing manifest entry
        pages = self.db.get_pages_by_status("draft")
        pages.extend(self.db.get_pages_by_status("published"))

        for page in pages:
            if page.url == url:
                # Page exists, check if hashes match
                return (
                    page.data_hash != data_hash or
                    page.template_hash != template_hash
                )

        # Page doesn't exist, needs generation
        return True

    def update_manifest(
        self,
        url: str,
        template: str,
        data_hash: str,
        template_hash: str,
        word_count: int = 0,
        internal_links_count: int = 0,
        status: str = "draft"
    ) -> None:
        """Update or create manifest entry for a page."""
        from execution.data.models import PageManifest

        manifest = PageManifest(
            url=url,
            template=template,
            data_hash=data_hash,
            template_hash=template_hash,
            status=status,
            generated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat() if status == "published" else None,
            word_count=word_count,
            internal_links_count=internal_links_count,
        )

        self.db.upsert_page_manifest(manifest)

    def get_pages_to_rebuild(
        self,
        data_hashes: dict[str, str],
        template_hashes: dict[str, str]
    ) -> list[str]:
        """Get list of page URLs that need rebuilding."""
        stale_urls = []

        # Check all known pages
        for status in ["draft", "published"]:
            pages = self.db.get_pages_by_status(status)
            for page in pages:
                current_data_hash = data_hashes.get(page.url)
                current_template_hash = template_hashes.get(page.template)

                if (current_data_hash is None or
                    current_data_hash != page.data_hash or
                    current_template_hash != page.template_hash):
                    stale_urls.append(page.url)

        return stale_urls

    def get_new_pages(
        self,
        all_page_urls: set[str]
    ) -> list[str]:
        """Get list of new pages that don't exist in manifest."""
        existing_urls = set()

        for status in ["draft", "published", "archived"]:
            pages = self.db.get_pages_by_status(status)
            existing_urls.update(p.url for p in pages)

        return list(all_page_urls - existing_urls)

    def mark_published(self, urls: list[str]) -> None:
        """Mark pages as published."""
        for status in ["draft"]:
            pages = self.db.get_pages_by_status(status)
            for page in pages:
                if page.url in urls:
                    self.update_manifest(
                        url=page.url,
                        template=page.template,
                        data_hash=page.data_hash,
                        template_hash=page.template_hash,
                        word_count=page.word_count,
                        internal_links_count=page.internal_links_count,
                        status="published"
                    )

    def get_publish_queue(self, limit: int = 100) -> list[str]:
        """Get next batch of pages ready for publishing."""
        draft_pages = self.db.get_pages_by_status("draft")
        # Sort by template priority (pillars first, then satellites)
        template_priority = {
            "pillars/category.html": 1,
            "pillars/region.html": 2,
            "satellites/tea-detail.html": 3,
            "satellites/comparison.html": 4,
            "satellites/brewing.html": 5,
            "satellites/occasion.html": 6,
        }

        sorted_pages = sorted(
            draft_pages,
            key=lambda p: template_priority.get(p.template, 10)
        )

        return [p.url for p in sorted_pages[:limit]]

    def get_stats(self) -> dict:
        """Get manifest statistics."""
        stats = {
            "draft": 0,
            "published": 0,
            "archived": 0,
            "total_words": 0,
            "by_template": {},
        }

        for status in ["draft", "published", "archived"]:
            pages = self.db.get_pages_by_status(status)
            stats[status] = len(pages)
            stats["total_words"] += sum(p.word_count for p in pages)

            for page in pages:
                if page.template not in stats["by_template"]:
                    stats["by_template"][page.template] = 0
                stats["by_template"][page.template] += 1

        return stats


def count_words(html: str) -> int:
    """Count words in HTML content (rough estimate)."""
    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Count words
    return len(text.split())


def count_internal_links(html: str) -> int:
    """Count internal links in HTML content."""
    import re
    # Count href attributes pointing to relative URLs
    internal_pattern = r'href=["\'](?!https?://|//|mailto:|tel:)[^"\']*["\']'
    return len(re.findall(internal_pattern, html))
