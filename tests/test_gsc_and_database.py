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
