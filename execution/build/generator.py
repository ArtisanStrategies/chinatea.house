"""
Static site generator for chinatea.house.

Generates 50,000+ pages with parallel processing and incremental builds.
"""

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional

from .templates import (
    TemplateEngine,
    create_tea_detail_context,
    create_comparison_context,
    create_category_context,
    create_region_context,
)
from .links import InternalLinkBuilder
from .manifest import PageManifestManager, count_words, count_internal_links


class SiteGenerator:
    """Main site generator with parallel processing."""

    def __init__(self, db, output_dir: Path):
        self.db = db
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(__file__).parent.parent.parent / "templates"

        self.template_engine = TemplateEngine(self.templates_dir)
        self.link_builder = InternalLinkBuilder(db)
        self.manifest_manager = PageManifestManager(db)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        incremental: bool = True,
        limit: Optional[int] = None,
        template_filter: Optional[str] = None,
    ) -> dict:
        """Build the static site."""
        start_time = time.time()
        result = {
            "pages_generated": 0,
            "pages_skipped": 0,
            "errors": [],
            "duration_seconds": 0,
        }

        # Get template hashes for change detection
        template_hashes = self.template_engine.get_all_template_hashes()

        # Collect all pages to generate
        pages_to_generate = []

        # Category pages
        if not template_filter or template_filter == "category":
            pages_to_generate.extend(self._collect_category_pages())

        # Region pages
        if not template_filter or template_filter == "region":
            pages_to_generate.extend(self._collect_region_pages())

        # Tea detail pages
        if not template_filter or template_filter == "tea-detail":
            pages_to_generate.extend(self._collect_tea_pages())

        # Comparison pages
        if not template_filter or template_filter == "comparison":
            pages_to_generate.extend(self._collect_comparison_pages())

        # Apply limit if specified
        if limit:
            pages_to_generate = pages_to_generate[:limit]

        # Filter to only stale pages if incremental
        if incremental:
            pages_to_generate = [
                p for p in pages_to_generate
                if self.manifest_manager.is_page_stale(
                    p["url"],
                    self.manifest_manager.compute_data_hash(p["data"]),
                    template_hashes.get(p["template"], "")
                )
            ]
            result["pages_skipped"] = len(pages_to_generate) if not limit else 0

        # Generate pages (single-threaded for now, can parallelize later)
        for page_info in pages_to_generate:
            try:
                self._generate_page(page_info, template_hashes)
                result["pages_generated"] += 1
            except Exception as e:
                result["errors"].append(f"{page_info['url']}: {str(e)}")

        result["duration_seconds"] = time.time() - start_time
        return result

    def _collect_category_pages(self) -> list[dict]:
        """Collect all category pages to generate."""
        pages = []
        categories = self.db.get_all_categories()

        for category in categories:
            links = self.link_builder.get_category_links(category)
            occasions = self.db.get_all_occasions()

            data = {
                "category": category.model_dump(),
                "teas": [t.model_dump() for t in links["teas"]],
            }

            context = create_category_context(
                category=category,
                subcategories=links["subcategories"],
                teas=links["teas"],
                teas_by_subcategory=links["teas_by_subcategory"],
                teas_by_region=links["teas_by_region"],
                regions=links["regions"],
                recommended_occasions=links["recommended_occasions"],
                other_categories=links["other_categories"],
                cross_links=links["cross_links"],
                parent_links=links["parent_links"],
            )

            pages.append({
                "url": f"/category/{category.id}/",
                "template": "pillars/category.html",
                "data": data,
                "context": context,
            })

        return pages

    def _collect_region_pages(self) -> list[dict]:
        """Collect all region pages to generate."""
        pages = []
        regions = self.db.get_all_regions()

        for region in regions:
            links = self.link_builder.get_region_links(region)

            data = {
                "region": region.model_dump(),
                "teas": [t.model_dump() for t in links["teas"]],
            }

            context = create_region_context(
                region=region,
                parent_region=links["parent_region"],
                child_regions=links["child_regions"],
                sibling_regions=links["sibling_regions"],
                teas=links["teas"],
                teas_by_category=links["teas_by_category"],
                teas_by_subregion=links["teas_by_subregion"],
                categories_in_region=links["categories_in_region"],
                region_content=None,  # TODO: Load curated content
                cross_links=links["cross_links"],
                parent_links=links["parent_links"],
            )

            pages.append({
                "url": f"/region/{region.id}/",
                "template": "pillars/region.html",
                "data": data,
                "context": context,
            })

        return pages

    def _collect_tea_pages(self) -> list[dict]:
        """Collect all tea detail pages to generate."""
        pages = []
        teas = self.db.get_all_teas()
        categories = {c.id: c for c in self.db.get_all_categories()}
        regions = {r.id: r for r in self.db.get_all_regions()}
        occasions = self.db.get_all_occasions()

        for tea in teas:
            category = categories.get(tea.category_id)
            region = regions.get(tea.region_id)
            subcategory = None
            if tea.subcategory_id:
                subs = self.db.get_subcategories_by_category(tea.category_id)
                subcategory = next((s for s in subs if s.id == tea.subcategory_id), None)

            province = None
            if region and region.parent_id:
                province = regions.get(region.parent_id)

            links = self.link_builder.get_tea_links(tea)
            comparisons = self.db.get_comparisons_for_tea(tea.id)

            data = {
                "tea": tea.model_dump(),
                "category_id": tea.category_id,
                "region_id": tea.region_id,
            }

            context = create_tea_detail_context(
                tea=tea,
                category=category,
                subcategory=subcategory,
                region=region,
                province=province,
                similar_teas=links["similar_teas"],
                comparisons=comparisons,
                occasions=occasions,
                recommended_teaware=links["recommended_teaware"],
                cross_links=links["cross_links"],
                parent_links=links["parent_links"],
            )

            pages.append({
                "url": f"/tea/{tea.id}/",
                "template": "satellites/tea-detail.html",
                "data": data,
                "context": context,
            })

        return pages

    def _collect_comparison_pages(self) -> list[dict]:
        """Collect all comparison pages to generate."""
        pages = []
        comparisons = self.db.get_all_comparisons(valid_only=True)
        teas = {t.id: t for t in self.db.get_all_teas()}
        categories = {c.id: c for c in self.db.get_all_categories()}
        regions = {r.id: r for r in self.db.get_all_regions()}

        for comparison in comparisons:
            tea_a = teas.get(comparison.tea_a_id)
            tea_b = teas.get(comparison.tea_b_id)

            if not tea_a or not tea_b:
                continue

            category_a = categories.get(tea_a.category_id)
            category_b = categories.get(tea_b.category_id)
            region_a = regions.get(tea_a.region_id)
            region_b = regions.get(tea_b.region_id)

            links = self.link_builder.get_comparison_links(tea_a, tea_b)

            data = {
                "tea_a_id": tea_a.id,
                "tea_b_id": tea_b.id,
                "comparison_id": comparison.id,
            }

            context = create_comparison_context(
                tea_a=tea_a,
                tea_b=tea_b,
                category_a=category_a,
                category_b=category_b,
                region_a=region_a,
                region_b=region_b,
                comparison=comparison,
                related_comparisons=links["related_comparisons"],
                cross_links=links["cross_links"],
                parent_links=links["parent_links"],
            )

            # Canonical URL uses alphabetically sorted tea IDs
            sorted_ids = sorted([tea_a.id, tea_b.id])
            url = f"/compare/{sorted_ids[0]}-vs-{sorted_ids[1]}/"

            pages.append({
                "url": url,
                "template": "satellites/comparison.html",
                "data": data,
                "context": context,
            })

        return pages

    def _generate_page(self, page_info: dict, template_hashes: dict) -> None:
        """Generate a single page."""
        url = page_info["url"]
        template = page_info["template"]
        context = page_info["context"]
        data = page_info["data"]

        # Render template
        html = self.template_engine.render(template, context)

        # Calculate output path
        if url.endswith("/"):
            output_path = self.output_dir / url.strip("/") / "index.html"
        else:
            output_path = self.output_dir / url.strip("/")

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        output_path.write_text(html)

        # Update manifest
        data_hash = self.manifest_manager.compute_data_hash(data)
        template_hash = template_hashes.get(template, "")

        self.manifest_manager.update_manifest(
            url=url,
            template=template,
            data_hash=data_hash,
            template_hash=template_hash,
            word_count=count_words(html),
            internal_links_count=count_internal_links(html),
        )

    def generate_sitemaps(self) -> None:
        """Generate XML sitemaps."""
        # Main sitemap index
        sitemap_index = []

        # Category sitemap
        sitemap_index.append(self._generate_sitemap(
            "sitemap-categories.xml",
            [f"/category/{c.id}/" for c in self.db.get_all_categories()],
            priority="1.0",
            changefreq="weekly"
        ))

        # Region sitemap
        sitemap_index.append(self._generate_sitemap(
            "sitemap-regions.xml",
            [f"/region/{r.id}/" for r in self.db.get_all_regions()],
            priority="0.9",
            changefreq="weekly"
        ))

        # Tea sitemap (split by category for large sites)
        for category in self.db.get_all_categories():
            teas = self.db.get_teas_by_category(category.id)
            if teas:
                sitemap_index.append(self._generate_sitemap(
                    f"sitemap-teas-{category.id}.xml",
                    [f"/tea/{t.id}/" for t in teas],
                    priority="0.8",
                    changefreq="monthly"
                ))

        # Comparison sitemap
        comparisons = self.db.get_all_comparisons()
        if comparisons:
            urls = []
            for comp in comparisons:
                sorted_ids = sorted([comp.tea_a_id, comp.tea_b_id])
                urls.append(f"/compare/{sorted_ids[0]}-vs-{sorted_ids[1]}/")
            sitemap_index.append(self._generate_sitemap(
                "sitemap-comparisons.xml",
                urls,
                priority="0.6",
                changefreq="monthly"
            ))

        # Write sitemap index
        self._write_sitemap_index(sitemap_index)

    def _generate_sitemap(
        self,
        filename: str,
        urls: list[str],
        priority: str,
        changefreq: str
    ) -> str:
        """Generate a single sitemap file."""
        base_url = "https://chinatea.house"
        today = datetime.now().strftime("%Y-%m-%d")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for url in urls:
            xml_lines.extend([
                '  <url>',
                f'    <loc>{base_url}{url}</loc>',
                f'    <lastmod>{today}</lastmod>',
                f'    <changefreq>{changefreq}</changefreq>',
                f'    <priority>{priority}</priority>',
                '  </url>',
            ])

        xml_lines.append('</urlset>')

        sitemap_path = self.output_dir / filename
        sitemap_path.write_text('\n'.join(xml_lines))

        return filename

    def _write_sitemap_index(self, sitemap_files: list[str]) -> None:
        """Write the sitemap index file."""
        base_url = "https://chinatea.house"
        today = datetime.now().strftime("%Y-%m-%d")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for filename in sitemap_files:
            xml_lines.extend([
                '  <sitemap>',
                f'    <loc>{base_url}/{filename}</loc>',
                f'    <lastmod>{today}</lastmod>',
                '  </sitemap>',
            ])

        xml_lines.append('</sitemapindex>')

        index_path = self.output_dir / "sitemap.xml"
        index_path.write_text('\n'.join(xml_lines))
