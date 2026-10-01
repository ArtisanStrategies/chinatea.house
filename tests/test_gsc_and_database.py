from execution.data.db import Database
from execution.monitor.gsc import GSCConfig, GoogleSearchConsole


def test_snapshot_aggregate_dimensions_are_idempotent(tmp_path):
    db = Database(tmp_path / "tea.db")
    for clicks in (1, 2):
        db.insert_performance_snapshot(
            url="https://chinatea.house/",
            snapshot_date="2026-08-20",
            clicks=clicks,
            impressions=10,
        )
    rows = db.get_performance_for_url("https://chinatea.house/")
    assert len(rows) == 1
    assert rows[0]["clicks"] == 2
    assert rows[0]["query"] == ""


def test_url_inspection_uses_searchconsole_service():
    class Request:
        def execute(self):
            return {"inspectionResult": {"indexStatusResult": {"verdict": "PASS"}}}

    class Index:
        def inspect(self, body):
            assert body["inspectionUrl"] == "https://chinatea.house/"
            return Request()

    class Inspection:
        def index(self):
            return Index()

    class Service:
        def urlInspection(self):
            return Inspection()

    client = GoogleSearchConsole(GSCConfig())
    client._inspection_service = Service()
    result = client.inspect_url("https://chinatea.house/")
    assert result["success"] is True


def test_site_and_page_totals_never_sum_query_or_device_breakdowns(tmp_path):
    db = Database(tmp_path / 'tea.db')
    for url, query, device, clicks, impressions in [
        ('', '', '', 7, 100),
        ('https://chinatea.house/', '', '', 5, 60),
        ('https://chinatea.house/', 'tea', '', 2, 20),
        ('https://chinatea.house/', '', 'MOBILE', 3, 30),
        ('', 'tea', '', 2, 20),
    ]:
        db.insert_performance_snapshot(url=url, query=query, device=device,
            snapshot_date='2026-09-28', clicks=clicks, impressions=impressions)
    site = db.get_performance_summary(url_only=False)
    page = db.get_performance_summary()
    assert (site['total_clicks'], site['total_impressions']) == (7, 100)
    assert (page['total_clicks'], page['total_impressions']) == (5, 60)
    assert site['available'] and site['latest_date'] == '2026-09-28'
    assert not db.get_performance_summary(start_date='2026-10-01', url_only=False)['available']
    candidates = db.get_underperforming_pages(min_impressions=1, max_ctr=1)
    assert len(candidates) == 1 and candidates[0]['impressions'] == 60


def test_search_window_has_exact_inclusive_length_and_pacific_boundary():
    from datetime import datetime, timezone, date
    from execution.monitor.periods import search_window
    start, end = search_window(30, datetime(2026, 10, 1, 1, tzinfo=timezone.utc))
    assert end == '2026-09-27'  # still September 30 in Pacific time
    assert (date.fromisoformat(end) - date.fromisoformat(start)).days + 1 == 30


def test_weekly_fetch_keeps_date_in_every_stored_grain(tmp_path, monkeypatch):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('weekly_seo_test', Path(__file__).parents[1] / 'scripts/weekly_seo_loop.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    requests = []
    class Client:
        def fetch_all_search_analytics(self, **kwargs):
            requests.append(kwargs)
            return []
    monkeypatch.setattr(module, 'GoogleSearchConsole', Client)
    module.fetch_gsc_data(Database(tmp_path / 'tea.db'))
    assert [request['dimensions'] for request in requests] == [
        ['date'], ['date', 'page'], ['date', 'page', 'query']]


def test_successful_empty_daily_fetch_removes_stale_rows_in_only_its_grain(tmp_path):
    import pytest
    db = Database(tmp_path / 'tea.db')
    db.insert_performance_snapshot(url='', snapshot_date='2026-09-28', clicks=3)
    db.insert_performance_snapshot(url='https://chinatea.house/', snapshot_date='2026-09-28', clicks=2)
    with pytest.raises(ValueError):
        db.replace_daily_performance_window([{'date': None}], '2026-09-01', '2026-09-28', 'site')
    assert db.get_performance_summary(url_only=False)['total_clicks'] == 3
    db.replace_daily_performance_window([], '2026-09-01', '2026-09-28', 'site')
    assert not db.get_performance_summary(url_only=False)['available']
    assert db.get_performance_summary()['total_clicks'] == 2


def test_weekly_target_uses_separate_seven_day_site_totals(tmp_path, monkeypatch, capsys):
    import importlib.util
    from datetime import date, timedelta
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('weekly_target_test', Path(__file__).parents[1] / 'scripts/weekly_seo_loop.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    end = date(2026, 9, 28)
    monkeypatch.setattr(module, 'search_window', lambda days: (
        (end - timedelta(days=days - 1)).isoformat(), end.isoformat()))
    db = Database(tmp_path / 'tea.db')
    module.print_report(module.generate_report(db))
    assert 'Weekly result unknown' in capsys.readouterr().out
    for offset in range(14):
        db.insert_performance_snapshot(url='', snapshot_date=(end - timedelta(days=offset)).isoformat(),
            clicks=1 if offset < 7 else 2, impressions=10)
    db.insert_performance_snapshot(url='https://chinatea.house/', query='tea',
        snapshot_date=end.isoformat(), clicks=100, impressions=1000)
    report = module.generate_report(db)
    assert report['weekly']['period'] == {'start': '2026-09-22', 'end': '2026-09-28'}
    assert report['weekly']['previous_period'] == {'start': '2026-09-15', 'end': '2026-09-21'}
    assert report['weekly']['summary']['total_clicks'] == 7
    assert report['weekly']['previous_summary']['total_clicks'] == 14
    module.print_report(report)
    assert 'Weekly target: met.' in capsys.readouterr().out
