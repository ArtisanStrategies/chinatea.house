"""Fetch GSC data and report if we hit 100 clicks/month."""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
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
from execution.monitor.periods import search_window

DB_PATH = Path(os.getenv("TEA_DB_PATH", PROJECT_ROOT / "data/canonical/tea.db"))


def main():
    db = Database(DB_PATH)
    start, end = search_window(30)

    client = GoogleSearchConsole()
    rows = client.fetch_all_search_analytics(start_date=start, end_date=end, dimensions=["date"])
    snapshots = [row.to_dict() for row in rows]
    db.replace_daily_performance_window(snapshots, start, end, "site")

    summary = db.get_performance_summary(start_date=start, end_date=end, url_only=False)
    clicks = summary["total_clicks"]
    impressions = summary["total_impressions"]
    ctr = summary["avg_ctr"]

    print(f"[GSC GOAL] Last 30 days: {clicks} clicks, {impressions} impressions, {ctr:.2%} CTR")

    if clicks >= 100:
        print(f"[GSC GOAL] TARGET REACHED: {clicks} clicks in the last 30 days!")
        sys.exit(0)
    else:
        print(f"[GSC GOAL] Need {100 - clicks} more clicks to reach 100/month.")
        sys.exit(1)


if __name__ == "__main__":
    main()
