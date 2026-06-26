"""
Jinja2 template engine configuration for chinatea.house.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
import xxhash

from execution.monitor.gsc import get_verification_meta


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

        # Google Search Console verification tag (rendered only if configured)
        try:
            env.globals["gsc_verification"] = get_verification_meta()
        except Exception:
            env.globals["gsc_verification"] = None

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


def _value(value: Any) -> str:
    """Return enum value or string representation."""
    if value is None:
        return ""
    return getattr(value, "value", str(value))


def _label(value: Any) -> str:
    """Return a human-readable label."""
    return _value(value).replace("-", " ").title()


def _list_text(items: list[str], fallback: str = "") -> str:
    """Format a short English list."""
    items = [item for item in items if item]
    if not items:
        return fallback
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _category_processing(category_id: str) -> str:
    return {
        "green": "halted oxidation through early heat-fixing, so the finished tea keeps a fresh, high-toned profile",
        "white": "gentle withering and drying, which preserves delicacy while allowing a little natural oxidation",
        "yellow": "a sealed yellowing step after heat-fixing, which softens green-tea sharpness into a rounder cup",
        "oolong": "partial oxidation and repeated leaf handling, creating a wide spectrum from floral to roasted",
        "black": "full oxidation, which converts fresh leaf aromatics into malt, honey, fruit, and cocoa notes",
        "dark": "post-fermentation, where microbial transformation creates smoother, earthier flavors over time",
        "puerh": "Yunnan large-leaf material and post-processing that rewards aging, compression, and repeated infusions",
        "scented": "repeated contact with fresh flowers or aromatic botanicals so the base tea absorbs fragrance",
    }.get(category_id, "careful Chinese tea processing that shapes aroma, body, and finish")


def _build_tea_analysis(tea, category, region, province) -> list[str]:
    """Build deeper explanatory paragraphs for tea detail pages."""
    flavors = _list_text(tea.flavor_primary[:4], "subtle tea aromatics")
    secondary = _list_text(tea.flavor_secondary[:4], "quiet supporting notes")
    aroma = _list_text(tea.aroma[:3], "a restrained aroma")
    body = _label(tea.body).lower() if tea.body else "balanced"
    caffeine = _label(tea.caffeine_level).lower() if tea.caffeine_level else "moderate"
    origin = region.name_en
    if province and province.id != region.id:
        origin = f"{region.name_en} in {province.name_en}"

    paragraphs = [
        (
            f"In the cup, {tea.name_en} is best understood as a {category.name_en.lower()} built around "
            f"{flavors}. The secondary notes of {secondary} give it more range than a simple category label "
            f"suggests, while the aroma leans toward {aroma}. Expect a {body} body and a finish that "
            f"{tea.finish or 'shows the tea most clearly after the first few sips'}."
        ),
        (
            f"The origin matters here. {tea.name_en} is associated with {origin}, so the page should be read "
            f"as a profile of both tea style and place. {region.terroir_notes or 'Local climate, elevation, and leaf handling all influence how the tea presents in the cup.'} "
            f"That context helps explain why two teas in the same broad family can taste noticeably different."
        ),
        (
            f"Processing is the other major clue: {category.name_en.lower()} is typically { _category_processing(tea.category_id) }. "
            f"For {tea.name_en}, the oxidation level is "
            f"{int(tea.oxidation_level * 100)}% when measured on a simple scale." if tea.oxidation_level is not None else
            f"Processing is the other major clue: {category.name_en.lower()} is typically { _category_processing(tea.category_id) }."
        ),
    ]

    if tea.brewing_gongfu:
        params = tea.brewing_gongfu
        paragraphs.append(
            f"For brewing, start near {params.water_temp_c}C with about {params.leaf_ratio_g_per_100ml:g}g per 100ml. "
            f"The first infusion at roughly {params.first_steep_seconds} seconds should show the tea's structure without over-extracting it; "
            f"later steeps can move in {params.steep_increment_seconds}-second increments. Because the expected range is about "
            f"{params.num_steeps} infusions, this tea is better judged across a session than from one long steep."
        )

    if tea.price_mid or tea.price_premium or tea.price_budget:
        price = tea.price_mid or tea.price_budget or tea.price_premium
        paragraphs.append(
            f"When buying {tea.name_en}, use price as a quality signal but not the only one. A common mid-range benchmark is "
            f"around ${price.min_usd_per_50g:.0f}-${price.max_usd_per_50g:.0f} per 50g. Look for clean aroma, credible origin naming, "
            f"and leaf appearance that matches the style before paying premium prices."
        )

    if tea.best_for:
        occasions = _list_text([item.replace("-", " ") for item in tea.best_for[:4]])
        paragraphs.append(
            f"It is especially useful for {occasions}. With {caffeine} caffeine and a {body} body, it can fit different roles "
            f"depending on steep strength: lighter infusions emphasize fragrance, while slightly longer infusions bring out texture and finish."
        )

    return paragraphs


def _build_comparison_analysis(tea_a, tea_b, category_a, category_b, region_a, region_b) -> dict[str, str]:
    """Build deeper data-grounded comparison copy."""
    same_category = tea_a.category_id == tea_b.category_id
    same_region = tea_a.region_id == tea_b.region_id
    flavor_a = _list_text(tea_a.flavor_primary[:3], "subtle notes")
    flavor_b = _list_text(tea_b.flavor_primary[:3], "distinct notes")
    body_a = _label(tea_a.body).lower() if tea_a.body else "balanced"
    body_b = _label(tea_b.body).lower() if tea_b.body else "balanced"
    caffeine_a = _label(tea_a.caffeine_level).lower() if tea_a.caffeine_level else "moderate"
    caffeine_b = _label(tea_b.caffeine_level).lower() if tea_b.caffeine_level else "moderate"

    category_frame = (
        f"Both teas sit inside the {category_a.name_en.lower()} family, so the comparison is mainly about regional expression, cultivar, and leaf handling."
        if same_category else
        f"This is a cross-category comparison: {tea_a.name_en} is {category_a.name_en.lower()}, while {tea_b.name_en} is {category_b.name_en.lower()}."
    )
    region_frame = (
        f"They also share {region_a.name_en} as an origin, which makes differences in processing and leaf grade easier to isolate."
        if same_region else
        f"Origin pulls them apart as well: {tea_a.name_en} comes from {region_a.name_en}, while {tea_b.name_en} comes from {region_b.name_en}."
    )

    return {
        "context": (
            f"{category_frame} {region_frame} This matters because category tells you the processing logic, while region tells you the growing conditions behind aroma, body, and finish."
        ),
        "flavor": (
            f"Flavor is the clearest split. {tea_a.name_en} emphasizes {flavor_a} with a {body_a} body; "
            f"{tea_b.name_en} leans toward {flavor_b} with a {body_b} body. If you are choosing for aroma, compare the dry leaf and the first rinse; "
            f"if you are choosing for texture, judge the second and third infusions, where body and aftertaste usually become easier to read."
        ),
        "brewing": (
            f"Brewing should not be identical by default. {tea_a.name_en} starts best around "
            f"{tea_a.brewing_gongfu.water_temp_c if tea_a.brewing_gongfu else 'moderate'}C, while {tea_b.name_en} starts around "
            f"{tea_b.brewing_gongfu.water_temp_c if tea_b.brewing_gongfu else 'moderate'}C. Keep the leaf ratio steady, then adjust water temperature and steep time; "
            f"that makes the comparison fair without forcing one tea into another tea's brewing style."
        ),
        "buyer": (
            f"Choose {tea_a.name_en} when you want {flavor_a}, {caffeine_a} caffeine, and a {body_a} body. "
            f"Choose {tea_b.name_en} when {flavor_b}, {caffeine_b} caffeine, and a {body_b} body sound more useful. "
            f"For buying, favor the tea whose origin and processing style match how you actually drink: daily cups reward reliability, while slower gongfu sessions reward aromatic complexity and re-steep performance."
        ),
        "session": (
            f"In a side-by-side tasting, brew both teas with the same vessel size and similar leaf weight, then adjust only after the first two infusions. "
            f"Track three things: which tea opens faster, which tea keeps its structure after several steeps, and which finish you still notice after the cup is empty. "
            f"That tasting method usually reveals more than comparing dry descriptions or price alone."
        ),
        "mistakes": (
            f"The common mistake is judging both teas by the same standard. {tea_a.name_en} should be evaluated as {category_a.name_en.lower()} from {region_a.name_en}; "
            f"{tea_b.name_en} should be evaluated as {category_b.name_en.lower()} from {region_b.name_en}. A tea can be objectively well made yet still be the wrong choice "
            f"for your preferred water temperature, session length, flavor intensity, or caffeine tolerance."
        ),
    }


def _build_category_guide(category, teas, regions) -> list[str]:
    """Build deeper category page guide copy."""
    flavors = []
    for tea in teas:
        flavors.extend(tea.flavor_primary[:2])
    common_flavors = []
    for flavor in flavors:
        if flavor not in common_flavors:
            common_flavors.append(flavor)
    region_names = _list_text([r.name_en for r in regions[:5]], "several Chinese tea regions")
    tier1 = [tea.name_en for tea in teas if tea.tier == 1][:4]

    return [
        (
            f"{category.name_en} is not a single flavor so much as a processing family. In this database it includes "
            f"{len(teas)} teas from {region_names}. The shared foundation is that the leaves are { _category_processing(category.id) }, "
            f"but each origin and cultivar pushes that foundation in a different direction."
        ),
        (
            f"Across the listed teas, recurring flavor signals include {_list_text(common_flavors[:6], 'a broad range of aromas')}. "
            f"Those notes are a practical starting point for tasting: first identify the dominant family of aromas, then compare body, finish, and brewing tolerance."
        ),
        (
            f"Good entry points include {_list_text(tier1, 'the better-known examples in this category')}. Treat them as reference points rather than final answers. "
            f"Once you know the reference style, the less famous teas become easier to evaluate because you can tell whether a tea is lighter, roastier, sweeter, more aromatic, or more textural than the benchmark."
        ),
        (
            f"When buying {category.name_en.lower()}, avoid judging only by the broad category name. The same family can include both simple daily drinkers and highly specific regional teas. "
            f"Look for origin, harvest season, intact leaf, clean aroma, and brewing notes that fit how you actually prepare tea. A lower-priced tea with clear origin and fresh aroma is often more useful than an expensive tea with vague sourcing."
        ),
        (
            f"For tasting practice, brew two teas from this category side by side and keep the variables steady: same vessel, same water, same leaf ratio, and short repeated infusions. "
            f"The differences that appear after the second or third steep are usually the most reliable clues about quality, processing, and whether the tea suits your palate."
        ),
    ]


def _build_region_guide(region, teas, child_regions, categories_in_region) -> list[str]:
    """Build deeper region page guide copy."""
    category_names = _list_text([c.name_en.lower() for c in categories_in_region[:5]], "multiple tea styles")
    tea_names = _list_text([tea.name_en for tea in teas[:5]], "the teas listed below")
    child_names = _list_text([child.name_en for child in child_regions[:5]], "")

    paragraphs = [
        (
            f"{region.name_en} is useful to study as a tea region because it connects place to cup character. "
            f"{region.terroir_notes or 'Its local climate, soils, elevations, and processing traditions shape how finished teas taste.'} "
            f"The teas here are not interchangeable examples of Chinese tea; they are local expressions of {category_names}."
        ),
        (
            f"The most relevant teas on this page include {tea_names}. Read them together rather than one by one: compare aroma first, then body, then aftertaste. "
            f"That pattern shows whether the region tends toward fragrance, roast, freshness, minerality, sweetness, or aged depth."
        ),
        (
            f"Regional pages are also buying guides. A named origin can signal climate, processing tradition, and expected price range, but it should not be treated as a guarantee by itself. "
            f"When evaluating tea from {region.name_en}, look for a seller who can connect the tea to a specific style, harvest, and production area rather than only using the broad regional name."
        ),
        (
            f"Brewing is where regional character becomes practical. If teas from {region.name_en} taste flat, reduce steep time before changing leaf quantity; if they taste thin, increase leaf ratio before pushing temperature. "
            f"This keeps the tea's local aroma intact while giving enough extraction to judge texture and finish."
        ),
        (
            f"When comparing {region.name_en} with another origin, do not start with which region is \"better.\" Start with what the region tends to make easy: fragrance, sweetness, roast depth, aging potential, freshness, or texture. "
            f"That framing makes the page more useful because it turns regional reputation into tasting questions you can actually verify in a cup."
        ),
        (
            f"For storage and repeat buying, keep notes on vendor, harvest year, leaf grade, and brewing response. Regional names can stay the same while lots vary widely, so a simple tasting log helps separate a reliable {region.name_en} tea from a merely recognizable name."
        ),
    ]
    if child_names:
        paragraphs.append(
            f"Within the broader region, sub-areas such as {child_names} matter because Chinese tea naming is often very local. "
            f"A county, mountain, village, or protected origin can change both quality expectations and price, even when the broad category label stays the same."
        )
    else:
        paragraphs.append(
            f"This page currently treats {region.name_en} as a single origin. As the database grows, adding county, mountain, or village-level pages will make the regional map more precise and help separate broad reputation from specific tea character."
        )
    if not teas:
        paragraphs.append(
            f"This page currently has no specific tea records attached to {region.name_en}. It is still useful as a regional hub, but it should be expanded with representative teas before being treated as a complete guide."
        )
    return paragraphs


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
        "tea_analysis": _build_tea_analysis(tea, category, region, province),
        "cross_links": cross_links,
        "parent_links": parent_links,
        "page_title": f"{tea.name_en} ({tea.name_zh or 'Chinese Tea'}) | Taste, Brew & Buying Guide",
        "meta_description": f"Discover {tea.name_en}, a {category.name_en.lower()} from {region.name_en if region else 'China'}. {tea.description_brief[:120]}",
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
        "comparison_analysis": _build_comparison_analysis(
            tea_a, tea_b, category_a, category_b, region_a, region_b
        ),
        "related_comparisons": related_comparisons,
        "cross_links": cross_links,
        "parent_links": parent_links,
        "page_title": f"{tea_a.name_en} vs {tea_b.name_en}: Which Chinese Tea Wins?",
        "meta_description": f"{tea_a.name_en} or {tea_b.name_en}? Compare flavor, brewing, caffeine, body, and price to choose the right Chinese tea for you.",
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
        "category_guide": _build_category_guide(category, teas, regions),
        "page_title": f"{category.name_en} ({category.name_zh or '中国茶'}) | Complete Guide & Best Teas",
        "meta_description": f"Explore {category.name_en} ({category.name_zh}): famous varieties, brewing guides, flavor profiles, and top-rated teas from China.",
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
        "region_guide": _build_region_guide(region, teas, child_regions, categories_in_region),
        "page_title": f"{region.name_en} Tea Region ({region.name_zh or '中国'}) | Varieties & Terroir",
        "meta_description": f"Explore teas from {region.name_en} ({region.name_zh}). {region.terroir_notes[:130] if region.terroir_notes else 'Discover famous Chinese teas, flavor profiles, and brewing guides from this region.'}",
        "canonical_url": f"https://chinatea.house/region/{region.id}/",
        "breadcrumbs": [
            {"label": "Regions", "url": "/region/"},
            {"label": region.name_en, "url": None},
        ],
    }


def create_home_context(
    categories,
    regions,
    teas,
    comparison_count: int,
    occasions=None,
) -> dict[str, Any]:
    """Create template context for the homepage."""
    featured_teas = sorted(teas, key=lambda tea: (tea.tier, tea.name_en))[:8]
    featured_regions = [
        region for region in regions
        if region.parent_id is not None and region.terroir_notes
    ][:8]
    teas_by_category = {}
    for tea in teas:
        teas_by_category.setdefault(tea.category_id, []).append(tea)

    return {
        "categories": categories,
        "regions": regions,
        "teas_by_category": teas_by_category,
        "featured_regions": featured_regions,
        "featured_teas": featured_teas,
        "occasions": occasions or [],
        "tea_count": len(teas),
        "category_count": len(categories),
        "region_count": len(regions),
        "comparison_count": comparison_count,
        "page_title": "Chinese Tea Guide | Types, Regions, Brewing & Comparisons",
        "meta_description": f"Explore {len(teas)} Chinese teas by category, region, and flavor. Compare teas side-by-side, find brewing guides, and discover the best Chinese tea for you.",
        "canonical_url": "https://chinatea.house/",
        "breadcrumbs": [],
    }


def create_region_index_context(
    provinces,
    all_regions,
    regions_by_province,
    teas_by_region,
) -> dict[str, Any]:
    """Create template context for region index page."""
    return {
        "provinces": provinces,
        "all_regions": all_regions,
        "regions_by_province": regions_by_province,
        "teas_by_region": teas_by_region,
        "page_title": "Chinese Tea Regions | Map of Origins, Provinces & Terroir",
        "meta_description": "Explore Chinese tea regions from Fujian and Yunnan to Zhejiang and Taiwan. Discover famous teas, terroir, and regional flavor profiles.",
        "canonical_url": "https://chinatea.house/region/",
        "breadcrumbs": [
            {"label": "Regions", "url": None},
        ],
    }


def create_category_index_context(
    categories,
    teas_by_category,
) -> dict[str, Any]:
    """Create template context for category index page."""
    return {
        "categories": categories,
        "teas_by_category": teas_by_category,
        "page_title": "Chinese Tea Types | Green, Oolong, Pu'er, Black, White & More",
        "meta_description": "Learn the 8 main types of Chinese tea. Compare green, oolong, pu'er, black, white, yellow, dark, and scented teas by flavor and brewing.",
        "canonical_url": "https://chinatea.house/category/",
        "breadcrumbs": [
            {"label": "Categories", "url": None},
        ],
    }


def _tea_matches_occasion(tea, occasion) -> bool:
    """Check if a tea matches an occasion's preferred categories and attributes."""
    # Preferred categories
    if occasion.preferred_categories and tea.category_id not in occasion.preferred_categories:
        return False

    # Preferred attributes
    for attr, values in occasion.preferred_attributes.items():
        if attr == "caffeine_level":
            if tea.caffeine_level.value not in values:
                return False
        elif attr == "body":
            if tea.body.value not in values:
                return False
        elif attr == "tier":
            if tea.tier not in values:
                return False
        elif attr == "roast_level":
            if not tea.roast_level or tea.roast_level.value not in values:
                return False

    return True


def create_occasion_context(
    occasion,
    all_teas,
) -> dict[str, Any]:
    """Create template context for best-tea-for occasion page."""
    recommended = [t for t in all_teas if _tea_matches_occasion(t, occasion)]
    # Sort by tier (best first) then name
    recommended = sorted(recommended, key=lambda t: (t.tier, t.name_en))

    top_picks = recommended[:8]
    alternatives = recommended[8:16]

    return {
        "occasion": occasion,
        "recommended_teas": top_picks,
        "alternative_teas": alternatives,
        "page_title": f"Best Tea for {occasion.name} | China Tea House Recommendations",
        "meta_description": f"Find the best Chinese tea for {occasion.name.lower()}. Our curated picks include {len(top_picks)} teas matched by flavor, caffeine, body, and brewing style.",
        "canonical_url": f"https://chinatea.house/best-tea-for/{occasion.id}/",
        "breadcrumbs": [
            {"label": "Best Tea For", "url": "/best-tea-for/"},
            {"label": occasion.name, "url": None},
        ],
    }
