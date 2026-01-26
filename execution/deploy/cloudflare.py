"""
Cloudflare Pages deployment via Wrangler CLI.

Handles deployment of static site to Cloudflare Pages.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional


class CloudflareDeployer:
    """Deploys site to Cloudflare Pages using Wrangler."""

    def __init__(
        self,
        output_dir: Path,
        project_name: str = "chinatea-house",
        branch: str = "main"
    ):
        self.output_dir = Path(output_dir)
        self.project_name = project_name
        self.branch = branch

    def check_wrangler(self) -> bool:
        """Check if Wrangler CLI is installed."""
        try:
            result = subprocess.run(
                ["wrangler", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def deploy(self, production: bool = False) -> dict:
        """Deploy to Cloudflare Pages."""
        if not self.check_wrangler():
            return {
                "success": False,
                "error": "Wrangler CLI not installed. Run: npm install -g wrangler",
            }

        if not self.output_dir.exists():
            return {
                "success": False,
                "error": f"Output directory not found: {self.output_dir}",
            }

        # Build wrangler command
        cmd = [
            "wrangler", "pages", "deploy",
            str(self.output_dir),
            "--project-name", self.project_name,
        ]

        if production:
            cmd.extend(["--branch", self.branch])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                # Parse deployment URL from output
                url = self._extract_url(result.stdout)
                return {
                    "success": True,
                    "url": url,
                    "output": result.stdout,
                    "production": production,
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "returncode": result.returncode,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Deployment timed out after 10 minutes",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _extract_url(self, output: str) -> Optional[str]:
        """Extract deployment URL from Wrangler output."""
        # Look for URL patterns in output
        for line in output.split('\n'):
            line = line.strip()
            if 'pages.dev' in line or 'chinatea.house' in line:
                # Extract URL
                import re
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    return url_match.group(0)
        return None

    def preview(self) -> dict:
        """Deploy to preview environment."""
        return self.deploy(production=False)

    def publish(self) -> dict:
        """Deploy to production."""
        return self.deploy(production=True)

    def get_deployment_status(self) -> dict:
        """Get current deployment status from Cloudflare."""
        if not self.check_wrangler():
            return {"error": "Wrangler not installed"}

        try:
            result = subprocess.run(
                ["wrangler", "pages", "deployment", "list",
                 "--project-name", self.project_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "deployments": result.stdout,
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                }
        except Exception as e:
            return {"error": str(e)}


def create_wrangler_config(project_dir: Path, project_name: str = "chinatea-house") -> Path:
    """Create wrangler.toml configuration file."""
    config = f"""# Cloudflare Pages configuration for {project_name}
name = "{project_name}"
compatibility_date = "2024-01-01"

[site]
bucket = "./output"

# Custom domain (configure in Cloudflare dashboard)
# route = "chinatea.house/*"

# Build settings (for Pages Functions if needed)
# [build]
# command = "python -m execution.cli build"
# cwd = "."
"""

    config_path = project_dir / "wrangler.toml"
    config_path.write_text(config)
    return config_path


def create_headers_file(output_dir: Path) -> Path:
    """Create _headers file for Cloudflare Pages."""
    headers = """# Cloudflare Pages headers for chinatea.house

# All pages
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()

# Static assets - long cache
/*.css
  Cache-Control: public, max-age=31536000, immutable

/*.js
  Cache-Control: public, max-age=31536000, immutable

/images/*
  Cache-Control: public, max-age=31536000, immutable

# HTML pages - short cache for freshness
/*.html
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400

# Sitemaps
/sitemap*.xml
  Cache-Control: public, max-age=86400
  Content-Type: application/xml

# Robots
/robots.txt
  Cache-Control: public, max-age=86400
"""

    headers_path = output_dir / "_headers"
    headers_path.write_text(headers)
    return headers_path


def create_redirects_file(output_dir: Path) -> Path:
    """Create _redirects file for Cloudflare Pages."""
    redirects = """# Cloudflare Pages redirects for chinatea.house

# Trailing slash normalization
/tea/* /tea/:splat/ 301
/category/* /category/:splat/ 301
/region/* /region/:splat/ 301
/compare/* /compare/:splat/ 301

# Old URL redirects (add as needed)
# /old-path /new-path 301

# Common typos/variations
/oolong-tea /category/oolong/ 301
/green-tea /category/green/ 301
/puerh /category/dark/ 301
/pu-erh /category/dark/ 301
"""

    redirects_path = output_dir / "_redirects"
    redirects_path.write_text(redirects)
    return redirects_path
