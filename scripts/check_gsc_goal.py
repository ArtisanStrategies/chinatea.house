"""Fetch GSC data and report if we hit 100 clicks/month."""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load agswebsite .env
from dotenv import load_dotenv
load_dotenv("/Users/josephw/MoneyGenerating/agswebsite/scripts/search-console/.env")
os.environ["GSC_SITE_URL"] = "sc-domain:chinatea.house"
os.environ["GSC_CREDENTIAL_TYPE"] = "oauth"

from execution.data.db import Database
from execution.monitor.gsc import GoogleSearchConsole

DB_PATH = Path("/Users/josephw/MoneyGenerating/chinateahouse/data/canonical/tea.db")


def main():
    db = Database(DB_PATH)
    end = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=33)).strftime("%Y-%m-%d")

    client = GoogleSearchConsole()
    rows = client.fetch_all_search_analytics(start_date=start, end_date=end, dimensions=["date"])
    snapshots = [row.to_dict() for row in rows]
    db.insert_performance_snapshots(snapshots, default_snapshot_date=end)

    summary = db.get_performance_summary(start_date=start, end_date=end)
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
