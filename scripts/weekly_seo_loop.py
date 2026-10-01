"""Weekly active SEO loop for chinatea.house.

Runs every week to:
1. Fetch latest GSC search analytics data.
2. Identify underperforming pages (high impressions, low CTR).
3. Find top queries and pages gaining traction.
4. Optionally submit the sitemap after a relevant publication change.
5. Optionally notify IndexNow after a relevant publication change.
6. Output an actionable report.

The loop intentionally does NOT rebuild/deploy the site; that should be
triggered by code/data changes via GitHub Actions. This keeps the cron fast
and safe.
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if env_path := os.getenv("GSC_ENV_FILE"):
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError("Install python-dotenv to use GSC_ENV_FILE") from exc
    load_dotenv(env_path)
os.environ.setdefault("GSC_SITE_URL", "sc-domain:chinatea.house")
os.environ.setdefault("GSC_CREDENTIAL_TYPE", "oauth")

from execution.data.db import Database
from execution.monitor.gsc import GoogleSearchConsole
from execution.cli import cli
from execution.monitor.periods import search_window

DB_PATH = Path(os.getenv("TEA_DB_PATH", PROJECT_ROOT / "data/canonical/tea.db"))


def fetch_gsc_data(db: Database) -> None:
    """Fetch last 35 days of GSC data and store snapshots."""
    start, end = search_window(35)

    client = GoogleSearchConsole()

    # Daily totals
    rows = client.fetch_all_search_analytics(start_date=start, end_date=end, dimensions=["date"])
    db.replace_daily_performance_window([r.to_dict() for r in rows], start, end, "site")

    # Page/date totals include traffic omitted from the query breakdown.
    rows = client.fetch_all_search_analytics(start_date=start, end_date=end, dimensions=["date", "page"])
    db.replace_daily_performance_window([r.to_dict() for r in rows], start, end, "page")

    # Page + query detail
    rows = client.fetch_all_search_analytics(
        start_date=start, end_date=end, dimensions=["date", "page", "query"]
    )
    db.replace_daily_performance_window([r.to_dict() for r in rows], start, end, "page_query")

    print(f"[SEO LOOP] Fetched GSC data: {start} to {end}")


def generate_report(db: Database) -> dict:
    """Analyze GSC data and return actionable report."""
    start_30, end = search_window(30)
    start_7, end_7 = search_window(7)
    previous_end = (date.fromisoformat(start_7) - timedelta(days=1)).isoformat()
    previous_start = (date.fromisoformat(start_7) - timedelta(days=7)).isoformat()
    weekly = {
        "target_clicks": 7,
        "period": {"start": start_7, "end": end_7},
        "summary": db.get_performance_summary(start_date=start_7, end_date=end_7, url_only=False),
        "previous_period": {"start": previous_start, "end": previous_end},
        "previous_summary": db.get_performance_summary(start_date=previous_start, end_date=previous_end, url_only=False),
    }

    summary = db.get_performance_summary(start_date=start_30, end_date=end, url_only=False)
    underperforming = db.get_underperforming_pages(
        start_date=start_30,
        end_date=end,
        min_impressions=100,
        max_ctr=0.05,
        limit=20,
    )

    with db.connection() as conn:
        top_queries = conn.execute("""
            SELECT query, SUM(clicks) AS clicks, SUM(impressions) AS impressions,
                   ROUND(CAST(SUM(clicks) AS REAL) / NULLIF(SUM(impressions), 0), 4) AS ctr
            FROM page_performance_snapshots
            WHERE snapshot_date BETWEEN ? AND ?
              AND query != '' AND url != '' AND device = '' AND country = ''
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
              AND url IS NOT NULL AND url != '' AND query = '' AND device = '' AND country = ''
            GROUP BY url
            ORDER BY impressions DESC
            LIMIT 10
        """, (start_30, end)).fetchall()

    return {
        "weekly": weekly,
        "summary": summary,
        "period": {"start": start_30, "end": end},
        "detail_limit": "Query rows omit anonymized queries and may be truncated; never sum them into site totals.",
        "underperforming": [dict(r) for r in underperforming],
        "top_queries": [dict(r) for r in top_queries],
        "top_pages": [dict(r) for r in top_pages],
    }


def print_report(report: dict) -> None:
    weekly = report["weekly"]
    week = weekly["summary"]
    period = weekly["period"]
    print(f"\n[SEO LOOP] Weekly minimum: {weekly['target_clicks']} Google Search clicks; "
          f"{period['start']} to {period['end']} (Pacific dates, three-day reporting lag)")
    if week["available"]:
        print(f"  Stored site totals: {week['total_clicks']} clicks; "
              f"{week['days_with_data']} dates reported, latest {week['latest_date']}.")
        if week["days_with_data"] == 7:
            status = "met" if week["total_clicks"] >= weekly["target_clicks"] else "below minimum"
            print(f"  Weekly target: {status}.")
        else:
            print("  Weekly target: provisional; missing dates may be zero-traffic days or incomplete data.")
        previous = weekly["previous_summary"]
        if previous["available"]:
            print(f"  Previous seven days: {previous['total_clicks']} clicks, "
                  f"{previous['days_with_data']} dates reported.")
    else:
        print("  Weekly result unknown: no stored site/date rows. Fetch Search Console before judging the target.")
    summary = report["summary"]
    if not summary["available"]:
        print("[SEO LOOP] No site/date data in this window. Traffic is unknown; fetch current data before making decisions.")
        return
    print(f"\n[SEO LOOP] Last 30 days: {summary['total_clicks']} clicks, "
          f"{summary['total_impressions']} impressions, "
          f"{summary['avg_ctr']:.2%} CTR; latest stored site date {summary['latest_date']}")

    print("\n[SEO LOOP] Top pages by impressions:")
    for p in report["top_pages"][:5]:
        print(f"  - {p['url']}: {p['clicks']} clicks, {p['impressions']} impr, "
              f"{p['ctr']:.2%} CTR, pos {p['avg_position']}")

    print("\n[SEO LOOP] Diagnostic candidates (at least 100 impressions, low CTR):")
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

    print("\n[SEO LOOP] Suggested actions:")
    print("  1. Inspect index status and matched page/query/country/device evidence before editing.")
    print("  2. For average positions beyond 30, investigate relevance, coverage and credibility first.")
    print("  3. Consider a snippet test only with adequate visibility and a matched query segment.")
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
    import argparse
    parser = argparse.ArgumentParser(description="Fetch and report SEO evidence. Crawler submissions are opt-in.")
    parser.add_argument("--offline", action="store_true", help="Read stored evidence without API calls")
    parser.add_argument("--submit-sitemap", action="store_true")
    parser.add_argument("--ping-indexnow", action="store_true")
    args = parser.parse_args()
    db = Database(DB_PATH)
    print(f"[SEO LOOP] Starting weekly SEO loop at {datetime.now().isoformat()}")

    if not args.offline:
        fetch_gsc_data(db)
    report = generate_report(db)
    print_report(report)
    if args.submit_sitemap:
        submit_sitemap()
    if args.ping_indexnow:
        ping_indexnow()

    print(f"\n[SEO LOOP] Finished at {datetime.now().isoformat()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
