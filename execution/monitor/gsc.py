"""
Google Search Console integration for chinatea.house.

Supports:
- Site ownership verification meta tag rendering
- Search analytics ingestion via the GSC API
- Sitemap submission helper
- URL inspection helper (when credentials permit)

The API client uses a service account JSON file by default. OAuth credentials
are also supported via the credential_type config field.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


GSC_CONFIG_PATHS = [
    Path("config/gsc.yaml"),
    Path("config/gsc.yml"),
    Path(".gsc.yaml"),
    Path(".gsc.yml"),
]


class GSCConfig(BaseModel):
    """Configuration for Google Search Console integration."""

    site_url: str = "https://chinatea.house/"
    # Verification code for the HTML tag method in GSC.
    # Example: "abc123..."
    verification_code: Optional[str] = None

    # API credentials
    credential_type: str = Field(default="service_account", pattern=r"^(service_account|oauth)$")
    credentials_path: Optional[Path] = None
    # For OAuth flows (not needed for service accounts)
    client_secrets_path: Optional[Path] = None

    # Scopes to request
    scopes: list[str] = Field(default_factory=lambda: [
        "https://www.googleapis.com/auth/webmasters",
        "https://www.googleapis.com/auth/webmasters.readonly",
    ])

    # Default date window for analytics fetches
    default_days: int = 28

    @field_validator("site_url")
    @classmethod
    def normalize_site_url(cls, v: str) -> str:
        # Domain properties use the sc-domain: prefix and must not have a
        # protocol or trailing slash.
        if v.startswith("sc-domain:"):
            return v.rstrip("/")
        if not v.endswith("/"):
            v = v + "/"
        if not v.startswith("http://") and not v.startswith("https://"):
            v = "https://" + v
        return v

    @field_validator("credentials_path", "client_secrets_path", mode="before")
    @classmethod
    def resolve_path(cls, v: Any) -> Optional[Path]:
        if v is None:
            return None
        path = Path(v).expanduser()
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
        return path

    def has_api_credentials(self) -> bool:
        if self.credential_type == "service_account":
            return self.credentials_path is not None and self.credentials_path.exists()
        if self.credential_type == "oauth":
            return bool(
                os.getenv("GOOGLE_CLIENT_ID")
                and os.getenv("GOOGLE_CLIENT_SECRET")
                and os.getenv("GOOGLE_REFRESH_TOKEN")
            )
        return False


def _load_yaml_config(path: Path) -> dict[str, Any]:
    """Load YAML config if available."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is required to load GSC YAML config. "
            "Install it with: pip install pyyaml"
        ) from exc
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_gsc_config(path: Optional[Path] = None) -> GSCConfig:
    """Load GSC configuration from the first available config file.

    Environment variables override file values:
    - GSC_SITE_URL
    - GSC_CREDENTIAL_TYPE
    - GSC_CREDENTIALS_PATH
    """
    if path is not None:
        if not path.exists():
            raise FileNotFoundError(f"GSC config not found: {path}")
        data = _load_yaml_config(path)
    else:
        data = {}
        for candidate in GSC_CONFIG_PATHS:
            if candidate.exists():
                data = _load_yaml_config(candidate)
                break

    if site_url := os.getenv("GSC_SITE_URL"):
        data["site_url"] = site_url
    if credential_type := os.getenv("GSC_CREDENTIAL_TYPE"):
        data["credential_type"] = credential_type
    if credentials_path := os.getenv("GSC_CREDENTIALS_PATH"):
        data["credentials_path"] = credentials_path

    return GSCConfig(**data)


def get_verification_meta(config: Optional[GSCConfig] = None) -> Optional[str]:
    """Return the GSC HTML verification meta tag if a code is configured."""
    cfg = config or load_gsc_config()
    if not cfg.verification_code:
        return None
    return (
        f'<meta name="google-site-verification" '
        f'content="{cfg.verification_code}" />'
    )


@dataclass
class SearchAnalyticsRow:
    """One row of GSC search analytics data."""

    url: str
    query: Optional[str]
    date: Optional[str]
    clicks: int
    impressions: int
    ctr: float
    position: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "query": self.query,
            "date": self.date,
            "clicks": self.clicks,
            "impressions": self.impressions,
            "ctr": self.ctr,
            "position": self.position,
        }


class GoogleSearchConsole:
    """Client for Google Search Console API operations."""

    def __init__(self, config: Optional[GSCConfig] = None):
        self.config = config or load_gsc_config()
        self._service: Any = None

    def _build_service(self) -> Any:
        """Build the authenticated webmasters service."""
        try:
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            from google.oauth2.credentials import Credentials as OAuthCredentials
        except ImportError as exc:
            raise RuntimeError(
                "Google API client libraries are required for GSC API access. "
                "Install them with: pip install google-api-python-client google-auth google-auth-oauthlib"
            ) from exc

        if self.config.credential_type == "service_account":
            if not self.config.credentials_path or not self.config.credentials_path.exists():
                raise FileNotFoundError(
                    f"Service account credentials not found: {self.config.credentials_path}. "
                    "Set credentials_path in your GSC config."
                )
            credentials = service_account.Credentials.from_service_account_file(
                str(self.config.credentials_path),
                scopes=self.config.scopes,
            )
        elif self.config.credential_type == "oauth":
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
            missing = [
                var for var, value in {
                    "GOOGLE_CLIENT_ID": client_id,
                    "GOOGLE_CLIENT_SECRET": client_secret,
                    "GOOGLE_REFRESH_TOKEN": refresh_token,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(
                    f"OAuth credentials missing: {', '.join(missing)}. "
                    "Set these environment variables or use credential_type: service_account."
                )
            credentials = OAuthCredentials(
                token=None,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=self.config.scopes,
            )
        else:
            raise ValueError(f"Unsupported credential_type: {self.config.credential_type}")

        return build("webmasters", "v3", credentials=credentials, cache_discovery=False)

    @property
    def service(self) -> Any:
        if self._service is None:
            self._service = self._build_service()
        return self._service

    def test_connection(self) -> dict[str, Any]:
        """Test that the API credentials work and the site is accessible."""
        try:
            site = self.service.sites().get(siteUrl=self.config.site_url).execute()
            return {
                "success": True,
                "site_url": self.config.site_url,
                "site": site,
            }
        except Exception as exc:
            return {
                "success": False,
                "site_url": self.config.site_url,
                "error": str(exc),
            }

    def fetch_search_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dimensions: Optional[list[str]] = None,
        row_limit: int = 25000,
        start_row: int = 0,
    ) -> list[SearchAnalyticsRow]:
        """Fetch search analytics from GSC.

        Dimensions can include any combination of:
        - query
        - page
        - country
        - device
        - searchAppearance
        - date
        """
        if end_date is None:
            end_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        if start_date is None:
            start_date = (
                datetime.strptime(end_date, "%Y-%m-%d")
                - timedelta(days=self.config.default_days)
            ).strftime("%Y-%m-%d")

        dimensions = dimensions or ["page"]

        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "startRow": start_row,
        }

        response = (
            self.service.searchanalytics()
            .query(siteUrl=self.config.site_url, body=body)
            .execute()
        )

        rows = response.get("rows", [])
        results: list[SearchAnalyticsRow] = []
        for row in rows:
            keys = row.get("keys", [])
            # Map dimension values by position.
            dim_map = dict(zip(dimensions, keys))
            url = dim_map.get("page", "")
            query = dim_map.get("query")
            date = dim_map.get("date")
            results.append(
                SearchAnalyticsRow(
                    url=url,
                    query=query,
                    date=date,
                    clicks=int(row.get("clicks", 0)),
                    impressions=int(row.get("impressions", 0)),
                    ctr=float(row.get("ctr", 0.0)),
                    position=float(row.get("position", 0.0)),
                )
            )
        return results

    def fetch_all_search_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dimensions: Optional[list[str]] = None,
    ) -> list[SearchAnalyticsRow]:
        """Fetch all search analytics rows, paging through GSC's row limit."""
        all_rows: list[SearchAnalyticsRow] = []
        start_row = 0
        page_size = 25000
        while True:
            rows = self.fetch_search_analytics(
                start_date=start_date,
                end_date=end_date,
                dimensions=dimensions,
                row_limit=page_size,
                start_row=start_row,
            )
            if not rows:
                break
            all_rows.extend(rows)
            if len(rows) < page_size:
                break
            start_row += page_size
        return all_rows

    def submit_sitemap(self, sitemap_url: str) -> dict[str, Any]:
        """Submit a sitemap URL to GSC."""
        try:
            self.service.sitemaps().submit(
                siteUrl=self.config.site_url, feedpath=sitemap_url
            ).execute()
            return {"success": True, "sitemap_url": sitemap_url}
        except Exception as exc:
            return {"success": False, "sitemap_url": sitemap_url, "error": str(exc)}

    def list_sitemaps(self) -> dict[str, Any]:
        """List sitemaps known to GSC for this site."""
        try:
            result = (
                self.service.sitemaps().list(siteUrl=self.config.site_url).execute()
            )
            return {"success": True, "sitemaps": result.get("sitemap", [])}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def inspect_url(self, url: str) -> dict[str, Any]:
        """Inspect a single URL using the GSC URL Inspection API.

        Requires additional scope:
        https://www.googleapis.com/auth/webmasters.readonly is sufficient for read access.
        """
        try:
            result = (
                self.service.urlInspection().index().inspect(
                    body={"inspectionUrl": url, "siteUrl": self.config.site_url}
                ).execute()
            )
            return {"success": True, "url": url, "result": result}
        except Exception as exc:
            return {"success": False, "url": url, "error": str(exc)}


def summarize_performance(rows: list[SearchAnalyticsRow]) -> dict[str, Any]:
    """Aggregate a list of analytics rows into summary metrics."""
    if not rows:
        return {
            "total_clicks": 0,
            "total_impressions": 0,
            "avg_ctr": 0.0,
            "avg_position": 0.0,
            "url_count": 0,
            "query_count": 0,
        }

    total_clicks = sum(r.clicks for r in rows)
    total_impressions = sum(r.impressions for r in rows)
    avg_ctr = total_clicks / total_impressions if total_impressions else 0.0
    avg_position = sum(r.position * r.impressions for r in rows) / total_impressions if total_impressions else 0.0

    urls = {r.url for r in rows}
    queries = {r.query for r in rows if r.query}

    return {
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "avg_ctr": round(avg_ctr, 4),
        "avg_position": round(avg_position, 2),
        "url_count": len(urls),
        "query_count": len(queries),
    }
