"""Weekly active SEO loop for chinatea.house.

Runs every week to:
1. Fetch latest GSC search analytics data.
2. Identify underperforming pages (high impressions, low CTR).
3. Find top queries and pages gaining traction.
4. Submit sitemap to Google Search Console.
5. Ping IndexNow to nudge crawlers.
6. Output an actionable report.

The loop intentionally does NOT rebuild/deploy the site; that should be
triggered by code/data changes via GitHub Actions. This keeps the cron fast
and safe.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv("/Users/josephw/MoneyGenerating/agswebsite/scripts/search-console/.env")
os.environ["GSC_SITE_URL"] = "sc-domain:chinatea.house"
os.environ["GSC_CREDENTIAL_TYPE"] = "oauth"

from execution.data.db import Database
from execution.monitor.gsc import GoogleSearchConsole
from execution.cli import cli

DB_PATH = Path("/Users/josephw/MoneyGenerating/chinateahouse/data/canonical/tea.db")


def fetch_gsc_data(db: Database) -> None:
    """Fetch last 35 days of GSC data and store snapshots."""
    end = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=38)).strftime("%Y-%m-%d")

    client = GoogleSearchConsole()

    # Daily totals
    rows = client.fetch_all_search_analytics(start_date=start, end_date=end, dimensions=["date"])
    db.insert_performance_snapshots([r.to_dict() for r in rows], default_snapshot_date=end)

    # Page + query detail
    rows = client.fetch_all_search_analytics(
        start_date=start, end_date=end, dimensions=["page", "query"]
    )
    db.insert_performance_snapshots([r.to_dict() for r in rows], default_snapshot_date=end)

    print(f"[SEO LOOP] Fetched GSC data: {start} to {end}")


def generate_report(db: Database) -> dict:
    """Analyze GSC data and return actionable report."""
    end = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    start_30 = (datetime.now() - timedelta(days=33)).strftime("%Y-%m-%d")

    summary = db.get_performance_summary(start_date=start_30, end_date=end)
    underperforming = db.get_underperforming_pages(
        start_date=start_30,
        end_date=end,
        min_impressions=10,
        max_ctr=0.05,
        limit=20,
    )

    with db.connection() as conn:
        top_queries = conn.execute("""
            SELECT query, SUM(clicks) AS clicks, SUM(impressions) AS impressions,
                   ROUND(CAST(SUM(clicks) AS REAL) / NULLIF(SUM(impressions), 0), 4) AS ctr
            FROM page_performance_snapshots
            WHERE snapshot_date BETWEEN ? AND ?
              AND query IS NOT NULL
            GROUP BY query
            ORDER BY impressions DESC
            LIMIT 20
        """, (start_30, end)).fetchall()

        top_pages = conn.execute("""
            SELECT url, SUM(clicks) AS clicks, SUM(impressions) AS impressions,
                   ROUND(CAST(SUM(clicks) AS REAL) / NULLIF(SUM(impressions), 0), 4) AS ctr,
                   ROUND(SUM(avg_position * impressions) / NULLIF(SUM(impressions), 0), 2) AS avg_position
            FROM page_performance_snapshots
            WHERE snapshot_date BETWEEN ? AND ?
              AND url IS NOT NULL AND url != ''
            GROUP BY url
            ORDER BY impressions DESC
            LIMIT 10
        """, (start_30, end)).fetchall()

    return {
        "summary": summary,
        "underperforming": [dict(r) for r in underperforming],
        "top_queries": [dict(r) for r in top_queries],
        "top_pages": [dict(r) for r in top_pages],
    }


def print_report(report: dict) -> None:
    summary = report["summary"]
    print(f"\n[SEO LOOP] Last 30 days: {summary['total_clicks']} clicks, "
          f"{summary['total_impressions']} impressions, "
          f"{summary['avg_ctr']:.2%} CTR across {summary['url_count']} URLs")

    print("\n[SEO LOOP] Top pages by impressions:")
    for p in report["top_pages"][:5]:
        print(f"  - {p['url']}: {p['clicks']} clicks, {p['impressions']} impr, "
              f"{p['ctr']:.2%} CTR, pos {p['avg_position']}")

    print("\n[SEO LOOP] CTR rewrite candidates (high impressions, low CTR):")
    if report["underperforming"]:
        for p in report["underperforming"][:10]:
            print(f"  - {p['url']}: {p['clicks']} clicks, {p['impressions']} impr, "
                  f"{p['ctr']:.2%} CTR, pos {p['avg_position']}")
    else:
        print("  None found.")

    print("\n[SEO LOOP] Top queries by impressions:")
    for q in report["top_queries"][:10]:
        print(f"  - '{q['query']}': {q['clicks']} clicks, {q['impressions']} impr, "
              f"{q['ctr']:.2%} CTR")

    clicks_needed = max(0, 100 - summary["total_clicks"])
    print(f"\n[SEO LOOP] Need {clicks_needed} more clicks to reach 100/month.")
    print("\n[SEO LOOP] Suggested actions:")
    print("  1. Review CTR rewrite candidates and improve their titles/meta descriptions.")
    print("  2. Add more content targeting top queries with 0 clicks.")
    print("  3. Build more comparison pages around teas related to rising queries.")
    print("  4. Ensure new pages are linked from the homepage and category pages.")


def submit_sitemap() -> None:
    print("\n[SEO LOOP] Submitting sitemap to GSC...")
    cli(["gsc", "submit-sitemap", "--sitemap-url", "https://chinatea.house/sitemap.xml"])


def ping_indexnow() -> None:
    print("\n[SEO LOOP] Pinging IndexNow with homepage and key pages...")
    from execution.monitor.indexnow import ping_single
    key_pages = [
        "https://chinatea.house/",
        "https://chinatea.house/sitemap.xml",
        "https://chinatea.house/category/green/",
        "https://chinatea.house/category/oolong/",
        "https://chinatea.house/category/black/",
        "https://chinatea.house/category/puerh/",
    ]
    for url in key_pages:
        try:
            result = ping_single(url)
            print(f"  {url}: {'OK' if result['success'] else 'FAIL'}")
        except Exception as e:
            print(f"  {url}: ERROR {e}")


def main() -> int:
    db = Database(DB_PATH)
    print(f"[SEO LOOP] Starting weekly SEO loop at {datetime.now().isoformat()}")

    fetch_gsc_data(db)
    report = generate_report(db)
    print_report(report)
    submit_sitemap()
    ping_indexnow()

    print(f"\n[SEO LOOP] Finished at {datetime.now().isoformat()}")

    if report["summary"]["total_clicks"] >= 100:
        print("[SEO LOOP] GOAL REACHED: 100+ clicks in the last 30 days!")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
