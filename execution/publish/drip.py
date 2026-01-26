"""
Drip publishing for controlled page rollout.

Controls the pace of publishing to avoid overwhelming search engines
and to allow monitoring of indexing and ranking.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from execution.data.db import Database


class DripPublisher:
    """Manages gradual publishing of pages."""

    # Default drip schedule (pages per day by week)
    DEFAULT_SCHEDULE = {
        1: 100,   # Week 1: 100 pages/day (pillars first)
        2: 200,   # Week 2: 200 pages/day
        3: 200,   # Week 3: 200 pages/day
        4: 200,   # Week 4: 200 pages/day
        5: 400,   # Month 2+: 400 pages/day
        9: 300,   # Month 4+: 300 pages/day (maintenance)
    }

    # Template priority for publishing order
    TEMPLATE_PRIORITY = {
        "pillars/category.html": 1,
        "pillars/region.html": 2,
        "satellites/tea-detail.html": 3,
        "satellites/brewing.html": 4,
        "satellites/occasion.html": 5,
        "satellites/comparison.html": 6,
    }

    def __init__(
        self,
        db: "Database",
        start_date: Optional[datetime] = None,
        schedule: Optional[dict] = None
    ):
        self.db = db
        self.start_date = start_date or datetime.now()
        self.schedule = schedule or self.DEFAULT_SCHEDULE

    def get_daily_limit(self) -> int:
        """Get the page limit for today based on schedule."""
        days_since_start = (datetime.now() - self.start_date).days
        weeks_since_start = days_since_start // 7 + 1

        # Find applicable limit from schedule
        limit = 100  # default
        for week, pages in sorted(self.schedule.items()):
            if weeks_since_start >= week:
                limit = pages

        return limit

    def get_next_batch(self, count: Optional[int] = None) -> list[str]:
        """Get next batch of pages to publish."""
        if count is None:
            count = self.get_daily_limit()

        # Get draft pages
        draft_pages = self.db.get_pages_by_status("draft")

        # Sort by template priority
        sorted_pages = sorted(
            draft_pages,
            key=lambda p: (
                self.TEMPLATE_PRIORITY.get(p.template, 10),
                p.generated_at  # Then by generation time
            )
        )

        return [p.url for p in sorted_pages[:count]]

    def get_all_pending(self) -> list[str]:
        """Get all draft pages (for full publish)."""
        draft_pages = self.db.get_pages_by_status("draft")
        return [p.url for p in draft_pages]

    def publish(self, urls: list[str]) -> dict:
        """Mark pages as published."""
        published_count = 0
        errors = []

        for url in urls:
            try:
                # Get current page info
                draft_pages = self.db.get_pages_by_status("draft")
                page = next((p for p in draft_pages if p.url == url), None)

                if page:
                    from execution.data.models import PageManifest

                    updated = PageManifest(
                        url=page.url,
                        template=page.template,
                        data_hash=page.data_hash,
                        template_hash=page.template_hash,
                        status="published",
                        generated_at=page.generated_at,
                        published_at=datetime.now().isoformat(),
                        word_count=page.word_count,
                        internal_links_count=page.internal_links_count,
                    )
                    self.db.upsert_page_manifest(updated)
                    published_count += 1
                else:
                    errors.append(f"Page not found in drafts: {url}")

            except Exception as e:
                errors.append(f"{url}: {str(e)}")

        return {
            "published": published_count,
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
        }

    def get_publish_stats(self) -> dict:
        """Get publishing statistics."""
        draft_pages = self.db.get_pages_by_status("draft")
        published_pages = self.db.get_pages_by_status("published")

        # Group by template
        draft_by_template = {}
        for page in draft_pages:
            template = page.template
            if template not in draft_by_template:
                draft_by_template[template] = 0
            draft_by_template[template] += 1

        published_by_template = {}
        for page in published_pages:
            template = page.template
            if template not in published_by_template:
                published_by_template[template] = 0
            published_by_template[template] += 1

        # Calculate progress
        total = len(draft_pages) + len(published_pages)
        progress = len(published_pages) / total if total > 0 else 0

        # Estimate completion
        daily_limit = self.get_daily_limit()
        days_remaining = len(draft_pages) // daily_limit if daily_limit > 0 else 0
        est_completion = datetime.now() + timedelta(days=days_remaining)

        return {
            "total_pages": total,
            "draft": len(draft_pages),
            "published": len(published_pages),
            "progress_percent": round(progress * 100, 1),
            "draft_by_template": draft_by_template,
            "published_by_template": published_by_template,
            "daily_limit": daily_limit,
            "days_remaining": days_remaining,
            "estimated_completion": est_completion.isoformat(),
        }

    def get_recently_published(self, limit: int = 50) -> list[dict]:
        """Get recently published pages for monitoring."""
        published_pages = self.db.get_pages_by_status("published")

        # Sort by published date (most recent first)
        sorted_pages = sorted(
            published_pages,
            key=lambda p: p.published_at or "",
            reverse=True
        )

        return [
            {
                "url": p.url,
                "template": p.template,
                "published_at": p.published_at,
                "word_count": p.word_count,
            }
            for p in sorted_pages[:limit]
        ]
