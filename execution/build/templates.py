"""
Jinja2 template engine configuration for chinatea.house.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
import xxhash


class TemplateEngine:
    """Manages Jinja2 template rendering."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.env = self._create_environment()
        self._template_hashes: dict[str, str] = {}

    def _create_environment(self) -> Environment:
        """Create and configure Jinja2 environment."""
        env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        env.filters["json_dumps"] = lambda x: json.dumps(x, default=str)
        env.filters["slugify"] = self._slugify
        env.filters["format_price"] = self._format_price

        # Add global variables
        env.globals["current_year"] = datetime.now().year
        env.globals["site_name"] = "China Tea House"
        env.globals["site_url"] = "https://chinatea.house"

        return env

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-safe slug."""
        return text.lower().replace(" ", "-").replace("'", "")

    @staticmethod
    def _format_price(price_range) -> str:
        """Format price range for display."""
        if not price_range:
            return ""
        return f"${price_range.min_usd_per_50g:.0f}-${price_range.max_usd_per_50g:.0f}"

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with context."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def get_template_hash(self, template_name: str) -> str:
        """Get hash of template file for change detection."""
        if template_name not in self._template_hashes:
            template_path = self.templates_dir / template_name
            if template_path.exists():
                content = template_path.read_text()
                # Also hash included templates
                self._template_hashes[template_name] = xxhash.xxh64(content).hexdigest()
            else:
                self._template_hashes[template_name] = ""
        return self._template_hashes[template_name]

    def get_all_template_hashes(self) -> dict[str, str]:
        """Get hashes for all templates."""
        hashes = {}
        for template_file in self.templates_dir.rglob("*.html"):
            rel_path = template_file.relative_to(self.templates_dir)
            template_name = str(rel_path)
            hashes[template_name] = self.get_template_hash(template_name)
        return hashes


def create_tea_detail_context(
    tea,
    category,
    subcategory,
    region,
    province,
    similar_teas,
    comparisons,
    occasions,
    recommended_teaware,
    cross_links,
    parent_links,
) -> dict[str, Any]:
    """Create template context for tea detail page."""
    return {
        "tea": tea,
        "category": category,
        "subcategory": subcategory,
        "region": region,
        "province": province,
        "similar_teas": similar_teas,
        "comparisons": comparisons,
        "occasions": {o.id: o for o in occasions} if occasions else {},
        "recommended_teaware": recommended_teaware,
        "cross_links": cross_links,
        "parent_links": parent_links,
        "page_title": f"{tea.name_en} - {category.name_en}",
        "meta_description": tea.description_brief[:160],
        "canonical_url": f"https://chinatea.house/tea/{tea.id}/",
        "breadcrumbs": [
            {"label": category.name_en, "url": f"/category/{category.id}/"},
            {"label": tea.name_en, "url": None},
        ],
    }


def create_comparison_context(
    tea_a,
    tea_b,
    category_a,
    category_b,
    region_a,
    region_b,
    comparison,
    related_comparisons,
    cross_links,
    parent_links,
) -> dict[str, Any]:
    """Create template context for comparison page."""
    return {
        "tea_a": tea_a,
        "tea_b": tea_b,
        "category_a": category_a,
        "category_b": category_b,
        "region_a": region_a,
        "region_b": region_b,
        "comparison": comparison,
        "related_comparisons": related_comparisons,
        "cross_links": cross_links,
        "parent_links": parent_links,
        "page_title": f"{tea_a.name_en} vs {tea_b.name_en}",
        "meta_description": f"Compare {tea_a.name_en} and {tea_b.name_en}: flavor profiles, brewing methods, prices.",
        "canonical_url": f"https://chinatea.house/compare/{tea_a.id}-vs-{tea_b.id}/",
        "breadcrumbs": [
            {"label": "Comparisons", "url": "/compare/"},
            {"label": f"{tea_a.name_en} vs {tea_b.name_en}", "url": None},
        ],
    }


def create_category_context(
    category,
    subcategories,
    teas,
    teas_by_subcategory,
    teas_by_region,
    regions,
    recommended_occasions,
    other_categories,
    cross_links,
    parent_links,
) -> dict[str, Any]:
    """Create template context for category pillar page."""
    return {
        "category": category,
        "subcategories": subcategories,
        "teas": teas,
        "teas_by_subcategory": teas_by_subcategory,
        "teas_by_region": teas_by_region,
        "regions": regions,
        "recommended_occasions": recommended_occasions,
        "other_categories": other_categories,
        "cross_links": cross_links,
        "parent_links": parent_links,
        "page_title": f"{category.name_en} - Complete Guide",
        "meta_description": category.description[:160],
        "canonical_url": f"https://chinatea.house/category/{category.id}/",
        "breadcrumbs": [
            {"label": "Categories", "url": "/category/"},
            {"label": category.name_en, "url": None},
        ],
    }


def create_region_context(
    region,
    parent_region,
    child_regions,
    sibling_regions,
    teas,
    teas_by_category,
    teas_by_subregion,
    categories_in_region,
    region_content,
    cross_links,
    parent_links,
) -> dict[str, Any]:
    """Create template context for region pillar page."""
    return {
        "region": region,
        "parent_region": parent_region,
        "child_regions": child_regions,
        "sibling_regions": sibling_regions,
        "teas": teas,
        "teas_by_category": teas_by_category,
        "teas_by_subregion": teas_by_subregion,
        "categories_in_region": categories_in_region,
        "region_content": region_content,
        "cross_links": cross_links,
        "parent_links": parent_links,
        "page_title": f"{region.name_en} Tea Region",
        "meta_description": region.terroir_notes[:160] if region.terroir_notes else f"Discover teas from {region.name_en}",
        "canonical_url": f"https://chinatea.house/region/{region.id}/",
        "breadcrumbs": [
            {"label": "Regions", "url": "/region/"},
            {"label": region.name_en, "url": None},
        ],
    }
