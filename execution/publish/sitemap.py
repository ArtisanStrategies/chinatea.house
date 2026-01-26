"""
Sitemap generation for chinatea.house.

Generates XML sitemaps split by content type for efficient crawling.
"""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from execution.data.db import Database


class SitemapGenerator:
    """Generates XML sitemaps for the site."""

    SITEMAP_LIMIT = 50000  # Max URLs per sitemap
    BASE_URL = "https://chinatea.house"

    # Priority and change frequency by template
    SITEMAP_CONFIG = {
        "pillars/category.html": {"priority": "1.0", "changefreq": "weekly"},
        "pillars/region.html": {"priority": "0.9", "changefreq": "weekly"},
        "satellites/tea-detail.html": {"priority": "0.8", "changefreq": "monthly"},
        "satellites/brewing.html": {"priority": "0.7", "changefreq": "monthly"},
        "satellites/occasion.html": {"priority": "0.7", "changefreq": "monthly"},
        "satellites/comparison.html": {"priority": "0.6", "changefreq": "monthly"},
    }

    def __init__(self, db: "Database", output_dir: Path):
        self.db = db
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self, published_only: bool = True) -> dict:
        """Generate all sitemaps and sitemap index."""
        sitemap_files = []
        total_urls = 0

        # Get pages
        if published_only:
            pages = self.db.get_pages_by_status("published")
        else:
            pages = []
            for status in ["draft", "published"]:
                pages.extend(self.db.get_pages_by_status(status))

        # Group by template type
        pages_by_template = {}
        for page in pages:
            template = page.template
            if template not in pages_by_template:
                pages_by_template[template] = []
            pages_by_template[template].append(page)

        # Generate sitemap for each template type
        for template, template_pages in pages_by_template.items():
            config = self.SITEMAP_CONFIG.get(template, {
                "priority": "0.5",
                "changefreq": "monthly"
            })

            # Split into chunks if needed
            chunks = [
                template_pages[i:i + self.SITEMAP_LIMIT]
                for i in range(0, len(template_pages), self.SITEMAP_LIMIT)
            ]

            for i, chunk in enumerate(chunks):
                filename = self._get_sitemap_filename(template, i if len(chunks) > 1 else None)
                self._write_sitemap(filename, chunk, config)
                sitemap_files.append(filename)
                total_urls += len(chunk)

        # Generate static pages sitemap
        static_urls = self._get_static_urls()
        if static_urls:
            self._write_static_sitemap(static_urls)
            sitemap_files.append("sitemap-static.xml")
            total_urls += len(static_urls)

        # Generate sitemap index
        self._write_sitemap_index(sitemap_files)

        return {
            "sitemap_files": sitemap_files,
            "total_urls": total_urls,
            "index_file": "sitemap.xml",
        }

    def _get_sitemap_filename(self, template: str, chunk_index: int = None) -> str:
        """Generate sitemap filename from template name."""
        # Convert template path to filename
        name = template.replace("/", "-").replace(".html", "")
        if chunk_index is not None:
            return f"sitemap-{name}-{chunk_index + 1}.xml"
        return f"sitemap-{name}.xml"

    def _write_sitemap(self, filename: str, pages: list, config: dict) -> None:
        """Write a single sitemap file."""
        today = datetime.now().strftime("%Y-%m-%d")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for page in pages:
            lastmod = page.published_at or page.generated_at or today
            if "T" in lastmod:
                lastmod = lastmod.split("T")[0]

            xml_lines.extend([
                '  <url>',
                f'    <loc>{self.BASE_URL}{page.url}</loc>',
                f'    <lastmod>{lastmod}</lastmod>',
                f'    <changefreq>{config["changefreq"]}</changefreq>',
                f'    <priority>{config["priority"]}</priority>',
                '  </url>',
            ])

        xml_lines.append('</urlset>')

        sitemap_path = self.output_dir / filename
        sitemap_path.write_text('\n'.join(xml_lines))

    def _get_static_urls(self) -> list[dict]:
        """Get URLs for static pages (home, about, etc.)."""
        return [
            {"url": "/", "priority": "1.0", "changefreq": "daily"},
            {"url": "/category/", "priority": "0.9", "changefreq": "weekly"},
            {"url": "/region/", "priority": "0.9", "changefreq": "weekly"},
            {"url": "/tea/", "priority": "0.8", "changefreq": "weekly"},
            {"url": "/brewing/", "priority": "0.8", "changefreq": "weekly"},
            {"url": "/best-tea-for/", "priority": "0.8", "changefreq": "weekly"},
            {"url": "/compare/", "priority": "0.7", "changefreq": "weekly"},
            {"url": "/teaware/", "priority": "0.7", "changefreq": "weekly"},
            {"url": "/about/", "priority": "0.5", "changefreq": "monthly"},
            {"url": "/contact/", "priority": "0.4", "changefreq": "yearly"},
            {"url": "/privacy/", "priority": "0.3", "changefreq": "yearly"},
        ]

    def _write_static_sitemap(self, urls: list[dict]) -> None:
        """Write sitemap for static pages."""
        today = datetime.now().strftime("%Y-%m-%d")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for page in urls:
            xml_lines.extend([
                '  <url>',
                f'    <loc>{self.BASE_URL}{page["url"]}</loc>',
                f'    <lastmod>{today}</lastmod>',
                f'    <changefreq>{page["changefreq"]}</changefreq>',
                f'    <priority>{page["priority"]}</priority>',
                '  </url>',
            ])

        xml_lines.append('</urlset>')

        sitemap_path = self.output_dir / "sitemap-static.xml"
        sitemap_path.write_text('\n'.join(xml_lines))

    def _write_sitemap_index(self, sitemap_files: list[str]) -> None:
        """Write the sitemap index file."""
        today = datetime.now().strftime("%Y-%m-%d")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for filename in sitemap_files:
            xml_lines.extend([
                '  <sitemap>',
                f'    <loc>{self.BASE_URL}/{filename}</loc>',
                f'    <lastmod>{today}</lastmod>',
                '  </sitemap>',
            ])

        xml_lines.append('</sitemapindex>')

        index_path = self.output_dir / "sitemap.xml"
        index_path.write_text('\n'.join(xml_lines))

    def generate_robots_txt(self) -> str:
        """Generate robots.txt content."""
        content = f"""# robots.txt for chinatea.house
User-agent: *
Allow: /

# Sitemaps
Sitemap: {self.BASE_URL}/sitemap.xml

# Crawl-delay (be gentle with small site)
Crawl-delay: 1
"""
        robots_path = self.output_dir / "robots.txt"
        robots_path.write_text(content)
        return str(robots_path)
