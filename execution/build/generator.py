"""
Static site generator for chinatea.house.

Generates 50,000+ pages with parallel processing and incremental builds.
"""

import csv
import json
import time
from collections import Counter
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
    create_home_context,
    create_region_index_context,
    create_category_index_context,
    create_occasion_context,
    create_brewing_guide_context,
    create_guide_context,
    create_guide_index_context,
    create_caffeine_chart_context,
    create_comparison_index_context,
    create_about_context,
    create_contact_context,
    create_tea_finder_context,
    create_dataset_context,
    load_guides,
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

        # Homepage
        if not template_filter or template_filter == "home":
            pages_to_generate.extend(self._collect_home_page())

        # Category pages
        if not template_filter or template_filter == "category":
            pages_to_generate.extend(self._collect_category_pages())
            pages_to_generate.extend(self._collect_category_index_page())

        # Region pages
        if not template_filter or template_filter == "region":
            pages_to_generate.extend(self._collect_region_pages())
            pages_to_generate.extend(self._collect_region_index_page())

        # Tea detail pages
        if not template_filter or template_filter == "tea-detail":
            pages_to_generate.extend(self._collect_tea_pages())

        # Comparison pages
        if not template_filter or template_filter == "comparison":
            pages_to_generate.extend(self._collect_comparison_pages())
            pages_to_generate.extend(self._collect_comparison_index_page())

        # Occasion pages
        if not template_filter or template_filter == "occasion":
            pages_to_generate.extend(self._collect_occasion_pages())

        # Brewing guide pages
        if not template_filter or template_filter == "brewing":
            pages_to_generate.extend(self._collect_brewing_pages())

        # Evergreen guide pages
        if not template_filter or template_filter == "guide":
            pages_to_generate.extend(self._collect_guide_pages())
            pages_to_generate.extend(self._collect_guide_index_page())

        # Caffeine chart page
        if not template_filter or template_filter == "caffeine-chart":
            pages_to_generate.extend(self._collect_caffeine_chart_page())

        # Static utility pages
        if not template_filter or template_filter == "static":
            pages_to_generate.extend(self._collect_static_pages())

        # Interactive tea finder
        if not template_filter or template_filter == "tea-finder":
            pages_to_generate.extend(self._collect_tea_finder_page())

        # Dataset download page
        if not template_filter or template_filter == "dataset":
            pages_to_generate.extend(self._collect_dataset_page())

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

        # Export downloadable datasets (only on full builds or when explicitly requested)
        if not template_filter or template_filter == "dataset":
            try:
                self._export_tea_datasets()
                self._generate_shareable_assets()
                self._generate_rss_feed()
            except Exception as e:
                result["errors"].append(f"dataset export: {str(e)}")

        result["duration_seconds"] = time.time() - start_time
        return result

    def _collect_home_page(self) -> list[dict]:
        """Collect homepage."""
        categories = self.db.get_all_categories()
        regions = self.db.get_all_regions()
        teas = self.db.get_all_teas()
        comparisons = self.db.get_all_comparisons(valid_only=True)
        occasions = self.db.get_all_occasions()

        data = {
            "categories": [c.id for c in categories],
            "regions_count": len(regions),
            "teas_count": len(teas),
            "comparisons_count": len(comparisons),
            "occasions": [o.id for o in occasions],
        }

        context = create_home_context(
            categories=categories,
            regions=regions,
            teas=teas,
            comparison_count=len(comparisons),
            occasions=occasions,
        )

        return [{
            "url": "/",
            "template": "index.html",
            "data": data,
            "context": context,
        }]

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

    def _collect_category_index_page(self) -> list[dict]:
        """Collect category index page."""
        categories = self.db.get_all_categories()
        teas = self.db.get_all_teas()

        # Group teas by category
        teas_by_category = {}
        for tea in teas:
            if tea.category_id:
                if tea.category_id not in teas_by_category:
                    teas_by_category[tea.category_id] = []
                teas_by_category[tea.category_id].append(tea)

        data = {
            "categories": [c.id for c in categories],
        }

        context = create_category_index_context(
            categories=categories,
            teas_by_category=teas_by_category,
        )

        return [{
            "url": "/category/",
            "template": "pillars/category-index.html",
            "data": data,
            "context": context,
        }]

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

    def _collect_region_index_page(self) -> list[dict]:
        """Collect region index page."""
        all_regions = self.db.get_all_regions()
        teas = self.db.get_all_teas()

        # Get provinces (top-level regions with no parent)
        provinces = [r for r in all_regions if r.parent_id is None]

        # Group regions by province
        regions_by_province = {}
        for province in provinces:
            regions_by_province[province.id] = [
                r for r in all_regions if r.parent_id == province.id
            ]

        # Group teas by region
        teas_by_region = {}
        for tea in teas:
            if tea.region_id:
                if tea.region_id not in teas_by_region:
                    teas_by_region[tea.region_id] = []
                teas_by_region[tea.region_id].append(tea)

        data = {
            "provinces": [p.id for p in provinces],
            "regions_count": len(all_regions),
        }

        context = create_region_index_context(
            provinces=provinces,
            all_regions=all_regions,
            regions_by_province=regions_by_province,
            teas_by_region=teas_by_region,
        )

        return [{
            "url": "/region/",
            "template": "pillars/region-index.html",
            "data": data,
            "context": context,
        }]

    def _collect_tea_pages(self) -> list[dict]:
        """Collect all tea detail pages to generate."""
        pages = []
        teas_list = self.db.get_all_teas()
        teas = {t.id: t for t in teas_list}  # Dict for lookups
        categories = {c.id: c for c in self.db.get_all_categories()}
        regions = {r.id: r for r in self.db.get_all_regions()}
        occasions = self.db.get_all_occasions()

        for tea in teas_list:
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
            comparisons_raw = self.db.get_comparisons_for_tea(tea.id)
            # Populate tea_a and tea_b objects for each comparison
            comparisons = []
            for comp in comparisons_raw:
                comp_dict = comp.model_dump() if hasattr(comp, 'model_dump') else dict(comp)
                comp_dict['tea_a'] = teas.get(comp.tea_a_id)
                comp_dict['tea_b'] = teas.get(comp.tea_b_id)
                if comp_dict['tea_a'] and comp_dict['tea_b']:
                    comparisons.append(type('Comparison', (), comp_dict)())

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

    def _collect_comparison_index_page(self) -> list[dict]:
        """Collect the comparison index page to generate."""
        categories = self.db.get_all_categories()
        comparisons = self.db.get_all_comparisons(valid_only=True)
        teas = self.db.get_all_teas()
        context = create_comparison_index_context(
            categories=categories,
            comparisons=comparisons,
            teas=teas,
        )

        return [{
            "url": "/compare/",
            "template": "pillars/comparison-index.html",
            "data": {"comparison_count": len(comparisons)},
            "context": context,
        }]

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

    def _collect_occasion_pages(self) -> list[dict]:
        """Collect all best-tea-for occasion pages to generate."""
        pages = []
        occasions = self.db.get_all_occasions()
        teas = self.db.get_all_teas()

        for occasion in occasions:
            context = create_occasion_context(occasion=occasion, all_teas=teas)

            data = {
                "occasion": occasion.model_dump(),
                "recommended_teas": [t.id for t in context["recommended_teas"]],
            }

            pages.append({
                "url": f"/best-tea-for/{occasion.id}/",
                "template": "pillars/occasion.html",
                "data": data,
                "context": context,
            })

        return pages

    def _collect_brewing_pages(self) -> list[dict]:
        """Collect all brewing guide pages to generate."""
        pages = []
        categories = self.db.get_all_categories()
        teas = self.db.get_all_teas()

        teas_by_category = {}
        for tea in teas:
            teas_by_category.setdefault(tea.category_id, []).append(tea)

        for category in categories:
            example_teas = sorted(
                teas_by_category.get(category.id, []),
                key=lambda t: (t.tier, t.name_en)
            )[:6]

            context = create_brewing_guide_context(
                category=category,
                example_teas=example_teas,
            )

            data = {
                "category": category.id,
                "example_teas": [t.id for t in example_teas],
            }

            pages.append({
                "url": f"/brewing/{category.id}/",
                "template": "pillars/brewing-guide.html",
                "data": data,
                "context": context,
            })

        return pages

    def _collect_guide_pages(self) -> list[dict]:
        """Collect all evergreen guide pages to generate."""
        pages = []
        guides = load_guides()

        for guide in guides:
            context = create_guide_context(guide=guide)

            data = {
                "guide_id": guide["id"],
            }

            pages.append({
                "url": f"/guide/{guide['id']}/",
                "template": "pillars/guide.html",
                "data": data,
                "context": context,
            })

        return pages

    def _collect_guide_index_page(self) -> list[dict]:
        """Collect the guide index page to generate."""
        guides = load_guides()
        context = create_guide_index_context(guides=guides)

        return [{
            "url": "/guide/",
            "template": "pillars/guide-index.html",
            "data": {"guide_count": len(guides)},
            "context": context,
        }]

    def _collect_caffeine_chart_page(self) -> list[dict]:
        """Collect the caffeine chart page to generate."""
        teas = self.db.get_all_teas()
        context = create_caffeine_chart_context(teas=teas)

        return [{
            "url": "/chinese-tea-caffeine-chart/",
            "template": "pillars/caffeine-chart.html",
            "data": {"page": "caffeine-chart"},
            "context": context,
        }]

    def _collect_static_pages(self) -> list[dict]:
        """Collect static utility pages like About and Contact."""
        pages = [
            {
                "url": "/about/",
                "template": "pillars/about.html",
                "data": {"page": "about"},
                "context": create_about_context(),
            },
            {
                "url": "/contact/",
                "template": "pillars/contact.html",
                "data": {"page": "contact"},
                "context": create_contact_context(),
            },
        ]
        return pages

    def _collect_tea_finder_page(self) -> list[dict]:
        """Collect the interactive tea finder page."""
        teas = self.db.get_all_teas()
        context = create_tea_finder_context(teas=teas)

        return [{
            "url": "/find-your-tea/",
            "template": "pillars/tea-finder.html",
            "data": {"page": "tea-finder"},
            "context": context,
        }]

    def _collect_dataset_page(self) -> list[dict]:
        """Collect the dataset download page."""
        teas = self.db.get_all_teas()
        context = create_dataset_context(tea_count=len(teas))

        return [{
            "url": "/dataset/",
            "template": "pillars/dataset.html",
            "data": {"page": "dataset", "tea_count": len(teas)},
            "context": context,
        }]

    def _generate_rss_feed(self) -> None:
        """Generate an RSS feed for guides and new pages."""
        from xml.sax.saxutils import escape

        guides = load_guides()
        today = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            '  <channel>',
            '    <title>China Tea House</title>',
            '    <link>https://chinatea.house/</link>',
            '    <description>A free guide to Chinese tea: types, regions, brewing, and comparisons.</description>',
            '    <language>en-us</language>',
            '    <lastBuildDate>' + today + '</lastBuildDate>',
            '    <atom:link href="https://chinatea.house/feed.xml" rel="self" type="application/rss+xml"/>',
        ]

        items = []
        for guide in guides:
            items.append({
                "title": guide["title"],
                "link": f"https://chinatea.house/guide/{guide['id']}/",
                "description": guide["description"],
            })
        # Add key pages
        items.extend([
            {"title": "Chinese Tea Caffeine Chart", "link": "https://chinatea.house/chinese-tea-caffeine-chart/", "description": "Compare caffeine levels across 136 Chinese teas."},
            {"title": "Find Your Chinese Tea", "link": "https://chinatea.house/find-your-tea/", "description": "Interactive tea recommendation tool."},
            {"title": "Chinese Tea Dataset", "link": "https://chinatea.house/dataset/", "description": "Free JSON and CSV dataset of Chinese teas."},
        ])

        for item in items:
            xml_lines.extend([
                '    <item>',
                '      <title>' + escape(item["title"]) + '</title>',
                '      <link>' + escape(item["link"]) + '</link>',
                '      <description>' + escape(item["description"]) + '</description>',
                '      <pubDate>' + today + '</pubDate>',
                '    </item>',
            ])

        xml_lines.extend([
            '  </channel>',
            '</rss>',
        ])

        rss_path = self.output_dir / "feed.xml"
        rss_path.write_text('\n'.join(xml_lines), encoding='utf-8')

    def _generate_shareable_assets(self) -> None:
        """Generate shareable images/charts for social media."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from collections import defaultdict

        teas = self.db.get_all_teas()
        categories = {c.id: c.name_en for c in self.db.get_all_categories()}

        # Prepare category caffeine counts
        cat_order = ['green', 'oolong', 'black', 'puerh', 'white', 'yellow', 'dark', 'scented']
        caffeine_order = ['low', 'moderate', 'high']
        color_map = {'low': '#7a9e7a', 'moderate': '#b8956c', 'high': '#a65d4e'}

        counts = {cat: defaultdict(int) for cat in cat_order}
        for tea in teas:
            cat = tea.category_id
            caf = tea.caffeine_level.value if tea.caffeine_level else 'moderate'
            if cat in cat_order and caf in caffeine_order:
                counts[cat][caf] += 1

        bottom = [0] * len(cat_order)
        fig, ax = plt.subplots(figsize=(12, 7))

        for caf in caffeine_order:
            values = [counts[cat][caf] for cat in cat_order]
            ax.bar(
                [categories.get(c, c).replace(' Tea', '') for c in cat_order],
                values,
                bottom=bottom,
                label=caf.title(),
                color=color_map[caf]
            )
            bottom = [b + v for b, v in zip(bottom, values)]

        ax.set_ylabel('Number of Teas', fontsize=12)
        ax.set_title('Chinese Tea Caffeine Levels by Category\n136 teas from chinatea.house', fontsize=16, pad=20)
        ax.legend(title='Caffeine Level', loc='upper right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        assets_dir = self.output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(assets_dir / "chinese-tea-caffeine-chart.png", dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        # Categories chart
        cat_counts = Counter(t.category_id for t in teas)
        cat_order = ['green', 'oolong', 'black', 'puerh', 'white', 'yellow', 'dark', 'scented']
        colors_cat = ['#7a9e7a', '#b8956c', '#a65d4e', '#5c4a3d', '#c9c4b8', '#c9b896', '#8b6914', '#b89fa3']
        values = [cat_counts.get(c, 0) for c in cat_order]
        short_labels = [categories.get(c, c).replace(' Tea', '') for c in cat_order]

        fig2, ax2 = plt.subplots(figsize=(12, 7))
        bars = ax2.barh(short_labels[::-1], values[::-1], color=colors_cat[::-1])
        ax2.set_xlabel('Number of Teas', fontsize=12)
        ax2.set_title('The 8 Types of Chinese Tea\n136 teas from chinatea.house', fontsize=16, pad=20)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 0.3, bar.get_y() + bar.get_height()/2, str(int(width)), va='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(assets_dir / "chinese-tea-categories.png", dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig2)

    def _export_tea_datasets(self) -> None:
        """Export downloadable JSON and CSV datasets of all teas."""
        teas = self.db.get_all_teas()
        categories = {c.id: c.name_en for c in self.db.get_all_categories()}
        regions = {r.id: r.name_en for r in self.db.get_all_regions()}

        dataset_dir = self.output_dir / "data"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        records = []
        for tea in teas:
            records.append({
                "id": tea.id,
                "name_en": tea.name_en,
                "name_zh": tea.name_zh,
                "category": categories.get(tea.category_id, tea.category_id),
                "region": regions.get(tea.region_id, tea.region_id),
                "caffeine_level": tea.caffeine_level.value if tea.caffeine_level else None,
                "body": tea.body.value if tea.body else None,
                "oxidation_level": tea.oxidation_level,
                "flavor_primary": ",".join(tea.flavor_primary) if tea.flavor_primary else None,
                "description_brief": tea.description_brief,
                "tier": tea.tier,
            })

        # JSON export
        json_path = dataset_dir / "chinese-tea-dataset.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "source": "https://chinatea.house",
                "generated_at": datetime.now().isoformat(),
                "count": len(records),
                "teas": records,
            }, f, ensure_ascii=False, indent=2)

        # CSV export
        csv_path = dataset_dir / "chinese-tea-dataset.csv"
        if records:
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)

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
            ["/category/"] + [f"/category/{c.id}/" for c in self.db.get_all_categories()],
            priority="1.0",
            changefreq="weekly"
        ))

        # Region sitemap
        sitemap_index.append(self._generate_sitemap(
            "sitemap-regions.xml",
            ["/region/"] + [f"/region/{r.id}/" for r in self.db.get_all_regions()],
            priority="0.9",
            changefreq="weekly"
        ))

        # Homepage sitemap
        sitemap_index.append(self._generate_sitemap(
            "sitemap-home.xml",
            ["/"],
            priority="1.0",
            changefreq="daily"
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
            urls = ["/compare/"]
            for comp in comparisons:
                sorted_ids = sorted([comp.tea_a_id, comp.tea_b_id])
                urls.append(f"/compare/{sorted_ids[0]}-vs-{sorted_ids[1]}/")
            sitemap_index.append(self._generate_sitemap(
                "sitemap-comparisons.xml",
                urls,
                priority="0.6",
                changefreq="monthly"
            ))

        # Occasion sitemap
        occasions = self.db.get_all_occasions()
        if occasions:
            sitemap_index.append(self._generate_sitemap(
                "sitemap-occasions.xml",
                [f"/best-tea-for/{o.id}/" for o in occasions],
                priority="0.7",
                changefreq="monthly"
            ))

        # Brewing guide sitemap
        categories = self.db.get_all_categories()
        if categories:
            sitemap_index.append(self._generate_sitemap(
                "sitemap-brewing.xml",
                [f"/brewing/{c.id}/" for c in categories],
                priority="0.7",
                changefreq="monthly"
            ))

        # Evergreen guide sitemap
        guides = load_guides()
        if guides:
            guide_urls = ["/guide/", "/chinese-tea-caffeine-chart/"] + [f"/guide/{g['id']}/" for g in guides]
            sitemap_index.append(self._generate_sitemap(
                "sitemap-guides.xml",
                guide_urls,
                priority="0.8",
                changefreq="monthly"
            ))

        # Static utility sitemap
        sitemap_index.append(self._generate_sitemap(
            "sitemap-static.xml",
            ["/about/", "/contact/", "/find-your-tea/", "/dataset/"],
            priority="0.5",
            changefreq="yearly"
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

    def generate_robots_txt(self) -> None:
        """Generate robots.txt."""
        content = """# robots.txt for chinatea.house
User-agent: *
Allow: /

Sitemap: https://chinatea.house/sitemap.xml
"""
        (self.output_dir / "robots.txt").write_text(content)
